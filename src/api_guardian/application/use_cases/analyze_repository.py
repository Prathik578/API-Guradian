"""Use case for analyzing a repository and creating a snapshot."""

import hashlib
import uuid

from api_guardian.analysis.graph_builder import GraphBuilder
from api_guardian.application.interfaces import SnapshotRepository
from api_guardian.application.interfaces.storage import ArtifactStoragePort
from api_guardian.domain import RepositoryRevision, RepositorySnapshot, TenantContext
from api_guardian.git.repository_manager import GitRepositoryManager


class AnalyzeRepositoryUseCase:
    """Constructs RepositorySnapshot and dependency graph."""

    def __init__(
        self,
        snapshot_repo: SnapshotRepository,
        git_manager: GitRepositoryManager,
        graph_builder: GraphBuilder,
        artifact_storage: ArtifactStoragePort,
    ) -> None:
        self.snapshot_repo = snapshot_repo
        self.git_manager = git_manager
        self.graph_builder = graph_builder
        self.artifact_storage = artifact_storage

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
        if not archive_path_str:
            raise RuntimeError("Failed to acquire repository snapshot.")
            
        archive_path = Path(archive_path_str)
        workspace_path = str(archive_path.parent)

        graph = self.graph_builder.build_graph(str(repository_id), commit_sha, workspace_path)

        if not archive_path.exists():
            raise RuntimeError(f"Snapshot archive missing at {archive_path}")

        archive_hash = self.artifact_storage.put_snapshot(
            tenant_id=str(ctx.tenant_id),
            repository_id=str(repository_id),
            commit_sha=commit_sha,
            archive_path=str(archive_path),
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
