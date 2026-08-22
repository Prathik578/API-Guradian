"""Domain model layer - Pure business entities and rules.

Rule: Domain code MUST NOT import external frameworks (FastAPI, SQLAlchemy, Celery, boto3, etc).
"""

from .exceptions import (
    DomainError,
    InvalidStateTransitionError,
    ResourceNotFoundError,
    InvariantViolationError
)
from .organization import TenantContext, Organization
from .repository import RepositoryRevision, RepositorySnapshot, Repository
from .provider_change import (
    ChangeClassification,
    VersionGraph,
    RawArtifact,
    CandidateChange,
    ProviderChange
)
from .maintenance import (
    MaintenanceCaseState,
    ImpactClassification,
    EvidenceLevel,
    ImpactAssessment,
    MaintenanceCase
)
from .migration import (
    MigrationState,
    PatchArtifact,
    MigrationAttempt,
    MigrationCampaign
)
from .verification import (
    VerificationState,
    ResultClass,
    VerificationPlan,
    VerificationResult,
    VerificationRun
)
from .pull_request import PullRequestState, PullRequest

__all__ = [
    "DomainError",
    "InvalidStateTransitionError",
    "ResourceNotFoundError",
    "InvariantViolationError",
    "TenantContext",
    "Organization",
    "RepositoryRevision",
    "RepositorySnapshot",
    "Repository",
    "ChangeClassification",
    "VersionGraph",
    "RawArtifact",
    "CandidateChange",
    "ProviderChange",
    "MaintenanceCaseState",
    "ImpactClassification",
    "EvidenceLevel",
    "ImpactAssessment",
    "MaintenanceCase",
    "MigrationState",
    "PatchArtifact",
    "MigrationAttempt",
    "MigrationCampaign",
    "VerificationState",
    "ResultClass",
    "VerificationPlan",
    "VerificationResult",
    "VerificationRun",
    "PullRequestState",
    "PullRequest"
]
