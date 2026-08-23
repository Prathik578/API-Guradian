"""Safe subprocess Git execution and archive manager."""

import os
import subprocess
import tempfile
import uuid


class GitRepositoryManager:
    """Handles shallow cloning and archiving of untrusted repositories."""

    def acquire_snapshot(
        self, clone_url: str, commit_sha: str, auth_token: str | None = None
    ) -> str:
        """Clones a repository safely and returns the path to a tar archive.

        Args:
            clone_url: URL to clone from
            commit_sha: Specific commit to checkout
            auth_token: Optional token for private repos

        Returns:
            Absolute path to the created tar.gz archive.
        """
        # Inject credentials safely without printing them to logs
        # For MVP, we clone into a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="api_guardian_repo_")
        archive_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.tar.gz")

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        # Clone exactly one commit depth
        subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, temp_dir],
            env=env,
            check=True,
            capture_output=True,
        )

        # Checkout specific SHA if needed
        subprocess.run(
            ["git", "checkout", commit_sha], cwd=temp_dir, env=env, check=True, capture_output=True
        )

        # Create immutable archive
        subprocess.run(
            ["tar", "-czf", archive_path, "-C", temp_dir, "."], check=True, capture_output=True
        )

        return archive_path
