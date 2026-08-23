"""Repository interfaces (Ports) for Domain Entities."""

import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from api_guardian.domain import (
    MaintenanceCase,
    MigrationCampaign,
    ProviderChange,
    PullRequest,
    RawArtifact,
    RepositorySnapshot,
    TenantContext,
    VerificationRun,
)
from api_guardian.domain.migration import MigrationAttempt, PatchArtifact


class MaintenanceCaseRepository(ABC):
    @abstractmethod
    def get_by_id(self, ctx: TenantContext, case_id: uuid.UUID) -> MaintenanceCase | None:
        pass

    @abstractmethod
    def save(self, ctx: TenantContext, case: MaintenanceCase) -> MaintenanceCase:
        pass

    @abstractmethod
    def list_active_cases(
        self, ctx: TenantContext, repository_id: uuid.UUID
    ) -> Sequence[MaintenanceCase]:
        pass


class SnapshotRepository(ABC):
    @abstractmethod
    def get_by_id(self, ctx: TenantContext, snapshot_id: uuid.UUID) -> RepositorySnapshot | None:
        pass

    @abstractmethod
    def save(self, ctx: TenantContext, snapshot: RepositorySnapshot) -> None:
        pass


class ProviderChangeRepository(ABC):
    @abstractmethod
    def get_by_id(self, change_id: uuid.UUID) -> ProviderChange | None:
        # Note: ProviderChanges might be system-wide rather than tenant-specific
        pass

    @abstractmethod
    def get_by_native_id(self, provider: str, provider_native_id: str) -> ProviderChange | None:
        pass

    @abstractmethod
    def save(self, change: ProviderChange) -> ProviderChange:
        pass

    @abstractmethod
    def save_revision(
        self,
        change: ProviderChange,
        evidence: dict[str, Any],
        evidence_source: str
    ) -> ProviderChange:
        """
        Atomically increments the revision of the canonical change and inserts a
        ProviderChangeRevision record. Returns the updated canonical change.
        """


class RawArtifactRepository(ABC):
    @abstractmethod
    def get_by_content_hash(
        self, provider: str, source_key: str, content_hash: str
    ) -> RawArtifact | None:
        pass

    @abstractmethod
    def get_latest_by_source(
        self, provider: str, source_key: str, exclude_id: uuid.UUID | None = None
    ) -> RawArtifact | None:
        pass

    @abstractmethod
    def save(self, artifact: RawArtifact) -> RawArtifact:
        pass


class MigrationRepository(ABC):
    @abstractmethod
    def get_campaign(self, ctx: TenantContext, campaign_id: uuid.UUID) -> MigrationCampaign | None:
        pass

    @abstractmethod
    def save_campaign(self, ctx: TenantContext, campaign: MigrationCampaign) -> None:
        pass

    @abstractmethod
    def save_patch(self, ctx: TenantContext, patch: "PatchArtifact") -> None:
        pass

    @abstractmethod
    def save_attempt(self, ctx: TenantContext, attempt: "MigrationAttempt") -> None:
        pass


class VerificationRepository(ABC):
    @abstractmethod
    def get_run(self, ctx: TenantContext, run_id: uuid.UUID) -> VerificationRun | None:
        pass

    @abstractmethod
    def save_run(self, ctx: TenantContext, run: VerificationRun) -> None:
        pass


class PullRequestRepository(ABC):
    @abstractmethod
    def get_by_id(self, ctx: TenantContext, pr_id: uuid.UUID) -> PullRequest | None:
        pass

    @abstractmethod
    def save(self, ctx: TenantContext, pr: PullRequest) -> None:
        pass
