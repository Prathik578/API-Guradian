"""Use case for creating a pull request."""

import uuid
from typing import Any

from api_guardian.application.interfaces.github import GitHubPlatform
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.platform.pr_templates import PRTemplateBuilder


class CreatePullRequestUseCase:
    """Validates target HEAD, checks non-stale, opens GitHub PR."""

    def __init__(self, case_repo: Any, github_platform: GitHubPlatform) -> None:
        self.case_repo = case_repo
        self.github_platform = github_platform

    def execute(
        self, ctx: TenantContext, case_id: uuid.UUID, patch_artifact: Any
    ) -> tuple[int, str]:
        """Creates the pull request."""

        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError("Case not found")

        current_head = self.github_platform.check_head_sha(case.repository_id, "main")
        if current_head != case.base_revision_sha:
            case.transition_to(MaintenanceCaseState.STALE)
            self.case_repo.save(ctx, case)
            raise RuntimeError("Repository HEAD advanced. Case is stale.")

        branch_name = f"api-guardian/patch-{case_id.hex[:8]}"
        files_to_update = {
            block.file_path: block.modified_snippet for block in patch_artifact.diff_blocks
        }

        self.github_platform.push_patch_to_branch(
            repository_id=case.repository_id,
            base_sha=case.base_revision_sha,
            branch_name=branch_name,
            files_to_update=files_to_update,
            commit_message="fix: Update Provider API usage",
        )

        body = PRTemplateBuilder.build_pr_body(
            provider_name="Stripe",
            change_title="API Update",
            affected_files_count=len(files_to_update),
            audit_passed=True,
        )

        pr_number, pr_url = self.github_platform.open_pull_request(
            repository_id=case.repository_id,
            head_branch=branch_name,
            base_branch="main",
            title="Auto-migration: Provider API Update",
            body=body,
        )

        case.transition_to(MaintenanceCaseState.PR_OPEN)
        self.case_repo.save(ctx, case)

        return pr_number, pr_url
