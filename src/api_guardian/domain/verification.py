"""Verification domain models."""
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class VerificationState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    VERIFIED = "verified"
    BASELINE_FAILED = "baseline_failed"
    PATCH_CONFLICT = "patch_conflict"
    TESTS_FAILED = "tests_failed"
    VERIFICATION_INTEGRITY_FAILED = "verification_integrity_failed"
    INFRASTRUCTURE_FAILED = "infrastructure_failed"
    TIMEOUT = "timeout"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    NO_TEST_COMMAND = "no_test_command"


class ResultClass(str, Enum):
    VERIFIED = "verified"
    BASELINE_FAILED = "baseline_failed"
    PATCH_CONFLICT = "patch_conflict"
    AUDIT_FAILED = "audit_failed"
    TESTS_FAILED = "tests_failed"
    INFRASTRUCTURE_FAILED = "infrastructure_failed"
    TIMEOUT = "timeout"
    NO_TEST_COMMAND = "no_test_command"


@dataclass
class VerificationPlan:
    """Captured from the baseline workspace before any patch is applied."""
    test_command: str
    working_directory: str
    test_inventory: dict[str, str]  # filepath -> hash
    config_file_hashes: dict[str, str] # filepath -> hash
    baseline_test_count: int
    baseline_skip_count: int
    test_framework: str | None = None
    build_command: str | None = None
    typecheck_command: str | None = None
    lint_command: str | None = None


@dataclass
class VerificationResult:
    """Authenticated result from the execution sandbox."""
    attempt_id: uuid.UUID
    nonce: str
    snapshot_hash: str
    patch_hash: str
    baseline_exit_code: int
    patched_exit_code: int
    patched_test_count: int
    patched_skip_count: int
    audit_passed: bool
    audit_failure_reasons: list[str]
    result_classification: ResultClass
    stdout_hash: str
    stderr_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class VerificationRun:
    """Structured result of running baseline and patched verification."""
    id: uuid.UUID
    campaign_id: uuid.UUID
    patch_artifact_id: uuid.UUID
    verification_plan: VerificationPlan | None = None
    sandbox_task_id: str | None = None
    state: VerificationState = VerificationState.QUEUED
    result: VerificationResult | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
