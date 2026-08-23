"""Use case for executing verification in a sandbox."""

import secrets
import uuid

from api_guardian.application.interfaces import MaintenanceCaseRepository, VerificationRepository
from api_guardian.application.interfaces.sandbox import SandboxOrchestrator
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.domain.verification import VerificationRun, VerificationState


class ExecuteVerificationUseCase:
    """Prepares VerificationPlan, launches sandbox, handles signed result."""

    def __init__(
        self, 
        verification_repo: VerificationRepository, 
        case_repo: MaintenanceCaseRepository, 
        sandbox_orchestrator: SandboxOrchestrator
    ) -> None:
        self.verification_repo = verification_repo
        self.case_repo = case_repo
        self.sandbox_orchestrator = sandbox_orchestrator

    def execute(self, ctx: TenantContext, case_id: uuid.UUID) -> str:
        """Kicks off a verification sandbox task."""

        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        case.transition_to(MaintenanceCaseState.VERIFYING)
        self.case_repo.save(ctx, case)

        attempt_id = uuid.uuid4()
        nonce = secrets.token_urlsafe(32)
        signing_secret = secrets.token_hex(64)

        task_id = self.sandbox_orchestrator.launch_verification_task(
            attempt_id=attempt_id,
            snapshot_url="https://s3.mock/snapshot.tar.gz",
            patch_url="https://s3.mock/patch.json",
            result_url="https://s3.mock/result_endpoint",
            expected_snapshot_hash="mock_hash",
            expected_patch_hash="mock_hash",
            nonce=nonce,
            signing_secret=signing_secret,
        )
        
        # In a real scenario we'd query the migration campaign to get patch_artifact_id
        # For MVP we mock the campaign id and patch id
        run = VerificationRun(
            id=uuid.uuid4(),
            campaign_id=uuid.uuid4(),
            patch_artifact_id=uuid.uuid4(),
            sandbox_task_id=task_id,
            state=VerificationState.QUEUED,
        )
        self.verification_repo.save_run(ctx, run)

        return task_id
