"""Concrete implementation of RawArtifactRepository."""

import uuid

from sqlalchemy import select

from api_guardian.application.interfaces import RawArtifactRepository
from api_guardian.domain import RawArtifact
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import RawArtifactModel


class SQLRawArtifactRepository(RawArtifactRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_by_content_hash(
        self, provider: str, source_key: str, content_hash: str
    ) -> RawArtifact | None:
        with self.db_manager.SessionLocal() as session:
            stmt = select(RawArtifactModel).where(
                RawArtifactModel.provider == provider,
                RawArtifactModel.source_key == source_key,
                RawArtifactModel.content_hash == content_hash,
            )
            model = session.execute(stmt).scalar_one_or_none()
            if not model:
                return None
            return RawArtifact(
                id=model.id,
                provider=model.provider,
                source_key=model.source_key,
                content_hash=model.content_hash,
                source_url=model.source_url,
                source_revision=model.source_revision,
                content_type=model.content_type,
                storage_ref=model.storage_ref,
                fetched_at=model.fetched_at, # Note: this is a string in DB model, usually we parse it. For MVP, we might keep it simple or parse.
            )

    def get_latest_by_source(
        self, provider: str, source_key: str, exclude_id: uuid.UUID | None = None
    ) -> RawArtifact | None:
        with self.db_manager.SessionLocal() as session:
            stmt = (
                select(RawArtifactModel)
                .where(
                    RawArtifactModel.provider == provider,
                    RawArtifactModel.source_key == source_key,
                )
                .order_by(RawArtifactModel.fetched_at.desc())
            )
            if exclude_id:
                stmt = stmt.where(RawArtifactModel.id != exclude_id)
                
            model = session.execute(stmt.limit(1)).scalar_one_or_none()
            if not model:
                return None
                
            return RawArtifact(
                id=model.id,
                provider=model.provider,
                source_key=model.source_key,
                content_hash=model.content_hash,
                source_url=model.source_url,
                source_revision=model.source_revision,
                content_type=model.content_type,
                storage_ref=model.storage_ref,
                fetched_at=model.fetched_at,
            )

    def save(self, artifact: RawArtifact) -> RawArtifact:
        from sqlalchemy.exc import IntegrityError
        
        with self.db_manager.SessionLocal() as session:
            model = session.get(RawArtifactModel, artifact.id)
            if not model:
                model = RawArtifactModel(
                    id=artifact.id,
                    provider=artifact.provider,
                    source_key=artifact.source_key,
                    content_hash=artifact.content_hash,
                    source_url=artifact.source_url,
                    source_revision=artifact.source_revision,
                    content_type=artifact.content_type,
                    storage_ref=artifact.storage_ref,
                    fetched_at=str(artifact.fetched_at),
                )
                session.add(model)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    # Exists by unique constraint (provider, source_key, content_hash)
                    stmt = select(RawArtifactModel).where(
                        RawArtifactModel.provider == artifact.provider,
                        RawArtifactModel.source_key == artifact.source_key,
                        RawArtifactModel.content_hash == artifact.content_hash,
                    )
                    existing = session.execute(stmt).scalar_one()
                    artifact.id = existing.id
            return artifact
