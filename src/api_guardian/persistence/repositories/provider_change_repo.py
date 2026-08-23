"""Concrete implementation of ProviderChangeRepository."""
import uuid
from typing import Any

from api_guardian.application.interfaces import ProviderChangeRepository
from api_guardian.domain import ChangeClassification, ProviderChange
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import ProviderChangeModel, ProviderChangeRevisionModel


class SQLProviderChangeRepository(ProviderChangeRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_by_id(self, change_id: uuid.UUID) -> ProviderChange | None:
        # Note: ProviderChanges do not use TenantContext because they are global
        # but they still need a generic DB session. We can use a context manager directly from SessionLocal
        with self.db_manager.SessionLocal() as session:
            model = session.get(ProviderChangeModel, change_id)
            if not model:
                return None
            return ProviderChange(
                id=model.id,
                provider=model.provider,
                provider_native_id=model.provider_native_id,
                classification=ChangeClassification(model.classification),
                summary=model.summary,
                affected_entities=model.affected_entities,
                effective_date=model.effective_date,
                sunset_date=model.sunset_date,
                source_artifact_hash=model.source_artifact_hash,
                revision=model.revision,
            )

    def get_by_native_id(self, provider: str, provider_native_id: str) -> ProviderChange | None:
        from sqlalchemy import select
        with self.db_manager.SessionLocal() as session:
            stmt = select(ProviderChangeModel).where(
                ProviderChangeModel.provider == provider,
                ProviderChangeModel.provider_native_id == provider_native_id
            )
            model = session.execute(stmt).scalar_one_or_none()
            if not model:
                return None
            return ProviderChange(
                id=model.id,
                provider=model.provider,
                provider_native_id=model.provider_native_id,
                classification=ChangeClassification(model.classification),
                summary=model.summary,
                affected_entities=model.affected_entities,
                effective_date=model.effective_date,
                sunset_date=model.sunset_date,
                source_artifact_hash=model.source_artifact_hash,
                revision=model.revision,
            )

    def save(self, change: ProviderChange) -> ProviderChange:
        from sqlalchemy import select
        from sqlalchemy.exc import IntegrityError
        
        with self.db_manager.SessionLocal() as session:
            model = session.get(ProviderChangeModel, change.id)
            if not model:
                model = ProviderChangeModel(
                    id=change.id,
                    provider=change.provider,
                    provider_native_id=change.provider_native_id,
                )
                model.classification = change.classification.value
                model.summary = change.summary
                model.affected_entities = change.affected_entities
                model.effective_date = change.effective_date
                model.sunset_date = change.sunset_date
                model.source_artifact_hash = change.source_artifact_hash
                model.revision = change.revision
                session.add(model)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    # It already exists, fetch it by unique constraint
                    stmt = select(ProviderChangeModel).where(
                        ProviderChangeModel.provider == change.provider,
                        ProviderChangeModel.provider_native_id == change.provider_native_id
                    )
                    existing_model = session.execute(stmt).scalar_one()
                    
                    return ProviderChange(
                        id=existing_model.id,
                        provider=existing_model.provider,
                        provider_native_id=existing_model.provider_native_id,
                        classification=ChangeClassification(existing_model.classification),
                        summary=existing_model.summary,
                        affected_entities=existing_model.affected_entities,
                        effective_date=existing_model.effective_date,
                        sunset_date=existing_model.sunset_date,
                        source_artifact_hash=existing_model.source_artifact_hash,
                        revision=existing_model.revision,
                    )
            else:
                model.classification = change.classification.value
                model.summary = change.summary
                model.affected_entities = change.affected_entities
                model.effective_date = change.effective_date
                model.sunset_date = change.sunset_date
                # DO NOT UPDATE revision or source_artifact_hash here, save_revision does that
                session.commit()
                
            return change

    def save_revision(
        self,
        change: ProviderChange,
        evidence: dict[str, Any],
        evidence_source: str
    ) -> ProviderChange:
        import uuid

        from sqlalchemy import text, update
        
        with self.db_manager.SessionLocal() as session:
            # 1. Atomic Update Returning
            stmt = (
                update(ProviderChangeModel)
                .where(ProviderChangeModel.id == change.id)
                .values(
                    revision=ProviderChangeModel.revision + 1,
                    source_artifact_hash=change.source_artifact_hash,
                    updated_at=text("now()")
                )
                .returning(ProviderChangeModel.revision)
            )
            
            new_revision_num = session.execute(stmt).scalar_one()
            
            # 2. Insert Revision Record
            rev_model = ProviderChangeRevisionModel(
                id=uuid.uuid4(),
                provider_change_id=change.id,
                revision_number=new_revision_num,
                source_artifact_hash=change.source_artifact_hash,
                evidence=evidence,
                classification=change.classification.value,
                summary=change.summary,
                evidence_source=evidence_source
            )
            session.add(rev_model)
            
            # 3. Commit Transaction
            # If the insert fails (e.g., due to UC on revision_number),
            # the update rolls back atomically.
            session.commit()
            
            # Update the domain object and return
            change.revision = new_revision_num
            return change
