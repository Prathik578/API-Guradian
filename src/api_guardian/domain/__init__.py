"""Domain model layer - Pure business entities and rules.

Rule: Domain code MUST NOT import external frameworks (FastAPI, SQLAlchemy, Celery, boto3, etc).
"""

from .exceptions import (
    DomainError,
    InvalidStateTransitionError,
    InvariantViolationError,
    ResourceNotFoundError,
)
from .maintenance import (
    EvidenceLevel,
    ImpactAssessment,
    ImpactClassification,
    MaintenanceCase,
    MaintenanceCaseState,
)
from .migration import MigrationAttempt, MigrationCampaign, MigrationState, PatchArtifact
from .organization import Organization, TenantContext
from .provider_change import (
    CandidateChange,
    ChangeClassification,
    EvidenceSource,
    ProviderChange,
    ProviderChangeRevision,
    RawArtifact,
    VersionGraph,
)
from .pull_request import PullRequest, PullRequestState
from .repository import Repository, RepositoryRevision, RepositorySnapshot
from .verification import (
    ResultClass,
    VerificationPlan,
    VerificationResult,
    VerificationRun,
    VerificationState,
)

__all__ = [
    "CandidateChange",
    "ChangeClassification",
    "DomainError",
    "EvidenceLevel",
    "EvidenceSource",
    "ImpactAssessment",
    "ImpactClassification",
    "InvalidStateTransitionError",
    "InvariantViolationError",
    "MaintenanceCase",
    "MaintenanceCaseState",
    "MigrationAttempt",
    "MigrationCampaign",
    "MigrationState",
    "Organization",
    "PatchArtifact",
    "ProviderChange",
    "ProviderChangeRevision",
    "PullRequest",
    "PullRequestState",
    "RawArtifact",
    "Repository",
    "RepositoryRevision",
    "RepositorySnapshot",
    "ResourceNotFoundError",
    "ResultClass",
    "TenantContext",
    "VerificationPlan",
    "VerificationResult",
    "VerificationRun",
    "VerificationState",
    "VersionGraph",
]
