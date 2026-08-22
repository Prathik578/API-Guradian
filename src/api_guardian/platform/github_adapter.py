"""GitHub Platform Adapter."""
import uuid

from api_guardian.application.interfaces.github import GitHubPlatform


class GitHubAdapter(GitHubPlatform):
    """Implementation of GitHubPlatform using httpx and GitHub REST API."""

    def __init__(self, api_base_url: str = "https://api.github.com"):
        self.api_base_url = api_base_url

    def _get_headers(self, installation_token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def check_head_sha(self, repository_id: uuid.UUID, branch: str) -> str:
        # TODO: Implement API call to get ref
        # For MVP, returning a dummy sha
        return "dummy_sha_8f3d1"

    def push_patch_to_branch(
        self, 
        repository_id: uuid.UUID, 
        base_sha: str, 
        branch_name: str, 
        files_to_update: dict[str, str], 
        commit_message: str
    ) -> str:
        # TODO: Implement Git Trees API to create blobs, tree, commit, and update ref
        # 1. Create blobs for each file in files_to_update
        # 2. Create a tree using base_sha and new blobs
        # 3. Create a commit pointing to the new tree and base_sha
        # 4. Create or update ref for branch_name
        return "new_dummy_sha_4b2c1"

    def open_pull_request(
        self,
        repository_id: uuid.UUID,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str
    ) -> tuple[int, str]:
        # TODO: Implement Pulls API call
        # POST /repos/{owner}/{repo}/pulls
        return 42, "https://github.com/dummy/repo/pull/42"
