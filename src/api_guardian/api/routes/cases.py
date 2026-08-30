"""Maintenance Cases routes."""

import uuid
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select

from api_guardian.api.schemas import (
    ActionResponse,
    MaintenanceCaseDetailResponse,
    MaintenanceCaseResponse,
    MigrationAttemptResponse,
    PaginatedResponse,
    VerificationRunResponse,
)
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import (
    MaintenanceCaseModel,
    MigrationAttemptModel,
    MigrationCampaignModel,
    VerificationRunModel,
)
from api_guardian.persistence.outbox import OutboxManager

router = APIRouter()

def get_tenant_context(request: Request) -> TenantContext:
    if not hasattr(request.state, "tenant") or not request.state.tenant:
        raise HTTPException(status_code=401, detail="Tenant context required")
    return cast(TenantContext, request.state.tenant)


@router.get("/", response_model=PaginatedResponse[MaintenanceCaseResponse])
async def list_cases(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(get_tenant_context)
) -> PaginatedResponse[MaintenanceCaseResponse]:
    """List active cases for the tenant."""
    with db_manager.get_tenant_session(ctx) as session:
        total = session.execute(select(func.count()).select_from(MaintenanceCaseModel)).scalar() or 0
        
        stmt = select(MaintenanceCaseModel).order_by(MaintenanceCaseModel.created_at.desc()).offset((page - 1) * size).limit(size)
        cases = session.execute(stmt).scalars().all()
        
        items = [
            MaintenanceCaseResponse(
                id=c.id,
                repository_id=c.repository_id,
                provider_change_id=c.provider_change_id,
                state=c.state.name,
                created_at=str(c.created_at) if c.created_at else None
            )
            for c in cases
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)


@router.get("/{case_id}", response_model=MaintenanceCaseDetailResponse)
async def get_case(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> MaintenanceCaseDetailResponse:
    """Get a specific case."""
    with db_manager.get_tenant_session(ctx) as session:
        c = session.get(MaintenanceCaseModel, case_id)
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")
        return MaintenanceCaseDetailResponse(
            id=c.id,
            repository_id=c.repository_id,
            provider_change_id=c.provider_change_id,
            base_revision_sha=c.base_revision_sha,
            state=c.state.name,
            created_at=str(c.created_at) if c.created_at else None
        )


@router.get("/{case_id}/migrations", response_model=list[MigrationAttemptResponse])
async def list_case_migrations(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> list[MigrationAttemptResponse]:
    """List migration attempts for a case."""
    with db_manager.get_tenant_session(ctx) as session:
        c = session.get(MaintenanceCaseModel, case_id)
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")
            
        stmt = (
            select(MigrationAttemptModel)
            .join(MigrationCampaignModel, MigrationAttemptModel.campaign_id == MigrationCampaignModel.id)
            .where(MigrationCampaignModel.case_id == case_id)
            .order_by(MigrationAttemptModel.created_at.desc())
        )
        attempts = session.execute(stmt).scalars().all()
        
        return [
            MigrationAttemptResponse(
                id=a.id,
                campaign_id=a.campaign_id,
                patch_artifact_id=a.patch_artifact_id,
                model_name=a.model_name,
                error_reason=a.error_reason,
                created_at=str(a.created_at) if a.created_at else None
            )
            for a in attempts
        ]


@router.get("/{case_id}/verifications", response_model=list[VerificationRunResponse])
async def list_case_verifications(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> list[VerificationRunResponse]:
    """List verification runs for a case."""
    with db_manager.get_tenant_session(ctx) as session:
        c = session.get(MaintenanceCaseModel, case_id)
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")
            
        stmt = (
            select(VerificationRunModel)
            .join(MigrationCampaignModel, VerificationRunModel.campaign_id == MigrationCampaignModel.id)
            .where(MigrationCampaignModel.case_id == case_id)
            .order_by(VerificationRunModel.created_at.desc())
        )
        runs = session.execute(stmt).scalars().all()
        
        return [
            VerificationRunResponse(
                id=r.id,
                campaign_id=r.campaign_id,
                patch_artifact_id=r.patch_artifact_id,
                state=r.state.name,
                audit_passed=r.audit_passed,
                created_at=str(r.created_at) if r.created_at else None
            )
            for r in runs
        ]


@router.post("/{case_id}/assess_impact", response_model=ActionResponse)
async def assess_impact(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> ActionResponse:
    """Asynchronously triggers impact assessment."""
    with db_manager.get_tenant_session(ctx) as session:
        c = session.get(MaintenanceCaseModel, case_id)
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")
        
        from api_guardian.persistence.models.tables import SnapshotModel
        stmt = select(SnapshotModel).where(SnapshotModel.repository_id == c.repository_id).order_by(SnapshotModel.created_at.desc()).limit(1)
        latest_snapshot = session.execute(stmt).scalars().first()
        if not latest_snapshot:
            raise HTTPException(status_code=400, detail="No snapshot found for repository")
            
        OutboxManager.schedule_task(
            session,
            "api_guardian.workers.tasks.analysis.assess_impact_task",
            {"tenant_id": str(ctx.tenant_id), "case_id": str(case_id), "snapshot_id": str(latest_snapshot.id)}
        )
    return ActionResponse(status="queued")


@router.post("/{case_id}/generate_migration", response_model=ActionResponse)
async def trigger_migration(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> ActionResponse:
    """Asynchronously triggers migration generation."""
    with db_manager.get_tenant_session(ctx) as session:
        c = session.get(MaintenanceCaseModel, case_id)
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")
            
        OutboxManager.schedule_task(
            session,
            "api_guardian.workers.tasks.migration.generate_migration_task",
            {"tenant_id": str(ctx.tenant_id), "case_id": str(case_id)}
        )
    return ActionResponse(status="queued")


@router.post("/{case_id}/verify", response_model=ActionResponse)
async def trigger_verification(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> ActionResponse:
    """Asynchronously triggers sandbox verification."""
    with db_manager.get_tenant_session(ctx) as session:
        c = session.get(MaintenanceCaseModel, case_id)
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")
            
        OutboxManager.schedule_task(
            session,
            "api_guardian.workers.tasks.verification.execute_verification_task",
            {"tenant_id": str(ctx.tenant_id), "case_id": str(case_id)}
        )
    return ActionResponse(status="queued")
