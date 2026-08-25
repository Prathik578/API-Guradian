"""Concrete implementation of MigrationRepository."""
import uuid

from api_guardian.application.interfaces import MigrationRepository
from api_guardian.domain import MigrationCampaign, TenantContext
from api_guardian.domain.migration import MigrationAttempt, PatchArtifact
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.tables import (
    MigrationAttemptModel,
    MigrationCampaignModel,
    PatchArtifactModel,
)


class SQLMigrationRepository(MigrationRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_campaign(self, ctx: TenantContext, campaign_id: uuid.UUID) -> MigrationCampaign | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(MigrationCampaignModel, campaign_id)
            if not model:
                return None
            
            return MigrationCampaign(
                id=model.id,
                case_id=model.case_id,
                state=model.state,
            )

    def save_campaign(self, ctx: TenantContext, campaign: MigrationCampaign) -> None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(MigrationCampaignModel, campaign.id)
            if not model:
                model = MigrationCampaignModel(
                    id=campaign.id,
                    organization_id=ctx.tenant_id,
                    case_id=campaign.case_id,
                )
                session.add(model)
            model.state = campaign.state

    def get_latest_campaign(
        self, ctx: TenantContext, case_id: uuid.UUID
    ) -> MigrationCampaign | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            from sqlalchemy import select
            model = session.scalar(
                select(MigrationCampaignModel)
                .where(MigrationCampaignModel.case_id == case_id)
                .order_by(MigrationCampaignModel.created_at.desc())
                .limit(1)
            )
            if not model:
                return None
            return MigrationCampaign(
                id=model.id,
                case_id=model.case_id,
                state=model.state,
            )

    def save_patch(self, ctx: TenantContext, patch: "PatchArtifact") -> None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(PatchArtifactModel, patch.id)
            if not model:
                model = PatchArtifactModel(
                    id=patch.id,
                    organization_id=ctx.tenant_id,
                    repository_id=patch.repository_id,
                    base_commit_sha=patch.base_commit_sha,
                    archive_content_hash=patch.archive_content_hash,
                    affected_files=patch.affected_files,
                    patch_data=patch.patch_data,
                )
                session.add(model)
            # patch is immutable, no updates needed

    def save_attempt(self, ctx: TenantContext, attempt: "MigrationAttempt") -> None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(MigrationAttemptModel, attempt.id)
            if not model:
                model = MigrationAttemptModel(
                    id=attempt.id,
                    organization_id=ctx.tenant_id,
                    campaign_id=attempt.campaign_id,
                    patch_artifact_id=attempt.patch_artifact_id,
                    model_name=attempt.model_name,
                    prompt_tokens=attempt.prompt_tokens,
                    completion_tokens=attempt.completion_tokens,
                )
                session.add(model)

    def get_latest_attempt_for_case(self, ctx: TenantContext, case_id: uuid.UUID) -> MigrationAttempt | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            # For MVP, just get the latest attempt joining on campaign where case_id matches
            # This is simple using SQLAlchemy select
            from sqlalchemy import select
            stmt = (
                select(MigrationAttemptModel)
                .join(MigrationCampaignModel)
                .where(MigrationCampaignModel.case_id == case_id)
                .order_by(MigrationAttemptModel.created_at.desc())
                .limit(1)
            )
            model = session.scalar(stmt)
            if not model:
                return None
            return MigrationAttempt(
                id=model.id,
                campaign_id=model.campaign_id,
                model_name=model.model_name,
                prompt_tokens=model.prompt_tokens,
                completion_tokens=model.completion_tokens,
                patch_artifact_id=model.patch_artifact_id,
                error_reason=model.error_reason,
            )

    def get_patch(self, ctx: TenantContext, patch_id: uuid.UUID) -> PatchArtifact | None:
        with self.db_manager.get_tenant_session(ctx) as session:
            model = session.get(PatchArtifactModel, patch_id)
            if not model:
                return None
            return PatchArtifact(
                id=model.id,
                repository_id=model.repository_id,
                base_commit_sha=model.base_commit_sha,
                archive_content_hash=model.archive_content_hash,
                affected_files=list(model.affected_files),
                patch_data=model.patch_data,
                patch_hash=model.patch_hash,
                pre_image_hashes=dict(model.pre_image_hashes) if model.pre_image_hashes else None,
            )
