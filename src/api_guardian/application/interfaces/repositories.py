"""Repository interfaces (Ports) for Domain Entities."""
import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence

from api_guardian.domain import (
    MaintenanceCase,
    MigrationCampaign,
    ProviderChange,
    PullRequest,
    RepositorySnapshot,
    TenantContext,
    VerificationRun,
)


class MaintenanceCaseRepository(ABC):
    @abstractmethod
    def get_by_id(self, ctx: TenantContext, case_id: uuid.UUID) -> MaintenanceCase | None:
        pass

    @abstractmethod
    def save(self, ctx: TenantContext, case: MaintenanceCase) -> None:
        pass

    @abstractmethod
    def list_active_cases(self, ctx: TenantContext, repository_id: uuid.UUID) -> Sequence[MaintenanceCase]:
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
    def save(self, change: ProviderChange) -> None:
        pass


class MigrationRepository(ABC):
    @abstractmethod
    def get_campaign(self, ctx: TenantContext, campaign_id: uuid.UUID) -> MigrationCampaign | None:
        pass

    @abstractmethod
    def save_campaign(self, ctx: TenantContext, campaign: MigrationCampaign) -> None:
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
