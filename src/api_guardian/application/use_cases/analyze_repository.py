"""Use case for analyzing a repository and creating a snapshot."""

import hashlib
import uuid

from api_guardian.analysis.graph_builder import GraphBuilder
from api_guardian.application.interfaces import SnapshotRepository
from api_guardian.domain import RepositoryRevision, RepositorySnapshot, TenantContext
from api_guardian.git.repository_manager import GitRepositoryManager


class AnalyzeRepositoryUseCase:
    """Constructs RepositorySnapshot and dependency graph."""

    def __init__(
        self,
        snapshot_repo: SnapshotRepository,
        git_manager: GitRepositoryManager,
        graph_builder: GraphBuilder,
    ) -> None:
        self.snapshot_repo = snapshot_repo
        self.git_manager = git_manager
        self.graph_builder = graph_builder

    def execute(
        self,
        ctx: TenantContext,
        repository_id: uuid.UUID,
        branch: str,
        commit_sha: str,
        clone_url: str,
    ) -> RepositorySnapshot:
        """Acquires a repository snapshot, builds the dependency graph, and saves it."""
        from pathlib import Path

        archive_path_str = self.git_manager.acquire_snapshot(clone_url, commit_sha)
        archive_path = Path(archive_path_str) if archive_path_str else None

        # Using archive_path as workspace for graph builder for now
        workspace_path = str(archive_path.parent) if archive_path else "/tmp/mock_workspace"

        graph = self.graph_builder.build_graph(str(repository_id), commit_sha, workspace_path)

        # Compute a dummy hash if archive_path doesn't exist, else real hash
        archive_hash = (
            hashlib.sha256(b"mock_archive").hexdigest()
            if not archive_path
            else hashlib.sha256(archive_path.read_bytes()).hexdigest()
        )

        snapshot = RepositorySnapshot(
            id=uuid.uuid4(),
            revision=RepositoryRevision(
                repository_id=repository_id,
                branch=branch,
                commit_sha=commit_sha,
            ),
            archive_content_hash=archive_hash,
            code_model_version="1.0.0",
            dependency_graph={"modules": list(graph.modules.keys())},
        )

        self.snapshot_repo.save(ctx, snapshot)
        return snapshot
