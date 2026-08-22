"""Celery tasks for migration."""
import uuid
from typing import Any

from api_guardian.workers.celery_app import app
from api_guardian.application.use_cases.generate_migration import GenerateMigrationUseCase
from api_guardian.reasoning.patch_generator import PatchGenerator
from api_guardian.domain import TenantContext


class MockLLMGateway:
    """Mock LLM Gateway for MVP task instantiation."""
    def generate_completion(self, *args: Any, **kwargs: Any) -> tuple[str, int, int]:
        return "```diff\n--- a\n+++ b\n```", 0, 0
    def generate_structured(self, *args: Any, **kwargs: Any) -> tuple[dict[str, Any], int, int]:
        return {}, 0, 0


@app.task  # type: ignore[untyped-decorator]
def generate_migration_task(tenant_id: str, case_id: str) -> None:
    ctx = TenantContext(tenant_id=uuid.UUID(tenant_id))
    
    # Normally these would be injected
    class MockCaseRepo:
        def get_by_id(self, *args: Any, **kwargs: Any) -> Any:
            pass
        def save(self, *args: Any, **kwargs: Any) -> None:
            pass
            
    use_case = GenerateMigrationUseCase(
        case_repo=MockCaseRepo(),
        patch_generator=PatchGenerator(llm_gateway=MockLLMGateway())  # type: ignore
    )
    use_case.execute(ctx, uuid.UUID(case_id))
