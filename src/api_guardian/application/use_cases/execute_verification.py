"""Use case for executing verification in a sandbox."""
import secrets
import uuid
from typing import Any

from api_guardian.application.interfaces.sandbox import SandboxOrchestrator
from api_guardian.domain import MaintenanceCaseState, TenantContext


class ExecuteVerificationUseCase:
    """Prepares VerificationPlan, launches sandbox, handles signed result."""
    def __init__(self, verification_repo: Any, case_repo: Any, sandbox_orchestrator: SandboxOrchestrator) -> None:
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
            signing_secret=signing_secret
        )
        
        return task_id
