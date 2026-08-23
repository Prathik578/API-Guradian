"""Celery tasks for verification."""
import uuid
from typing import Any

from api_guardian.application.use_cases.execute_verification import ExecuteVerificationUseCase
from api_guardian.domain import TenantContext
from api_guardian.sandbox.orchestrator import FargateSandboxOrchestrator
from api_guardian.workers.celery_app import app


@app.task  # type: ignore[untyped-decorator]
def execute_verification_task(tenant_id: str, case_id: str) -> None:
    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    
    class MockCaseRepo:
        def get_by_id(self, *args: Any, **kwargs: Any) -> Any:
            pass
        def save(self, *args: Any, **kwargs: Any) -> None:
            pass
            
    sandbox = FargateSandboxOrchestrator(
        cluster_name="api-guardian-cluster",
        task_definition="api-guardian-bootstrap",
        subnets=["subnet-123"],
        security_groups=["sg-123"]
    )
    
    use_case = ExecuteVerificationUseCase(
        verification_repo=None,
        case_repo=MockCaseRepo(),
        sandbox_orchestrator=sandbox
    )
    use_case.execute(ctx, uuid.UUID(case_id))
