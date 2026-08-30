"""Celery tasks for verification."""

import logging
import uuid
from typing import Any

from sqlalchemy.exc import OperationalError

from api_guardian.application.use_cases.execute_verification import ExecuteVerificationUseCase
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.outbox import OutboxManager
from api_guardian.platform.sandbox.local_sandbox import LocalSandboxOrchestrator
from api_guardian.workers.celery_app import app

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def execute_verification_task(self: Any, tenant_id: str, case_id: str) -> None:
    from api_guardian.domain import MaintenanceCaseState
    from api_guardian.persistence.repositories.maintenance_case_repo import (
        SQLMaintenanceCaseRepository,
    )
    from api_guardian.persistence.repositories.migration_repo import SQLMigrationRepository
    from api_guardian.persistence.repositories.snapshot_repo import SQLSnapshotRepository
    from api_guardian.persistence.repositories.verification_repo import SQLVerificationRepository
    from api_guardian.platform.storage.local_storage import LocalArtifactStorage

    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    logger.info("Starting execute_verification_task", extra={"tenant_id": tenant_id, "case_id": case_id, "attempt": self.request.retries})

    try:
        case_repo = SQLMaintenanceCaseRepository(db_manager)
        
        # State-aware idempotency check
        case = case_repo.get_by_id(ctx, uuid.UUID(case_id))
        if case and case.state != MaintenanceCaseState.MIGRATING:
            logger.info("Case already past MIGRATING state, exiting harmlessly.")
            return

        verification_repo = SQLVerificationRepository(db_manager)
        migration_repo = SQLMigrationRepository(db_manager)
        snapshot_repo = SQLSnapshotRepository(db_manager)
        artifact_storage = LocalArtifactStorage()

        def use_case_factory() -> ExecuteVerificationUseCase:
            return ExecuteVerificationUseCase(
                verification_repo=verification_repo,
                case_repo=case_repo,
                migration_repo=migration_repo,
                snapshot_repo=snapshot_repo,
                sandbox_orchestrator=LocalSandboxOrchestrator(), # dummy for factory
                artifact_storage=artifact_storage,
            )

        sandbox = LocalSandboxOrchestrator(use_case_factory=use_case_factory)

        use_case = ExecuteVerificationUseCase(
            verification_repo=verification_repo, 
            case_repo=case_repo, 
            migration_repo=migration_repo,
            snapshot_repo=snapshot_repo,
            sandbox_orchestrator=sandbox,
            artifact_storage=artifact_storage,
        )
        use_case.execute(ctx, uuid.UUID(case_id))
        
        # For a truly autonomous loop in testing, we might simulate the webhook callback immediately
        # if the sandbox is mocked. In production, this task ends here, and the webhook handles the rest.
        # However, to let the orchestrator know we transitioned to VERIFYING:
        with db_manager.get_tenant_session(ctx) as session:
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.orchestrator.orchestrate_case_task",
                {"tenant_id": tenant_id, "case_id": case_id}
            )
    except OperationalError as e:
        logger.warning(f"Transient DB error in execute_verification_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed execute_verification_task: {e}")
        raise
