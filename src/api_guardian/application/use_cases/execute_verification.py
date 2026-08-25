"""Use case for executing verification in a sandbox."""

import secrets
import uuid
from typing import Any

from api_guardian.application.interfaces import MaintenanceCaseRepository, VerificationRepository, MigrationRepository, SnapshotRepository
from api_guardian.application.interfaces.storage import ArtifactStoragePort
from api_guardian.application.interfaces.sandbox import SandboxOrchestrator
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.domain.verification import VerificationRun, VerificationState


class ExecuteVerificationUseCase:
    """Prepares VerificationPlan, launches sandbox, handles signed result."""

    def __init__(
        self, 
        verification_repo: VerificationRepository, 
        case_repo: MaintenanceCaseRepository, 
        migration_repo: MigrationRepository,
        snapshot_repo: SnapshotRepository,
        sandbox_orchestrator: SandboxOrchestrator,
        artifact_storage: ArtifactStoragePort,
    ) -> None:
        self.verification_repo = verification_repo
        self.case_repo = case_repo
        self.migration_repo = migration_repo
        self.snapshot_repo = snapshot_repo
        self.sandbox_orchestrator = sandbox_orchestrator
        self.artifact_storage = artifact_storage

    def execute(self, ctx: TenantContext, case_id: uuid.UUID) -> str:
        """Kicks off a verification sandbox task."""

        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        case.transition_to(MaintenanceCaseState.VERIFYING)
        self.case_repo.save(ctx, case)

        nonce = secrets.token_urlsafe(32)
        signing_secret = secrets.token_hex(64)

        attempt = self.migration_repo.get_latest_attempt_for_case(ctx, case.id)
        if not attempt:
            raise ValueError("No migration attempt found for case")
        
        patch = None
        if attempt.patch_artifact_id:
            patch = self.migration_repo.get_patch(ctx, attempt.patch_artifact_id)
        
        if not patch:
            raise ValueError("No patch artifact found for attempt")
            
        snapshot_url = self.artifact_storage.generate_consumable_input_capability(
            str(ctx.tenant_id), "snapshot", f"{case.repository_id}/{case.base_revision_sha}"
        )
        patch_url = self.artifact_storage.generate_consumable_input_capability(
            str(ctx.tenant_id), "patch", str(patch.id)
        )

        run = VerificationRun(
            id=uuid.uuid4(),
            campaign_id=attempt.campaign_id,
            patch_artifact_id=patch.id,
            sandbox_task_id=None, # Placeholder until task is launched
            state=VerificationState.QUEUED,
            signing_secret=signing_secret,
            nonce=nonce,
        )
        self.verification_repo.save_run(ctx, run)

        task_id = self.sandbox_orchestrator.launch_verification_task(
            attempt_id=run.id,
            snapshot_url=snapshot_url,
            patch_url=patch_url,
            result_url="https://sandbox.internal/result", # TODO: Implement webhook callback url
            expected_snapshot_hash=patch.archive_content_hash,
            expected_patch_hash=patch.patch_hash or "",
            nonce=nonce,
            signing_secret=signing_secret,
            pre_image_hashes=patch.pre_image_hashes or {},
        )

        run.sandbox_task_id = str(task_id) if task_id else None
        self.verification_repo.save_run(ctx, run)

        return task_id

    def handle_result(self, ctx: TenantContext, run_id: uuid.UUID, raw_payload: bytes, signature: str) -> None:
        """Handles the callback from the sandbox."""
        import json
        from api_guardian.sandbox.verification import VerificationPayloadValidator
        run = self.verification_repo.get_run(ctx, run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")

        if not run.signing_secret:
            raise ValueError("No signing secret found for run")

        # Verify signature using robust constant-time validator
        if not VerificationPayloadValidator.verify_signature(raw_payload, signature, run.signing_secret):
            raise ValueError("Invalid webhook signature")
            
        result_data = json.loads(raw_payload)
        
        # Verify nonce and replay protection
        nonce = result_data.get("nonce")
        if not nonce or nonce != run.nonce:
            raise ValueError("Invalid nonce or replay detected")

        baseline_exit = result_data.get("baseline_exit_code")
        patched_exit = result_data.get("patched_exit_code")
        baseline_tests = result_data.get("baseline_test_count", 0)
        patched_tests = result_data.get("patched_test_count", 0)
        config_mutated = result_data.get("config_mutated", False)

        passed = False
        if baseline_exit == 0 and patched_exit == 0 and patched_tests >= baseline_tests and not config_mutated:
            passed = True

        run.audit_passed = passed
        run.state = VerificationState.VERIFIED if passed else VerificationState.TESTS_FAILED
        self.verification_repo.save_run(ctx, run)

        case = self.case_repo.get_by_id(ctx, uuid.UUID(result_data["case_id"]))
        if case:
            if not passed:
                case.transition_to(MaintenanceCaseState.AFFECTED_ACTION_REQUIRED)
                self.case_repo.save(ctx, case)
            # If passed, we do NOT transition to PR_OPEN here.
            # PR creation is handled exclusively by CreatePullRequestUseCase,
            # which enforces all state gating requirements.
            self.case_repo.save(ctx, case)
