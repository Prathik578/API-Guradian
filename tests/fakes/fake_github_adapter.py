"""Deterministic FakeGitHubAdapter for integration tests."""
import uuid
from typing import Any

from api_guardian.application.interfaces.github import GitHubPlatform


class FakeGitHubAdapter(GitHubPlatform):
    """Records all calls for later assertion, returns deterministic values."""

    def __init__(self, head_sha: str) -> None:
        self.head_sha = head_sha
        self.pushed_branches: list[dict[str, Any]] = []
        self.opened_prs: list[dict[str, Any]] = []

    def check_head_sha(self, repository_id: uuid.UUID, branch: str) -> str:
        return self.head_sha

    def push_patch_to_branch(
        self,
        repository_id: uuid.UUID,
        base_sha: str,
        branch_name: str,
        files_to_update: dict[str, str],
        commit_message: str,
    ) -> str:
        record: dict[str, Any] = {
            "repository_id": repository_id,
            "base_sha": base_sha,
            "branch_name": branch_name,
            "files_to_update": files_to_update,
            "commit_message": commit_message,
        }
        self.pushed_branches.append(record)
        return "fake_new_commit_sha_abc123"

    def open_pull_request(
        self,
        repository_id: uuid.UUID,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
    ) -> tuple[int, str]:
        record: dict[str, Any] = {
            "repository_id": repository_id,
            "head_branch": head_branch,
            "base_branch": base_branch,
            "title": title,
            "body": body,
        }
        self.opened_prs.append(record)
        return 42, "https://github.com/test-org/test-repo/pull/42"
