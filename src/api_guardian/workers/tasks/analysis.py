"""Celery tasks for analysis."""
import uuid

from api_guardian.analysis.graph_builder import GraphBuilder
from api_guardian.application.use_cases.analyze_repository import AnalyzeRepositoryUseCase
from api_guardian.domain import TenantContext
from api_guardian.git.repository_manager import GitRepositoryManager
from api_guardian.workers.celery_app import app


@app.task  # type: ignore[untyped-decorator]
def analyze_repository_task(tenant_id: str, repository_id: str, commit_sha: str, clone_url: str) -> None:
    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    use_case = AnalyzeRepositoryUseCase(
        snapshot_repo=None,
        git_manager=GitRepositoryManager(),
        graph_builder=GraphBuilder()
    )
    use_case.execute(ctx, uuid.UUID(repository_id), commit_sha, clone_url)
