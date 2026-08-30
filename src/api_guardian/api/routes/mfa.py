"""MFA routes."""
import pyotp
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from pydantic import BaseModel

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import UserModel
from api_guardian.api.dependencies import require_member

router = APIRouter()

class MFAEnableResponse(BaseModel):
    secret: str
    uri: str

class MFAVerifyRequest(BaseModel):
    code: str

@router.post("/enable", response_model=MFAEnableResponse)
def enable_mfa(ctx: TenantContext = Depends(require_member)) -> MFAEnableResponse:
    if not ctx.user_id:
        raise HTTPException(status_code=401, detail="User required")
        
    with db_manager.SessionLocal() as session:
        user = session.get(UserModel, ctx.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA already enabled")
            
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        session.commit()
        
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="API Guardian")
        return MFAEnableResponse(secret=secret, uri=uri)

@router.post("/verify")
def verify_mfa(request: MFAVerifyRequest, ctx: TenantContext = Depends(require_member)) -> dict[str, str]:
    if not ctx.user_id:
        raise HTTPException(status_code=401, detail="User required")
        
    with db_manager.SessionLocal() as session:
        user = session.get(UserModel, ctx.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not user.mfa_secret:
            raise HTTPException(status_code=400, detail="MFA not setup")
            
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(request.code):
            raise HTTPException(status_code=400, detail="Invalid MFA code")
            
        user.mfa_enabled = True
        session.commit()
        return {"status": "success"}

@router.post("/disable")
def disable_mfa(request: MFAVerifyRequest, ctx: TenantContext = Depends(require_member)) -> dict[str, str]:
    if not ctx.user_id:
        raise HTTPException(status_code=401, detail="User required")
        
    with db_manager.SessionLocal() as session:
        user = session.get(UserModel, ctx.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not user.mfa_enabled or not user.mfa_secret:
            raise HTTPException(status_code=400, detail="MFA is not enabled")
            
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(request.code):
            raise HTTPException(status_code=400, detail="Invalid MFA code")
            
        user.mfa_enabled = False
        user.mfa_secret = None
        session.commit()
        return {"status": "success"}
