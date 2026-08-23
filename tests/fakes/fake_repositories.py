"""In-memory repository implementations for integration tests."""
import uuid
from collections.abc import Sequence

from api_guardian.application.interfaces.repositories import (
    MaintenanceCaseRepository,
    MigrationRepository,
    ProviderChangeRepository,
    PullRequestRepository,
    SnapshotRepository,
    VerificationRepository,
)
from api_guardian.domain import (
    MaintenanceCase,
    MigrationCampaign,
    ProviderChange,
    PullRequest,
    RepositorySnapshot,
    TenantContext,
    VerificationRun,
)


class InMemoryMaintenanceCaseRepository(MaintenanceCaseRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, MaintenanceCase] = {}

    def get_by_id(self, ctx: TenantContext, case_id: uuid.UUID) -> MaintenanceCase | None:
        return self._store.get(case_id)

    def save(self, ctx: TenantContext, case: MaintenanceCase) -> None:
        self._store[case.id] = case

    def list_active_cases(self, ctx: TenantContext, repository_id: uuid.UUID) -> Sequence[MaintenanceCase]:
        return [c for c in self._store.values() if c.repository_id == repository_id]


class InMemorySnapshotRepository(SnapshotRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, RepositorySnapshot] = {}

    def get_by_id(self, ctx: TenantContext, snapshot_id: uuid.UUID) -> RepositorySnapshot | None:
        return self._store.get(snapshot_id)

    def save(self, ctx: TenantContext, snapshot: RepositorySnapshot) -> None:
        self._store[snapshot.id] = snapshot


class InMemoryProviderChangeRepository(ProviderChangeRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, ProviderChange] = {}

    def get_by_id(self, change_id: uuid.UUID) -> ProviderChange | None:
        return self._store.get(change_id)

    def save(self, change: ProviderChange) -> None:
        self._store[change.id] = change


class InMemoryMigrationRepository(MigrationRepository):
    def __init__(self) -> None:
        self._campaigns: dict[uuid.UUID, MigrationCampaign] = {}

    def get_campaign(self, ctx: TenantContext, campaign_id: uuid.UUID) -> MigrationCampaign | None:
        return self._campaigns.get(campaign_id)

    def save_campaign(self, ctx: TenantContext, campaign: MigrationCampaign) -> None:
        self._campaigns[campaign.id] = campaign


class InMemoryVerificationRepository(VerificationRepository):
    def __init__(self) -> None:
        self._runs: dict[uuid.UUID, VerificationRun] = {}

    def get_run(self, ctx: TenantContext, run_id: uuid.UUID) -> VerificationRun | None:
        return self._runs.get(run_id)

    def save_run(self, ctx: TenantContext, run: VerificationRun) -> None:
        self._runs[run.id] = run


class InMemoryPullRequestRepository(PullRequestRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, PullRequest] = {}

    def get_by_id(self, ctx: TenantContext, pr_id: uuid.UUID) -> PullRequest | None:
        return self._store.get(pr_id)

    def save(self, ctx: TenantContext, pr: PullRequest) -> None:
        self._store[pr.id] = pr
