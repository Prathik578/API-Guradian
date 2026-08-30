"""Celery tasks for GitHub integration."""

import logging
import os
import uuid
from typing import Any

from sqlalchemy.exc import OperationalError

from api_guardian.application.use_cases.create_pull_request import CreatePullRequestUseCase
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.outbox import OutboxManager
from api_guardian.persistence.repositories.maintenance_case_repo import SQLMaintenanceCaseRepository
from api_guardian.persistence.repositories.migration_repo import SQLMigrationRepository
from api_guardian.persistence.repositories.verification_repo import SQLVerificationRepository
from api_guardian.platform.github_adapter import GitHubAdapter
from api_guardian.workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def create_pull_request_task(self: Any, tenant_id: str, case_id: str) -> None:
    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    logger.info("Starting create_pull_request_task", extra={"tenant_id": tenant_id, "case_id": case_id})

    try:
        case_repo = SQLMaintenanceCaseRepository(db_manager)
        
        case = case_repo.get_by_id(ctx, uuid.UUID(case_id))
        if not case:
            return
        if case.state != MaintenanceCaseState.VERIFYING:
            logger.info("Case is not in VERIFYING state, exiting.")
            return

        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            logger.error("GitHub integration blocked: GITHUB_TOKEN is not set.")
            case.transition_to(MaintenanceCaseState.HUMAN_INTERVENTION_REQUIRED)
            case_repo.save(ctx, case)
            return

        migration_repo = SQLMigrationRepository(db_manager)
        verification_repo = SQLVerificationRepository(db_manager)
        github_platform = GitHubAdapter(installation_token=github_token)

        use_case = CreatePullRequestUseCase(
            case_repo=case_repo,
            migration_repo=migration_repo,
            verification_repo=verification_repo,
            github_platform=github_platform,
        )

        attempt = migration_repo.get_latest_attempt_for_case(ctx, uuid.UUID(case_id))
        if not attempt or not attempt.patch_artifact_id:
            raise ValueError("No patch artifact found for case.")
            
        patch_artifact = migration_repo.get_patch(ctx, attempt.patch_artifact_id)
        if not patch_artifact:
            raise ValueError("Patch artifact not found.")

        pr_number, pr_url = use_case.execute(ctx, uuid.UUID(case_id), patch_artifact)
        logger.info(f"Successfully created PR #{pr_number}: {pr_url}")

        from api_guardian.application.services.notification_service import NotificationService
        NotificationService.create_notification(
            ctx,
            title="Pull Request Created",
            message=f"Automated maintenance PR #{pr_number} created for API integration updates.",
            event_type="PR_CREATED",
            resource_url=pr_url
        )

        with db_manager.get_tenant_session(ctx) as session:
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.orchestrator.orchestrate_case_task",
                {"tenant_id": tenant_id, "case_id": case_id}
            )

    except OperationalError as e:
        logger.warning(f"Transient DB error in create_pull_request_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed create_pull_request_task: {e}")
        raise
