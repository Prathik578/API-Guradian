"""Concrete implementation of MaintenanceCaseRepository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from api_guardian.application.interfaces import MaintenanceCaseRepository
from api_guardian.domain import MaintenanceCase, TenantContext
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import MaintenanceCaseModel


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
                updated_at=model.updated_at,
            )

    def save(self, ctx: TenantContext, case: MaintenanceCase) -> MaintenanceCase:
        
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(MaintenanceCaseModel, case.id)
            if not model:
                model = MaintenanceCaseModel(
                    id=case.id,
                    organization_id=case.organization_id,
                    repository_id=case.repository_id,
                    provider_change_id=case.provider_change_id,
                    base_revision_sha=case.base_revision_sha,
                )
                model.state = case.state
                session.add(model)
                try:
                    session.flush() # flush to catch IntegrityError before context manager commit
                except IntegrityError:
                    session.rollback()
                    # It already exists, fetch it by unique constraint
                    # We must reset the tenant context because we rolled back!
                    # Actually, get_tenant_session sets the local variable. Rolling back clears LOCAL settings in Postgres!
                    # So we must reset it.
                    session.execute(
                        text("SET LOCAL app.current_tenant_id = :tenant_id"),
                        {"tenant_id": str(ctx.tenant_id)},
                    )
                    stmt = select(MaintenanceCaseModel).where(
                        MaintenanceCaseModel.repository_id == case.repository_id,
                        MaintenanceCaseModel.provider_change_id == case.provider_change_id,
                        MaintenanceCaseModel.base_revision_sha == case.base_revision_sha
                    )
                    existing_model = session.execute(stmt).scalar_one()
                    
                    return MaintenanceCase(
                        id=existing_model.id,
                        organization_id=existing_model.organization_id,
                        repository_id=existing_model.repository_id,
                        provider_change_id=existing_model.provider_change_id,
                        base_revision_sha=existing_model.base_revision_sha,
                        state=existing_model.state,
                        created_at=existing_model.created_at,
                        updated_at=existing_model.updated_at,
                    )
            else:
                model.state = case.state
                
            return case

    def list_active_cases(
        self, ctx: TenantContext, repository_id: uuid.UUID
    ) -> Sequence[MaintenanceCase]:
        # TODO: Implement active cases listing
        return []
