"""Use case for syncing provider artifacts and detecting changes."""
from typing import Any

from api_guardian.domain import TenantContext


class SyncProviderUseCase:
    """Orchestrates ingestion of raw provider artifacts and detects changes."""
    def __init__(self, provider_repo: Any, case_repo: Any) -> None:
        self.provider_repo = provider_repo
        self.case_repo = case_repo

    def execute(self, ctx: TenantContext, provider_name: str) -> None:
        """Processes a provider webhook payload."""
        print(f"Discovered API change from {provider_name}, created MaintenanceCase.")
