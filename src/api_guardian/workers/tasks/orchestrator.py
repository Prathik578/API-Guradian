"""Celery tasks for orchestrating MaintenanceCases."""

import logging
import uuid
from typing import Any

from sqlalchemy.exc import OperationalError

from api_guardian.application.use_cases.orchestrate_case import OrchestrateCaseUseCase
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.repositories.maintenance_case_repo import SQLMaintenanceCaseRepository
from api_guardian.persistence.outbox import OutboxManager
from api_guardian.workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=5)  # type: ignore[untyped-decorator]
def orchestrate_case_task(self: Any, tenant_id: str, case_id: str) -> None:
    """Evaluates case state and triggers next phase."""
    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    logger.info("Starting orchestrate_case_task", extra={"tenant_id": tenant_id, "case_id": case_id})

    try:
        case_repo = SQLMaintenanceCaseRepository(db_manager)
        use_case = OrchestrateCaseUseCase(case_repo=case_repo)
        state = use_case.execute(ctx, uuid.UUID(case_id))

        # Dispatch next task based on state
        case = case_repo.get_by_id(ctx, uuid.UUID(case_id))
        if not case:
            return
            
        with db_manager.get_tenant_session(ctx) as session:
            if state == MaintenanceCaseState.DISCOVERED:
                from api_guardian.persistence.models.tables import RepositoryModel
                repo_model = session.get(RepositoryModel, case.repository_id)
                if not repo_model:
                    raise ValueError(f"Repository {case.repository_id} not found")
                
                clone_url = f"https://github.com/{repo_model.github_full_name}.git"
                OutboxManager.schedule_task(
                    session,
                    "api_guardian.workers.tasks.analysis.analyze_repository_task",
                    {
                        "tenant_id": tenant_id,
                        "repository_id": str(case.repository_id),
                        "branch": repo_model.default_branch,
                        "commit_sha": case.base_revision_sha,
                        "clone_url": clone_url,
                        "case_id": case_id,
                    }
                )
            elif state == MaintenanceCaseState.AFFECTED_ACTION_REQUIRED:
                OutboxManager.schedule_task(
                    session,
                    "api_guardian.workers.tasks.migration.generate_migration_task",
                    {"tenant_id": tenant_id, "case_id": case_id}
                )
            elif state == MaintenanceCaseState.MIGRATING:
                pass # Awaiting migration generation
            elif state == MaintenanceCaseState.VERIFYING:
                pass # Awaiting verification result
            elif state == MaintenanceCaseState.PR_OPEN:
                pass # Awaiting GitHub webhook

    except OperationalError as e:
        logger.warning(f"Transient DB error in orchestrate_case_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed orchestrate_case_task: {e}")
        raise
