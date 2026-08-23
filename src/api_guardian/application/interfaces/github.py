"""GitHub platform integration interface (Port)."""

import uuid
from abc import ABC, abstractmethod


class GitHubPlatform(ABC):
    @abstractmethod
    def check_head_sha(self, repository_id: uuid.UUID, branch: str) -> str:
        """Fetches the current HEAD commit SHA for a branch."""

    @abstractmethod
    def push_patch_to_branch(
        self,
        repository_id: uuid.UUID,
        base_sha: str,
        branch_name: str,
        files_to_update: dict[str, str],
        commit_message: str,
    ) -> str:
        """Commits and pushes file changes to a new or existing branch.

        Returns:
            The new commit SHA.
        """

    @abstractmethod
    def open_pull_request(
        self, repository_id: uuid.UUID, head_branch: str, base_branch: str, title: str, body: str
    ) -> tuple[int, str]:
        """Opens a Pull Request on GitHub.

        Returns:
            Tuple of (pr_number, pr_url).
        """
