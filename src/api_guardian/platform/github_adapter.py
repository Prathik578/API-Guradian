"""GitHub Platform Adapter."""

import uuid

from api_guardian.application.interfaces.github import GitHubPlatform
import httpx


class GitHubAdapter(GitHubPlatform):
    """Implementation of GitHubPlatform using httpx and GitHub REST API."""

    def __init__(self, api_base_url: str = "https://api.github.com", installation_token: str = "placeholder_token"):
        self.api_base_url = api_base_url
        self.installation_token = installation_token

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.installation_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_repo_name(self, repository_id: uuid.UUID) -> str:
        # In a real system, we'd query the DB for the repo's full name.
        # For the adapter interface without DB access, this assumes the repo_id 
        # mapping is handled upstream or passed as full name.
        # Since interface requires uuid, let's assume it maps directly for now.
        return f"org/{repository_id.hex}"

    def check_head_sha(self, repository_id: uuid.UUID, branch: str) -> str:
        repo_name = self._get_repo_name(repository_id)
        url = f"{self.api_base_url}/repos/{repo_name}/git/ref/heads/{branch}"
        
        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return str(data["object"]["sha"])

    def push_patch_to_branch(
        self,
        repository_id: uuid.UUID,
        base_sha: str,
        branch_name: str,
        files_to_update: dict[str, str],
        commit_message: str,
    ) -> str:
        repo_name = self._get_repo_name(repository_id)
        
        with httpx.Client(headers=self._get_headers()) as client:
            # 1. Create blobs
            tree_entries = []
            for filepath, content in files_to_update.items():
                blob_url = f"{self.api_base_url}/repos/{repo_name}/git/blobs"
                blob_resp = client.post(blob_url, json={"content": content, "encoding": "utf-8"})
                blob_resp.raise_for_status()
                tree_entries.append({
                    "path": filepath,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_resp.json()["sha"]
                })
            
            # 2. Create tree
            tree_url = f"{self.api_base_url}/repos/{repo_name}/git/trees"
            tree_resp = client.post(tree_url, json={"base_tree": base_sha, "tree": tree_entries})
            tree_resp.raise_for_status()
            new_tree_sha = tree_resp.json()["sha"]
            
            # 3. Create commit
            commit_url = f"{self.api_base_url}/repos/{repo_name}/git/commits"
            commit_resp = client.post(commit_url, json={
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [base_sha]
            })
            commit_resp.raise_for_status()
            new_commit_sha = commit_resp.json()["sha"]
            
            # 4. Create or update ref
            ref_url = f"{self.api_base_url}/repos/{repo_name}/git/refs"
            ref_resp = client.post(ref_url, json={
                "ref": f"refs/heads/{branch_name}",
                "sha": new_commit_sha
            })
            if ref_resp.status_code == 422: # Ref exists, update it
                update_url = f"{self.api_base_url}/repos/{repo_name}/git/refs/heads/{branch_name}"
                client.patch(update_url, json={"sha": new_commit_sha, "force": True}).raise_for_status()
            else:
                ref_resp.raise_for_status()
                
            return str(new_commit_sha)

    def open_pull_request(
        self, repository_id: uuid.UUID, head_branch: str, base_branch: str, title: str, body: str
    ) -> tuple[int, str]:
        repo_name = self._get_repo_name(repository_id)
        url = f"{self.api_base_url}/repos/{repo_name}/pulls"
        
        with httpx.Client() as client:
            response = client.post(url, headers=self._get_headers(), json={
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch
            })
            response.raise_for_status()
            data = response.json()
            return int(data["number"]), str(data["html_url"])
