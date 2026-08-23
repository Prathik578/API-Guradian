"""Celery tasks for migration."""

import uuid
from typing import Any

from api_guardian.application.use_cases.generate_migration import GenerateMigrationUseCase
from api_guardian.domain import TenantContext
from api_guardian.reasoning.patch_generator import PatchGenerator
from api_guardian.workers.celery_app import app


class MockLLMGateway:
    """Mock LLM Gateway for MVP task instantiation."""

    def generate_completion(self, *args: Any, **kwargs: Any) -> tuple[str, int, int]:
        return "```diff\n--- a\n+++ b\n```", 0, 0

    def generate_structured(self, *args: Any, **kwargs: Any) -> tuple[dict[str, Any], int, int]:
        return {}, 0, 0


import logging

from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def generate_migration_task(self: Any, tenant_id: str, case_id: str) -> None:
    from api_guardian.domain import MaintenanceCaseState
    from api_guardian.persistence.database import db_manager
    from api_guardian.persistence.repositories.maintenance_case_repo import (
        SQLMaintenanceCaseRepository,
    )
    from api_guardian.persistence.repositories.migration_repo import SQLMigrationRepository

    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    logger.info("Starting generate_migration_task", extra={"tenant_id": tenant_id, "case_id": case_id, "attempt": self.request.retries})

    try:
        case_repo = SQLMaintenanceCaseRepository(db_manager)
        
        # State-aware idempotency check
        case = case_repo.get_by_id(ctx, uuid.UUID(case_id))
        if case and case.state != MaintenanceCaseState.AFFECTED_ACTION_REQUIRED:
            logger.info("Case already past AFFECTED_ACTION_REQUIRED state, exiting harmlessly.")
            return

        migration_repo = SQLMigrationRepository(db_manager)
        
        # We still use a Mock LLM for the pipeline to be deterministic in MVP
        patch_generator = PatchGenerator(llm_gateway=MockLLMGateway())  # type: ignore

        use_case = GenerateMigrationUseCase(
            case_repo=case_repo,
            migration_repo=migration_repo,
            patch_generator=patch_generator,
        )
        use_case.execute(ctx, uuid.UUID(case_id))
    except OperationalError as e:
        logger.warning(f"Transient DB error in generate_migration_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed generate_migration_task: {e}")
        raise
