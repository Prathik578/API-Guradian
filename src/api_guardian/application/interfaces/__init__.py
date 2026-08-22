"""Abstract interface contracts (Dependency Inversion Ports)."""

from .repositories import (
    MaintenanceCaseRepository,
    SnapshotRepository,
    ProviderChangeRepository,
    MigrationRepository,
    VerificationRepository,
    PullRequestRepository
)
from .sandbox import SandboxOrchestrator
from .llm import LLMGateway, LLMRole
from .github import GitHubPlatform

__all__ = [
    "MaintenanceCaseRepository",
    "SnapshotRepository",
    "ProviderChangeRepository",
    "MigrationRepository",
    "VerificationRepository",
    "PullRequestRepository",
    "SandboxOrchestrator",
    "LLMGateway",
    "LLMRole",
    "GitHubPlatform"
]
