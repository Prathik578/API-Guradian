"""Organization and Member Management routes."""
import uuid
from typing import cast
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import OrganizationModel, OrganizationMemberModel, UserModel
from api_guardian.api.schemas import OrganizationResponse, UserResponse
from api_guardian.api.dependencies import require_owner, require_admin, require_member, require_viewer
from pydantic import BaseModel

router = APIRouter()

class MemberResponse(BaseModel):
    id: uuid.UUID
    user: UserResponse
    role: str
    created_at: str | None = None

class InviteRequest(BaseModel):
    email: str
    role: str

class UpdateRoleRequest(BaseModel):
    role: str

@router.get("/", response_model=OrganizationResponse)
def get_organization(ctx: TenantContext = Depends(require_viewer)) -> OrganizationResponse:
    with db_manager.get_tenant_session(ctx) as session:
        org = session.get(OrganizationModel, ctx.tenant_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            account_type=org.account_type,
            created_at=str(org.created_at) if org.created_at else None
        )

class UpdateOrganizationRequest(BaseModel):
    name: str

@router.patch("/", response_model=OrganizationResponse)
def update_organization(request: UpdateOrganizationRequest, ctx: TenantContext = Depends(require_owner)) -> OrganizationResponse:
    with db_manager.get_tenant_session(ctx) as session:
        org = session.get(OrganizationModel, ctx.tenant_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
            
        org.name = request.name
        session.commit()
        session.refresh(org)
        
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            account_type=org.account_type,
            created_at=str(org.created_at) if org.created_at else None
        )

@router.get("/members", response_model=list[MemberResponse])
def list_members(ctx: TenantContext = Depends(require_viewer)) -> list[MemberResponse]:
    with db_manager.get_tenant_session(ctx) as session:
        members = session.execute(
            select(OrganizationMemberModel).where(OrganizationMemberModel.organization_id == ctx.tenant_id)
        ).scalars().all()
        
        result = []
        for mem in members:
            user = session.get(UserModel, mem.user_id)
            if user:
                result.append(MemberResponse(
                    id=mem.id,
                    user=UserResponse(
                        id=user.id,
                        email=user.email,
                        name=user.name,
                        auth_provider=user.auth_provider,
                        mfa_enabled=user.mfa_enabled,
                        created_at=str(user.created_at) if user.created_at else None
                    ),
                    role=mem.role,
                    created_at=str(mem.created_at) if mem.created_at else None
                ))
        return result

@router.post("/members", response_model=MemberResponse)
def invite_member(request: InviteRequest, ctx: TenantContext = Depends(require_admin)) -> MemberResponse:
    if request.role not in ["OWNER", "ADMIN", "MEMBER", "VIEWER"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    with db_manager.SessionLocal() as session:
        user = session.execute(select(UserModel).where(UserModel.email == request.email)).scalars().first()
        if not user:
            # For MVP, auto-create user placeholder
            user = UserModel(email=request.email, name="Invited User", auth_provider="pending", auth_provider_id=f"pending_{uuid.uuid4()}")
            session.add(user)
            session.flush()
            
        existing = session.execute(
            select(OrganizationMemberModel).where(
                OrganizationMemberModel.organization_id == ctx.tenant_id,
                OrganizationMemberModel.user_id == user.id
            )
        ).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="User already in organization")
            
        member = OrganizationMemberModel(
            organization_id=ctx.tenant_id,
            user_id=user.id,
            role=request.role
        )
        session.add(member)
        session.commit()
        session.refresh(member)
        
        return MemberResponse(
            id=member.id,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                auth_provider=user.auth_provider,
                mfa_enabled=user.mfa_enabled,
                created_at=str(user.created_at) if user.created_at else None
            ),
            role=member.role,
            created_at=str(member.created_at) if member.created_at else None
        )

@router.delete("/members/{member_id}")
def remove_member(member_id: uuid.UUID, ctx: TenantContext = Depends(require_admin)) -> dict[str, str]:
    with db_manager.SessionLocal() as session:
        member = session.execute(
            select(OrganizationMemberModel).where(
                OrganizationMemberModel.id == member_id,
                OrganizationMemberModel.organization_id == ctx.tenant_id
            )
        ).scalars().first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if member.user_id == ctx.user_id:
            raise HTTPException(status_code=400, detail="Cannot remove yourself")
        if member.role == "OWNER" and ctx.role != "OWNER":
            raise HTTPException(status_code=403, detail="Admins cannot remove Owners")
            
        session.delete(member)
        session.commit()
        return {"status": "success"}

@router.patch("/members/{member_id}/role")
def update_role(member_id: uuid.UUID, request: UpdateRoleRequest, ctx: TenantContext = Depends(require_owner)) -> dict[str, str]:
    if request.role not in ["OWNER", "ADMIN", "MEMBER", "VIEWER"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    with db_manager.SessionLocal() as session:
        member = session.execute(
            select(OrganizationMemberModel).where(
                OrganizationMemberModel.id == member_id,
                OrganizationMemberModel.organization_id == ctx.tenant_id
            )
        ).scalars().first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
            
        if member.user_id == ctx.user_id and request.role != "OWNER" and member.role == "OWNER":
            from sqlalchemy import func
            owners_count = session.execute(
                select(func.count()).select_from(OrganizationMemberModel).where(
                    OrganizationMemberModel.organization_id == ctx.tenant_id,
                    OrganizationMemberModel.role == "OWNER"
                )
            ).scalar()
            if owners_count is None or owners_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot demote the last owner")
        
        member.role = request.role
        session.commit()
        return {"status": "success"}
