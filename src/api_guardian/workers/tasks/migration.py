"""Celery tasks for migration."""

import uuid
from typing import Any

from api_guardian.application.use_cases.generate_migration import GenerateMigrationUseCase
from api_guardian.domain import TenantContext
from api_guardian.reasoning.patch_generator import PatchGenerator
from api_guardian.workers.celery_app import app





import logging

from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def generate_migration_task(self: Any, tenant_id: str, case_id: str) -> None:
    from api_guardian.domain import MaintenanceCaseState
    from api_guardian.persistence.database import db_manager
    from api_guardian.persistence.outbox import OutboxManager
    from api_guardian.persistence.repositories.impact_assessment_repo import (
        SQLImpactAssessmentRepository,
    )
    from api_guardian.persistence.repositories.maintenance_case_repo import (
        SQLMaintenanceCaseRepository,
    )
    from api_guardian.persistence.repositories.migration_repo import SQLMigrationRepository
    from api_guardian.persistence.repositories.provider_change_repo import (
        SQLProviderChangeRepository,
    )
    from api_guardian.persistence.repositories.snapshot_repo import SQLSnapshotRepository
    from api_guardian.platform.storage.local_storage import LocalArtifactStorage

    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    logger.info("Starting generate_migration_task", extra={"tenant_id": tenant_id, "case_id": case_id, "attempt": self.request.retries})

    try:
        case_repo = SQLMaintenanceCaseRepository(db_manager)
        
        # State-aware idempotency check
        case = case_repo.get_by_id(ctx, uuid.UUID(case_id))
        if not case:
            return
        if case.state != MaintenanceCaseState.AFFECTED_ACTION_REQUIRED:
            logger.info("Case already past AFFECTED_ACTION_REQUIRED state, exiting harmlessly.")
            return

        migration_repo = SQLMigrationRepository(db_manager)
        change_repo = SQLProviderChangeRepository(db_manager)
        assessment_repo = SQLImpactAssessmentRepository(db_manager)
        
        # Use Resilient LLM Gateway with actual implementation
        from api_guardian.platform.llm.resilient_gateway import ResilientLLMGateway
        from api_guardian.platform.llm.openai_gateway import OpenAIGateway, LLMConfigurationError
        
        try:
            underlying_llm = OpenAIGateway()
        except LLMConfigurationError as e:
            logger.error(f"Migration generation blocked: {e}")
            case.transition_to(MaintenanceCaseState.HUMAN_INTERVENTION_REQUIRED)
            case_repo.save(ctx, case)
            return
            
        llm = ResilientLLMGateway(underlying=underlying_llm)
        patch_generator = PatchGenerator(llm_gateway=llm)

        snapshot_repo = SQLSnapshotRepository(db_manager)
        
        from api_guardian.application.interfaces.storage import ArtifactStoragePort
        artifact_storage: ArtifactStoragePort

        import os
        s3_bucket = os.environ.get("S3_BUCKET")
        if s3_bucket:
            from api_guardian.platform.storage.s3_storage import S3ArtifactStorage
            artifact_storage = S3ArtifactStorage(bucket_name=s3_bucket)
        else:
            artifact_storage = LocalArtifactStorage()

        use_case = GenerateMigrationUseCase(
            case_repo=case_repo,
            migration_repo=migration_repo,
            change_repo=change_repo,
            assessment_repo=assessment_repo,
            snapshot_repo=snapshot_repo,
            patch_generator=patch_generator,
            artifact_storage=artifact_storage,
        )
        use_case.execute(ctx, uuid.UUID(case_id))
        
        with db_manager.get_tenant_session(ctx) as session:
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.orchestrator.orchestrate_case_task",
                {"tenant_id": tenant_id, "case_id": case_id}
            )
    except OperationalError as e:
        logger.warning(f"Transient DB error in generate_migration_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed generate_migration_task: {e}")
        raise
