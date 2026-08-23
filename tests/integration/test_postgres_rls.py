import uuid

import pytest
from sqlalchemy import select, text

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.base import Base
from api_guardian.persistence.models.tables import RepositoryModel

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
        # testcontainers uses psycopg2 by default, but we might want psycopg or just let SQLAlchemy handle it
        db_url = postgres.get_connection_url().replace("+psycopg2", "")
        db_manager = DatabaseManager(db_url)
        
        # Create schema
        Base.metadata.create_all(db_manager.engine)
        
        # Enable RLS on repository table
        with db_manager.engine.begin() as conn:
            conn.execute(text("ALTER TABLE repositories ENABLE ROW LEVEL SECURITY;"))
            conn.execute(text(
                "CREATE POLICY tenant_isolation_policy ON repositories "
                "USING (organization_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);"
            ))
            # Force RLS to apply even for the table owner (which SQLAlchemy connects as)
            conn.execute(text("ALTER TABLE repositories FORCE ROW LEVEL SECURITY;"))
            
            # The test user in testcontainers might be a superuser or have BYPASSRLS.
            # We must revoke BYPASSRLS so that RLS is actually enforced.
            conn.execute(text("ALTER ROLE test NOSUPERUSER NOBYPASSRLS;"))
            
        yield db_manager


@pytest.mark.skipif(not HAS_TESTCONTAINERS, reason="Requires testcontainers-python")
def test_postgres_rls_isolation(postgres_db: DatabaseManager):
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    repo_a_id = uuid.uuid4()
    
    ctx_a = TenantContext(tenant_id=tenant_a)
    ctx_b = TenantContext(tenant_id=tenant_b)
    
    # 1. Start a transaction with Tenant A context and insert data
    with postgres_db.get_tenant_session(ctx_a) as session_a:
        repo_a = RepositoryModel(
            id=repo_a_id,
            organization_id=tenant_a,
            name="Repo A",
            github_full_name="org/repo-a",
        )
        session_a.add(repo_a)
        session_a.commit()
        
    # 2. Start a transaction with Tenant A context and confirm access
    with postgres_db.get_tenant_session(ctx_a) as session_a:
        result = session_a.get(RepositoryModel, repo_a_id)
        assert result is not None
        assert result.name == "Repo A"

    # 3. Start a transaction with Tenant B context and confirm no access
    with postgres_db.get_tenant_session(ctx_b) as session_b:
        result = session_b.get(RepositoryModel, repo_a_id)
        assert result is None  # RLS silently hides it

    # 4. Attempt unscoped access
    # Use raw engine to bypass get_tenant_session
    with postgres_db.SessionLocal() as session_unscoped:
        # Since app.current_tenant_id is not set, current_setting('app.current_tenant_id', true) returns NULL.
        # organization_id = NULL is false, so it returns 0 rows.
        stmt = select(RepositoryModel)
        results = session_unscoped.execute(stmt).scalars().all()
        assert len(results) == 0
