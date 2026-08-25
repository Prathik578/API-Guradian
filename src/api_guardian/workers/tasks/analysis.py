"""Celery tasks for analysis."""

import logging
import uuid
from typing import Any

from sqlalchemy.exc import OperationalError

from api_guardian.analysis.graph_builder import GraphBuilder
from api_guardian.application.use_cases.analyze_repository import AnalyzeRepositoryUseCase
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.git.repository_manager import GitRepositoryManager
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.outbox import OutboxManager
from api_guardian.persistence.repositories.snapshot_repo import SQLSnapshotRepository
from api_guardian.platform.storage.local_storage import LocalArtifactStorage
from api_guardian.workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def analyze_repository_task(
    self: Any, tenant_id: str, repository_id: str, branch: str, commit_sha: str, clone_url: str, case_id: str | None = None
) -> str:
    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    logger.info("Starting analyze_repository_task", extra={"tenant_id": tenant_id, "attempt": self.request.retries})
    
    try:
        snapshot_repo = SQLSnapshotRepository(db_manager)
        use_case = AnalyzeRepositoryUseCase(
            snapshot_repo=snapshot_repo,
            git_manager=GitRepositoryManager(),
            graph_builder=GraphBuilder(),
            artifact_storage=LocalArtifactStorage(),
        )
        snapshot = use_case.execute(ctx, uuid.UUID(repository_id), branch, commit_sha, clone_url)
        
        if case_id and snapshot:
            with db_manager.get_tenant_session(ctx) as session:
                OutboxManager.schedule_task(
                    session,
                    "api_guardian.workers.tasks.analysis.assess_impact_task",
                    {"tenant_id": tenant_id, "case_id": case_id, "snapshot_id": str(snapshot.id)}
                )
            
        return str(snapshot.id)
    except OperationalError as e:
        logger.warning(f"Transient DB error in analyze_repository_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed analyze_repository_task: {e}")
        raise


@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def assess_impact_task(self: Any, tenant_id: str, case_id: str, snapshot_id: str) -> None:
    from api_guardian.application.use_cases.assess_impact import AssessImpactUseCase
    from api_guardian.persistence.repositories.impact_assessment_repo import (
        SQLImpactAssessmentRepository,
    )
    from api_guardian.persistence.repositories.maintenance_case_repo import (
        SQLMaintenanceCaseRepository,
    )
    from api_guardian.persistence.repositories.provider_change_repo import (
        SQLProviderChangeRepository,
    )
    
    logger.info("Starting assess_impact_task", extra={"tenant_id": tenant_id, "case_id": case_id, "attempt": self.request.retries})
    
    try:
        ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
        case_repo = SQLMaintenanceCaseRepository(db_manager)
        
        # State-aware idempotency check
        case = case_repo.get_by_id(ctx, uuid.UUID(case_id))
        if case and case.state != MaintenanceCaseState.DISCOVERED:
            logger.info("Case already past DISCOVERED state, exiting harmlessly.")
            return

        change_repo = SQLProviderChangeRepository(db_manager)
        snapshot_repo = SQLSnapshotRepository(db_manager)
        assessment_repo = SQLImpactAssessmentRepository(db_manager)
        
        use_case = AssessImpactUseCase(
            case_repo=case_repo,
            change_repo=change_repo,
            snapshot_repo=snapshot_repo,
            assessment_repo=assessment_repo,
        )
        use_case.execute(ctx, uuid.UUID(case_id), uuid.UUID(snapshot_id))
        
        with db_manager.get_tenant_session(ctx) as session:
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.orchestrator.orchestrate_case_task",
                {"tenant_id": tenant_id, "case_id": case_id}
            )
    except OperationalError as e:
        logger.warning(f"Transient DB error in assess_impact_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except Exception as e:
        logger.error(f"Failed assess_impact_task: {e}")
        raise
