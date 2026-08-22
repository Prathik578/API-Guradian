"""Abstract interface contracts (Dependency Inversion Ports)."""

from .github import GitHubPlatform
from .llm import LLMGateway, LLMRole
from .repositories import (
    MaintenanceCaseRepository,
    MigrationRepository,
    ProviderChangeRepository,
    PullRequestRepository,
    SnapshotRepository,
    VerificationRepository,
)
from .sandbox import SandboxOrchestrator

__all__ = [
    "GitHubPlatform",
    "LLMGateway",
    "LLMRole",
    "MaintenanceCaseRepository",
    "MigrationRepository",
    "ProviderChangeRepository",
    "PullRequestRepository",
    "SandboxOrchestrator",
    "SnapshotRepository",
    "VerificationRepository"
]
