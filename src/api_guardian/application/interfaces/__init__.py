"""Abstract interface contracts (Dependency Inversion Ports)."""

from .github import GitHubPlatform
from .llm import LLMGateway, LLMRole
from .repositories import (
    ImpactAssessmentRepository,
    MaintenanceCaseRepository,
    MigrationRepository,
    ProviderChangeRepository,
    PullRequestRepository,
    RawArtifactRepository,
    SnapshotRepository,
    VerificationRepository,
)
from .sandbox import SandboxOrchestrator
from .storage import ArtifactStoragePort

__all__ = [
    "ArtifactStoragePort",
    "GitHubPlatform",
    "ImpactAssessmentRepository",
    "LLMGateway",
    "LLMRole",
    "MaintenanceCaseRepository",
    "MigrationRepository",
    "ProviderChangeRepository",
    "PullRequestRepository",
    "RawArtifactRepository",
    "SandboxOrchestrator",
    "SnapshotRepository",
    "VerificationRepository",
]
