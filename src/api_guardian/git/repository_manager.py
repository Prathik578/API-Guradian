"""Safe subprocess Git execution and archive manager."""

import os
import subprocess
import tempfile
import uuid


class GitRepositoryManager:
    """Handles shallow cloning and archiving of untrusted repositories."""

    def __init__(self, max_repo_size_bytes: int = 500 * 1024 * 1024, max_file_count: int = 50000) -> None:
        self.max_repo_size_bytes = max_repo_size_bytes
        self.max_file_count = max_file_count

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
        env["GIT_LFS_SKIP_SMUDGE"] = "1"  # Block LFS smudge

        # Clone exactly one commit depth
        subprocess.run(
            [
                "git", 
                "-c", "core.hooksPath=/dev/null", 
                "-c", "submodule.recurse=false", 
                "clone", 
                "--depth", "1", 
                clone_url, 
                temp_dir
            ],
            env=env,
            check=True,
            capture_output=True,
        )

        # Checkout specific SHA if needed
        subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "checkout", commit_sha], cwd=temp_dir, env=env, check=True, capture_output=True
        )

        # Check repository limits and symlink policy
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            if ".git" in dirnames:
                dirnames.remove(".git")  # Skip .git directory for size/symlink checks
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.islink(fp):
                    raise ValueError("Repository contains symlinks, which are explicitly rejected.")
                total_size += os.path.getsize(fp)
                file_count += 1
                
        if total_size > self.max_repo_size_bytes:
            raise ValueError(f"Repository exceeds maximum size limit of {self.max_repo_size_bytes} bytes.")
        if file_count > self.max_file_count:
            raise ValueError(f"Repository exceeds maximum file count limit of {self.max_file_count}.")

        # Create immutable archive (excluding .git)
        subprocess.run(
            ["tar", "--exclude=.git", "-czf", archive_path, "-C", temp_dir, "."], check=True, capture_output=True
        )

        return archive_path
