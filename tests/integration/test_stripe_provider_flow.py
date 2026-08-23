"""Integration tests for Stripe Provider flow and DB constraints."""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from testcontainers.postgres import PostgresContainer  # type: ignore

from api_guardian.application.use_cases.sync_provider import SyncProviderUseCase
from api_guardian.domain import ProviderChange
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.base import Base
from api_guardian.persistence.repositories.maintenance_case_repo import SQLMaintenanceCaseRepository
from api_guardian.persistence.repositories.provider_change_repo import SQLProviderChangeRepository
from api_guardian.persistence.repositories.raw_artifact_repo import SQLRawArtifactRepository
from api_guardian.providers.base import AcquiredSource
from api_guardian.providers.stripe.adapter import StripeOpenAPIAdapter
from api_guardian.workers.tasks.provider import S3ArtifactStorage


@pytest.fixture(scope="module")
def db_engine():
    with PostgresContainer("postgres:15") as postgres:
        url = postgres.get_connection_url().replace("+psycopg2", "")
        db_manager = DatabaseManager(url)
        Base.metadata.create_all(db_manager.engine)
        yield db_manager


class LocalArtifactStorage(S3ArtifactStorage):
    def __init__(self):
        self.store = {}
    
    def store_artifact(self, key: str, content: bytes) -> str:
        self.store[key] = content
        return key

    def retrieve_artifact(self, key: str) -> bytes:
        return self.store[key]


def test_full_pipeline_and_idempotency(db_engine):
    raw_repo = SQLRawArtifactRepository(db_engine)
    prov_repo = SQLProviderChangeRepository(db_engine)
    case_repo = SQLMaintenanceCaseRepository(db_engine)
    storage = LocalArtifactStorage()
    
    baseline_content = b'{"openapi": "3.0.0", "paths": {"/a": {"get": {}}}}'
    changed_content = b'{"openapi": "3.0.0", "paths": {}}'
    
    class MockAdapterBaseline(StripeOpenAPIAdapter):
        def acquire_source(self):
            return AcquiredSource(
                content=baseline_content,
                source_url="http://test",
                content_type="application/json",
                source_key="openapi/spec3",
                source_revision="v1"
            )
            
    # 1. First sync (Baseline)
    use_case = SyncProviderUseCase(
        provider_adapter=MockAdapterBaseline(),
        raw_artifact_repo=raw_repo,
        provider_repo=prov_repo,
        case_repo=case_repo,
        artifact_storage=storage
    )
    use_case.execute()
    
    # 2. Second sync (Same baseline - Idempotent, should be no-op)
    use_case.execute()
    
    # 3. Changed sync
    class MockAdapterChanged(StripeOpenAPIAdapter):
        def acquire_source(self):
            return AcquiredSource(
                content=changed_content,
                source_url="http://test",
                content_type="application/json",
                source_key="openapi/spec3",
                source_revision="v2"
            )
            
    use_case = SyncProviderUseCase(
        provider_adapter=MockAdapterChanged(),
        raw_artifact_repo=raw_repo,
        provider_repo=prov_repo,
        case_repo=case_repo,
        artifact_storage=storage
    )
    use_case.execute()
    
    # Verify DB state
    with db_engine.SessionLocal() as session:
        from sqlalchemy import select

        from api_guardian.persistence.models.tables import (
            ProviderChangeModel,
            ProviderChangeRevisionModel,
            RawArtifactModel,
        )
        
        # 2 artifacts should exist
        artifacts = session.execute(select(RawArtifactModel)).scalars().all()
        assert len(artifacts) == 2
        
        # 1 change detected (/a removed)
        changes = session.execute(select(ProviderChangeModel)).scalars().all()
        assert len(changes) == 1
        change = changes[0]
        assert change.revision == 1
        
        # We can also test revision update by executing sync again with a slightly different source but same logical change
        # Let's say we change title but same endpoint removed
        
    changed_content_v3 = b'{"openapi": "3.0.0", "info": {"title": "New"}, "paths": {}}'
    class MockAdapterChangedV3(StripeOpenAPIAdapter):
        def acquire_source(self):
            return AcquiredSource(
                content=changed_content_v3,
                source_url="http://test",
                content_type="application/json",
                source_key="openapi/spec3",
                source_revision="v3"
            )
            
        def detect_changes(self, current_spec, previous_spec, current_artifact_id, previous_artifact_id):
            # Force the detector to return the same change so we trigger the revision update logic
            import uuid

            from api_guardian.domain import CandidateChange, EvidenceSource
            return [
                CandidateChange(
                    id=uuid.uuid4(),
                    raw_artifact_id=current_artifact_id,
                    previous_artifact_id=previous_artifact_id,
                    provider="stripe",
                    change_type="endpoint_removed",
                    target_entity="/a",
                    extracted_summary="Mocked",
                    evidence_source=EvidenceSource.OBSERVED_SCHEMA_CHANGE,
                    evidence={}
                )
            ]
            
    use_case = SyncProviderUseCase(
        provider_adapter=MockAdapterChangedV3(),
        raw_artifact_repo=raw_repo,
        provider_repo=prov_repo,
        case_repo=case_repo,
        artifact_storage=storage
    )
    use_case.execute()
    
    # Verify revision was updated
    with db_engine.SessionLocal() as session:
        from api_guardian.persistence.models.tables import (
            ProviderChangeModel,
            ProviderChangeRevisionModel,
        )
        changes = session.execute(select(ProviderChangeModel)).scalars().all()
        assert len(changes) == 1
        assert changes[0].revision == 2
        
        revisions = session.execute(select(ProviderChangeRevisionModel)).scalars().all()
        assert len(revisions) == 1
        assert revisions[0].revision_number == 2


def test_atomic_revision_rollback(db_engine):
    """Test that if revision history insert fails, canonical update rolls back."""
    prov_repo = SQLProviderChangeRepository(db_engine)
    
    # Create base change
    from api_guardian.domain import ChangeClassification
    change = ProviderChange(
        id=uuid.uuid4(),
        provider="test",
        provider_native_id="test_id_123",
        classification=ChangeClassification.DEPRECATION,
        summary="Test",
        affected_entities=[],
        effective_date=None,
        sunset_date=None,
        source_artifact_hash="hash1",
        revision=1
    )
    saved_change = prov_repo.save(change)
    
    saved_change.source_artifact_hash = "hash2"
    
    # Try to save revision but mock the insert to fail
        
    with db_engine.SessionLocal() as session:
        from api_guardian.persistence.models.tables import ProviderChangeRevisionModel
        # Insert conflicting revision 2
        conflict = ProviderChangeRevisionModel(
            id=uuid.uuid4(),
            provider_change_id=saved_change.id,
            revision_number=2,
            source_artifact_hash="conflict_hash",
            evidence={},
            classification="deprecation",
            summary="Test",
            evidence_source="test_source"
        )
        session.add(conflict)
        session.commit()
        
    # Now when we call save_revision, it will increment canonical to 2, but insert will fail due to UC
    with pytest.raises(IntegrityError):
        prov_repo.save_revision(saved_change, {}, "test_source")
        
    # Verify rollback: canonical revision should still be 1 (because the update rolled back)
    with db_engine.SessionLocal() as session:
        from sqlalchemy import select

        from api_guardian.persistence.models.tables import ProviderChangeModel
        db_change = session.execute(select(ProviderChangeModel).where(ProviderChangeModel.id == saved_change.id)).scalar_one()
        assert db_change.revision == 1
        assert db_change.source_artifact_hash == "hash1" # NOT hash2
