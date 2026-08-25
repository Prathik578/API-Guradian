"""Repository-related tasks."""

import logging
import uuid
from typing import Any

from celery import shared_task
from sqlalchemy import select

from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import MaintenanceCaseModel
from api_guardian.persistence.outbox import OutboxManager

logger = logging.getLogger(__name__)


@shared_task  # type: ignore
def handle_push_task(payload: dict[str, Any]) -> None:
    """Handles a GitHub push event."""
    tenant_id_str = payload.get("tenant_id_str")
    event_payload = payload.get("payload", {})

    ref = event_payload.get("ref", "")
    if not ref.startswith("refs/heads/"):
        return
    branch = ref.replace("refs/heads/", "")
    
    repo_data = event_payload.get("repository", {})
    repo_full_name = repo_data.get("full_name")
    after_sha = event_payload.get("after")

    if not repo_full_name or not after_sha or not tenant_id_str:
        return

    tenant_id = uuid.UUID(tenant_id_str)
    ctx = TenantContext(tenant_id=tenant_id)

    with db_manager.get_tenant_session(ctx) as session:
        from api_guardian.persistence.models.tables import RepositoryModel
        # Find repo by full name
        repo_model = session.scalar(
            select(RepositoryModel).where(RepositoryModel.github_full_name == repo_full_name)
        )
        if not repo_model:
            return
            
        # Only process pushes to default branch
        if branch != repo_model.default_branch:
            return

        # Find all active maintenance cases for this repository
        active_cases = session.scalars(
            select(MaintenanceCaseModel).where(
                MaintenanceCaseModel.repository_id == repo_model.id,
                MaintenanceCaseModel.state.in_([
                    MaintenanceCaseState.DISCOVERED,
                    MaintenanceCaseState.IMPACT_ANALYZING,
                    MaintenanceCaseState.AFFECTED_ACTION_REQUIRED,
                    MaintenanceCaseState.MIGRATING,
                    MaintenanceCaseState.VERIFYING,
                    MaintenanceCaseState.PR_OPEN,
                    MaintenanceCaseState.STALE
                ])
            )
        ).all()
        
        for case in active_cases:
            # Re-queue analysis for each active case with the NEW commit_sha
            clone_url = f"https://github.com/{repo_model.github_full_name}.git"
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.analysis.analyze_repository_task",
                {
                    "tenant_id": str(tenant_id),
                    "repository_id": str(repo_model.id),
                    "branch": branch,
                    "commit_sha": after_sha,
                    "case_id": str(case.id),
                }
            )
