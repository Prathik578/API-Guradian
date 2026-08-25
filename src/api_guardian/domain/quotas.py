"""Resource quotas and bounds."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class RepositoryResourcePolicy:
    max_repository_size_mb: int = 500
    max_archive_size_mb: int = 100
    max_files: int = 50000
    max_individual_file_size_kb: int = 10000
    max_scan_duration_seconds: int = 300


@dataclass(frozen=True)
class AnalysisResourcePolicy:
    max_graph_nodes: int = 100000
    max_graph_edges: int = 500000
    max_analysis_duration_seconds: int = 600


@dataclass(frozen=True)
class MigrationResourcePolicy:
    max_context_files: int = 50
    max_context_bytes: int = 1024 * 1024  # 1MB
    max_model_tokens: int = 128000
    max_patch_bytes: int = 512 * 1024  # 512KB
    max_changed_lines: int = 1000
    max_attempts: int = 3


@dataclass(frozen=True)
class SandboxResourcePolicy:
    max_cpu_shares: int = 1024
    max_memory_mb: int = 2048
    max_runtime_seconds: int = 1800  # 30 mins
    max_workspace_mb: int = 2048
    max_logs_kb: int = 10000
    max_outbound_bandwidth_mb: int = 500
    max_connections: int = 1000


@dataclass(frozen=True)
class TenantResourcePolicy:
    max_repositories: int = 100
    max_concurrent_analysis_jobs: int = 5
    max_concurrent_sandbox_tasks: int = 2
    max_llm_tokens_monthly: int = 10000000
    max_monthly_spend_cents: int = 50000  # $500.00
    max_artifact_storage_gb: int = 100


@dataclass(frozen=True)
class GlobalResourcePolicy:
    max_sandbox_concurrency: int = 100
    max_queue_depth: int = 10000
    max_global_llm_spend_daily_cents: int = 100000
    max_egress_gb_monthly: int = 10000


@dataclass(frozen=True)
class ResourcePolicy:
    """Central configuration object for all system limits."""
    repository: RepositoryResourcePolicy = RepositoryResourcePolicy()
    analysis: AnalysisResourcePolicy = AnalysisResourcePolicy()
    migration: MigrationResourcePolicy = MigrationResourcePolicy()
    sandbox: SandboxResourcePolicy = SandboxResourcePolicy()
    tenant: TenantResourcePolicy = TenantResourcePolicy()
    global_limits: GlobalResourcePolicy = GlobalResourcePolicy()
    
    _instance: ClassVar['ResourcePolicy | None'] = None
    
    @classmethod
    def get_default(cls) -> 'ResourcePolicy':
        if cls._instance is None:
            cls._instance = ResourcePolicy()
        return cls._instance
