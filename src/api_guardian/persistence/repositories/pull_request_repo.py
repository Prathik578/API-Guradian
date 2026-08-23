"""Concrete implementation of PullRequestRepository."""
import uuid

from api_guardian.application.interfaces import PullRequestRepository
from api_guardian.domain import PullRequest, PullRequestState, TenantContext
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import PullRequestModel


class SQLPullRequestRepository(PullRequestRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_by_id(self, ctx: TenantContext, pr_id: uuid.UUID) -> PullRequest | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(PullRequestModel, pr_id)
            if not model:
                return None
            return PullRequest(
                id=model.id,
                case_id=model.case_id,
                patch_artifact_id=model.patch_artifact_id,
                repository_id=model.repository_id,
                github_pr_number=model.github_pr_number,
                github_pr_url=model.github_pr_url,
                head_branch=model.head_branch,
                base_branch=model.base_branch,
                state=PullRequestState(model.state)
            )

    def save(self, ctx: TenantContext, pr: PullRequest) -> None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(PullRequestModel, pr.id)
            if not model:
                model = PullRequestModel(
                    id=pr.id,
                    organization_id=ctx.tenant_id,
                    case_id=pr.case_id,
                    patch_artifact_id=pr.patch_artifact_id,
                    repository_id=pr.repository_id,
                    github_pr_number=pr.github_pr_number,
                    github_pr_url=pr.github_pr_url,
                    head_branch=pr.head_branch,
                    base_branch=pr.base_branch,
                )
                session.add(model)
            model.state = pr.state.value
