"""Concrete implementation of MaintenanceCaseRepository."""
import uuid
from typing import Sequence
from sqlalchemy import select

from api_guardian.domain import MaintenanceCase, TenantContext
from api_guardian.application.interfaces import MaintenanceCaseRepository
from api_guardian.persistence.models.tables import MaintenanceCaseModel
from api_guardian.persistence.database import DatabaseManager


class SQLMaintenanceCaseRepository(MaintenanceCaseRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_by_id(self, ctx: TenantContext, case_id: uuid.UUID) -> MaintenanceCase | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(MaintenanceCaseModel, case_id)
            if not model:
                return None
            return MaintenanceCase(
                id=model.id,
                organization_id=model.organization_id,
                repository_id=model.repository_id,
                provider_change_id=model.provider_change_id,
                base_revision_sha=model.base_revision_sha,
                state=model.state,
                created_at=model.created_at,
                updated_at=model.updated_at
            )

    def save(self, ctx: TenantContext, case: MaintenanceCase) -> None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(MaintenanceCaseModel, case.id)
            if not model:
                model = MaintenanceCaseModel(
                    id=case.id,
                    organization_id=case.organization_id,
                    repository_id=case.repository_id,
                    provider_change_id=case.provider_change_id,
                    base_revision_sha=case.base_revision_sha
                )
                session.add(model)
            model.state = case.state
            # session commit is handled by context manager

    def list_active_cases(self, ctx: TenantContext, repository_id: uuid.UUID) -> Sequence[MaintenanceCase]:
        # TODO: Implement active cases listing
        return []
