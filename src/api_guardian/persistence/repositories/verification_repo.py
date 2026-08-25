"""Concrete implementation of VerificationRepository."""
import uuid

from api_guardian.application.interfaces import VerificationRepository
from api_guardian.domain import TenantContext, VerificationRun
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import VerificationRunModel


class SQLVerificationRepository(VerificationRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_run(self, ctx: TenantContext, run_id: uuid.UUID) -> VerificationRun | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(VerificationRunModel, run_id)
            if not model:
                return None
            
            # Simple cast for MVP
            from api_guardian.domain.verification import VerificationPlan, VerificationResult
            
            plan = None
            if model.verification_plan:
                plan = VerificationPlan(**dict(model.verification_plan))
                
            result = None
            if model.result_data:
                r_dict = dict(model.result_data)
                # Need to convert uuid strings back for MVP
                if "attempt_id" in r_dict and isinstance(r_dict["attempt_id"], str):
                    r_dict["attempt_id"] = uuid.UUID(r_dict["attempt_id"])
                result = VerificationResult(**r_dict)
            
            return VerificationRun(
                id=model.id,
                campaign_id=model.campaign_id,
                patch_artifact_id=model.patch_artifact_id,
                sandbox_task_id=model.sandbox_task_id,
                state=model.state,
                verification_plan=plan,
                result=result,
                signing_secret=model.signing_secret,
                nonce=model.nonce,
            )

    def save_run(self, ctx: TenantContext, run: VerificationRun) -> None:
        import dataclasses
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(VerificationRunModel, run.id)
            if not model:
                model = VerificationRunModel(
                    id=run.id,
                    organization_id=ctx.tenant_id,
                    campaign_id=run.campaign_id,
                    patch_artifact_id=run.patch_artifact_id,
                )
                session.add(model)
            model.sandbox_task_id = run.sandbox_task_id
            model.state = run.state
            model.signing_secret = run.signing_secret
            model.nonce = run.nonce
            
            if run.verification_plan:
                model.verification_plan = dataclasses.asdict(run.verification_plan)
            
            if run.result:
                # Use dict() cast to break Pyright's strict TypedDict inference from asdict
                r_dict = dict(dataclasses.asdict(run.result))
                r_dict["attempt_id"] = str(r_dict["attempt_id"])
                r_dict["timestamp"] = r_dict["timestamp"].isoformat()
                model.result_data = r_dict
