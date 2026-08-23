import threading
import uuid

import pytest

from api_guardian.domain import (
    ChangeClassification,
    MaintenanceCase,
    MaintenanceCaseState,
    ProviderChange,
    TenantContext,
)
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.base import Base
from api_guardian.persistence.repositories.maintenance_case_repo import SQLMaintenanceCaseRepository
from api_guardian.persistence.repositories.provider_change_repo import SQLProviderChangeRepository

try:
    from testcontainers.postgres import PostgresContainer  # type: ignore
    HAS_TESTCONTAINERS = True
except ImportError:
    HAS_TESTCONTAINERS = False

@pytest.fixture(scope="module")
def postgres_db():
    if not HAS_TESTCONTAINERS:
        pytest.skip("Testcontainers not available")
        
    with PostgresContainer("postgres:15-alpine") as postgres:
        db_url = postgres.get_connection_url().replace("+psycopg2", "")
        # pool_size must be larger than the number of concurrent threads
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        db_manager = DatabaseManager(db_url)
        db_manager.engine = create_engine(db_url, pool_size=10, max_overflow=20)
        db_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
        
        Base.metadata.create_all(db_manager.engine)
        yield db_manager

@pytest.mark.skipif(not HAS_TESTCONTAINERS, reason="Requires testcontainers-python")
def test_concurrent_idempotent_creation(postgres_db):
    """Proves that multiple threads attempting to create the same case don't duplicate it."""
    tenant_id = uuid.uuid4()
    ctx = TenantContext(tenant_id=tenant_id)
    
    repo_id = uuid.uuid4()
    provider_native_id = "concurrent_event_123"

    # Insert a repository first to avoid ForeignKeyViolation
    from api_guardian.persistence.models.tables import RepositoryModel
    with postgres_db.get_tenant_session(ctx) as session:
        session.add(RepositoryModel(
            id=repo_id,
            organization_id=tenant_id,
            name="Concurrent Repo",
            github_full_name="org/concurrent-repo"
        ))
        session.commit()

    def worker(results_list, index):
        try:
            # We use a separate repository instance per thread, mimicking Celery workers
            provider_repo = SQLProviderChangeRepository(postgres_db)
            case_repo = SQLMaintenanceCaseRepository(postgres_db)
            
            change = ProviderChange(
                id=uuid.uuid4(),
                provider="Stripe",
                provider_native_id=provider_native_id,
                classification=ChangeClassification.UNKNOWN,
                summary="Concurrent test",
                affected_entities=[],
                effective_date=None,
                sunset_date=None,
            )
            change = provider_repo.save(change)
            
            case = MaintenanceCase(
                id=uuid.uuid4(),
                organization_id=tenant_id,
                repository_id=repo_id,
                provider_change_id=change.id,
                base_revision_sha="abc",
                state=MaintenanceCaseState.DISCOVERED
            )
            case = case_repo.save(ctx, case)
            results_list[index] = {"change_id": change.id, "case_id": case.id}
        except Exception as e:  # noqa: BLE001
            import traceback
            results_list[index] = {"error": str(e), "traceback": traceback.format_exc()}

    # Run 5 threads concurrently
    threads: list[threading.Thread] = []
    results: list[dict[str, object]] = [{} for _ in range(5)]
    for i in range(5):
        t = threading.Thread(target=worker, args=(results, i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    # Verify results
    successful_cases: set[object] = set()
    successful_changes: set[object] = set()
    for res in results:
        assert "error" not in res, (
            f"Thread failed: {res.get('error')}\n{res.get('traceback', '')}"
        )
        successful_changes.add(res["change_id"])
        successful_cases.add(res["case_id"])
        
    # Due to idempotency, all threads should have received the EXACT SAME case ID and change ID
    assert len(successful_changes) == 1
    assert len(successful_cases) == 1
