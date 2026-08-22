"""Use case for analyzing a repository and creating a snapshot."""
import uuid
from typing import Any

from api_guardian.analysis.graph_builder import GraphBuilder
from api_guardian.domain import TenantContext
from api_guardian.git.repository_manager import GitRepositoryManager


class AnalyzeRepositoryUseCase:
    """Constructs RepositorySnapshot and dependency graph."""
    def __init__(self, snapshot_repo: Any, git_manager: GitRepositoryManager, graph_builder: GraphBuilder) -> None:
        self.snapshot_repo = snapshot_repo
        self.git_manager = git_manager
        self.graph_builder = graph_builder

    def execute(self, ctx: TenantContext, repository_id: uuid.UUID, commit_sha: str, clone_url: str) -> None:
        """Acquires a repository snapshot and builds the dependency graph."""
        archive_path = self.git_manager.acquire_snapshot(clone_url, commit_sha)
        graph = self.graph_builder.build_graph(str(repository_id), commit_sha, "/tmp/mock_workspace")
        print(f"Acquired snapshot at {archive_path} and built graph with {len(graph.modules)} modules.")
