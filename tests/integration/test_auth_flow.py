import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Any

from api_guardian.api.app import app
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.base import Base

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_db():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(test_engine)
    db_manager.engine = test_engine
    db_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def test_full_auth_signup_onboarding_login_flow():
    test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    test_name = "Test Developer"
    
    # 1. Signup
    signup_res = client.post("/api/v1/auth/signup", json={
        "name": test_name,
        "email": test_email,
        "password": test_password,
        "confirm_password": test_password
    })
    assert signup_res.status_code == 200
    data = signup_res.json()
    assert "token" in data
    user_id = data["user"]["id"]
    token = data["token"]
    assert data["organizations"] == []

    # 2. Onboarding
    onboard_res = client.post(
        f"/api/v1/auth/onboarding?user_id={user_id}",
        json={
            "account_type": "PERSONAL",
            "organization_name": "My Primary Workspace"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert onboard_res.status_code == 200
    org_data = onboard_res.json()
    org_id = org_data["id"]
    assert org_data["name"] == "My Primary Workspace"

    # 3. Existing User Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["token"] != ""
    assert len(login_data["organizations"]) == 1
    assert login_data["organizations"][0]["id"] == org_id

    # 4. Authenticated Dashboard Overview Access
    dashboard_res = client.get(
        "/api/v1/analytics/overview",
        headers={
            "Authorization": f"Bearer {login_data['token']}",
            "X-Tenant-ID": org_id
        }
    )
    assert dashboard_res.status_code == 200
    overview = dashboard_res.json()
    assert "active_repositories" in overview
    assert "active_cases" in overview
    assert "pending_api_changes" in overview

def test_invalid_credentials():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert login_res.status_code == 401
    assert login_res.json()["detail"] == "Invalid email or password"

def test_unauthenticated_protected_route_access():
    dashboard_res = client.get("/api/v1/analytics/overview")
    assert dashboard_res.status_code == 401

def test_tenant_isolation():
    # Create User A with Org A
    email_a = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    signup_a = client.post("/api/v1/auth/signup", json={
        "name": "User A",
        "email": email_a,
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token_a = signup_a["token"]
    user_a_id = signup_a["user"]["id"]
    
    org_a = client.post(
        f"/api/v1/auth/onboarding?user_id={user_a_id}",
        json={"account_type": "PERSONAL", "organization_name": "Org A"},
        headers={"Authorization": f"Bearer {token_a}"}
    ).json()

    # Create User B with Org B
    email_b = f"user_b_{uuid.uuid4().hex[:8]}@example.com"
    signup_b = client.post("/api/v1/auth/signup", json={
        "name": "User B",
        "email": email_b,
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).json()
    token_b = signup_b["token"]
    user_b_id = signup_b["user"]["id"]

    org_b = client.post(
        f"/api/v1/auth/onboarding?user_id={user_b_id}",
        json={"account_type": "PERSONAL", "organization_name": "Org B"},
        headers={"Authorization": f"Bearer {token_b}"}
    ).json()

    # User B attempts to access Org A with Org A's tenant ID
    res = client.get(
        "/api/v1/analytics/overview",
        headers={
            "Authorization": f"Bearer {token_b}",
            "X-Tenant-ID": org_a["id"]
        }
    )
    assert res.status_code in (401, 403)
