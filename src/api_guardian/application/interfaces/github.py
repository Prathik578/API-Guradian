"""GitHub platform integration interface (Port)."""
import uuid
from abc import ABC, abstractmethod


class GitHubPlatform(ABC):
    @abstractmethod
    def check_head_sha(self, repository_id: uuid.UUID, branch: str) -> str:
        """Fetches the current HEAD commit SHA for a branch."""
        pass

    @abstractmethod
    def open_pull_request(
        self,
        repository_id: uuid.UUID,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str
    ) -> tuple[int, str]:
        """Opens a Pull Request on GitHub.
        
        Returns:
            Tuple of (pr_number, pr_url).
        """
        pass
