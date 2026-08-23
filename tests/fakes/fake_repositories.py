"""In-memory repository implementations for integration tests."""
import uuid
from collections.abc import Sequence
from typing import Any

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
    MigrationAttempt,
    MigrationCampaign,
    PatchArtifact,
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

    def save(self, ctx: TenantContext, case: MaintenanceCase) -> MaintenanceCase:
        # Simulate unique constraint: repository_id, provider_change_id, base_revision_sha
        for existing_case in self._store.values():
            if (
                existing_case.repository_id == case.repository_id
                and existing_case.provider_change_id == case.provider_change_id
                and existing_case.base_revision_sha == case.base_revision_sha
            ):
                return existing_case
        self._store[case.id] = case
        return case

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

    def get_by_native_id(self, provider: str, provider_native_id: str) -> ProviderChange | None:
        for change in self._store.values():
            if change.provider == provider and change.provider_native_id == provider_native_id:
                return change
        return None

    def save(self, change: ProviderChange) -> ProviderChange:
        # Simulate unique constraint: provider, provider_native_id
        for existing_change in self._store.values():
            if (
                existing_change.provider == change.provider
                and existing_change.provider_native_id == change.provider_native_id
            ):
                return existing_change
        self._store[change.id] = change
        return change

    def save_revision(self, change: ProviderChange, evidence: dict[str, Any], evidence_source: str) -> ProviderChange:
        change.revision += 1
        self._store[change.id] = change
        return change


class InMemoryMigrationRepository(MigrationRepository):
    def __init__(self) -> None:
        self._campaigns: dict[uuid.UUID, MigrationCampaign] = {}
        self._patches: dict[uuid.UUID, PatchArtifact] = {}
        self._attempts: dict[uuid.UUID, MigrationAttempt] = {}

    def get_campaign(self, ctx: TenantContext, campaign_id: uuid.UUID) -> MigrationCampaign | None:
        return self._campaigns.get(campaign_id)

    def save_campaign(self, ctx: TenantContext, campaign: MigrationCampaign) -> None:
        self._campaigns[campaign.id] = campaign

    def save_patch(self, ctx: TenantContext, patch: "PatchArtifact") -> None:
        self._patches[patch.id] = patch

    def save_attempt(self, ctx: TenantContext, attempt: "MigrationAttempt") -> None:
        self._attempts[attempt.id] = attempt


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
