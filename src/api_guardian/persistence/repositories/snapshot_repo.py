"""Concrete implementation of SnapshotRepository."""

import uuid

from api_guardian.application.interfaces import SnapshotRepository
from api_guardian.domain import RepositoryRevision, RepositorySnapshot, TenantContext
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import SnapshotModel


class SQLSnapshotRepository(SnapshotRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_by_id(self, ctx: TenantContext, snapshot_id: uuid.UUID) -> RepositorySnapshot | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(SnapshotModel, snapshot_id)
            if not model:
                return None
            return RepositorySnapshot(
                id=model.id,
                revision=RepositoryRevision(
                    repository_id=model.repository_id,
                    branch=model.branch,
                    commit_sha=model.commit_sha,
                ),
                archive_content_hash=model.archive_content_hash,
                code_model_version=model.code_model_version,
                dependency_graph=dict(model.dependency_graph) if model.dependency_graph else {},
            )

    def save(self, ctx: TenantContext, snapshot: RepositorySnapshot) -> None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(SnapshotModel, snapshot.id)
            if not model:
                model = SnapshotModel(
                    id=snapshot.id,
                    organization_id=ctx.tenant_id,
                    repository_id=snapshot.revision.repository_id,
                    branch=snapshot.revision.branch,
                    commit_sha=snapshot.revision.commit_sha,
                )
                session.add(model)
            model.archive_content_hash = snapshot.archive_content_hash
            model.code_model_version = snapshot.code_model_version
            model.dependency_graph = snapshot.dependency_graph or {}
