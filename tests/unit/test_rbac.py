import uuid

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import api_guardian.persistence.database as db_mod
from api_guardian.api.dependencies import (
    require_admin,
    require_member,
    require_owner,
    require_viewer,
)
from api_guardian.api.middleware import TenantIdentificationMiddleware
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import DatabaseManager
from api_guardian.persistence.models.base import Base
from api_guardian.persistence.models.tables import (
    OrganizationMemberModel,
    OrganizationModel,
    UserModel,
)

try:
    from testcontainers.postgres import PostgresContainer
    HAS_TESTCONTAINERS = True
except ImportError:
    HAS_TESTCONTAINERS = False

app = FastAPI()
app.add_middleware(TenantIdentificationMiddleware)

@app.get("/owner")
def owner_route(ctx: TenantContext = Depends(require_owner)):
    return {"status": "ok"}

@app.get("/admin")
def admin_route(ctx: TenantContext = Depends(require_admin)):
    return {"status": "ok"}

@app.get("/member")
def member_route(ctx: TenantContext = Depends(require_member)):
    return {"status": "ok"}

@app.get("/viewer")
def viewer_route(ctx: TenantContext = Depends(require_viewer)):
    return {"status": "ok"}

client = TestClient(app)

@pytest.fixture(scope="module")
def postgres_db():
    if not HAS_TESTCONTAINERS:
        pytest.skip("Testcontainers not available")
    with PostgresContainer("postgres:15-alpine") as postgres:
        db_url = postgres.get_connection_url().replace("+psycopg2", "")
        test_db_manager = DatabaseManager(db_url)
        Base.metadata.create_all(test_db_manager.engine)
        
        # Patch the global db_manager for the tests
        old_manager = db_mod.db_manager
        db_mod.db_manager = test_db_manager
        
        yield test_db_manager
        
        db_mod.db_manager = old_manager

def create_user_and_org(session, role: str):
    user = UserModel(email=f"{uuid.uuid4()}@test.com", name="Test", auth_provider="local", auth_provider_id=str(uuid.uuid4()))
    session.add(user)
    session.flush()
    
    org = OrganizationModel(name="Test Org", account_type="ENTERPRISE")
    session.add(org)
    session.flush()
    
    member = OrganizationMemberModel(organization_id=org.id, user_id=user.id, role=role)
    session.add(member)
    session.commit()
    
    token = jwt.encode({"sub": str(user.id)}, "dev_secret_key", algorithm="HS256")
    return org.id, token

def test_rbac_owner(postgres_db):
    with postgres_db.SessionLocal() as session:
        org_id, token = create_user_and_org(session, "OWNER")
    headers = {"X-Tenant-ID": str(org_id), "Authorization": f"Bearer {token}"}
    
    assert client.get("/owner", headers=headers).status_code == 200
    assert client.get("/admin", headers=headers).status_code == 200
    assert client.get("/member", headers=headers).status_code == 200
    assert client.get("/viewer", headers=headers).status_code == 200

def test_rbac_member(postgres_db):
    with postgres_db.SessionLocal() as session:
        org_id, token = create_user_and_org(session, "MEMBER")
    headers = {"X-Tenant-ID": str(org_id), "Authorization": f"Bearer {token}"}
    
    assert client.get("/owner", headers=headers).status_code == 403
    assert client.get("/admin", headers=headers).status_code == 403
    assert client.get("/member", headers=headers).status_code == 200
    assert client.get("/viewer", headers=headers).status_code == 200

def test_rbac_no_auth(postgres_db):
    with postgres_db.SessionLocal() as session:
        org_id, _ = create_user_and_org(session, "OWNER")
    headers = {"X-Tenant-ID": str(org_id)}
    
    assert client.get("/owner", headers=headers).status_code == 403
    assert client.get("/viewer", headers=headers).status_code == 403
