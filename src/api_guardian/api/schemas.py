"""Pydantic schemas for API requests and responses."""
import uuid
from typing import Generic, TypeVar, Any

from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int

class RepositoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    github_full_name: str
    default_branch: str
    created_at: str | None = None

class CreateRepositoryRequest(BaseModel):
    name: str
    github_full_name: str
    default_branch: str = "main"

class DashboardOverviewResponse(BaseModel):
    active_repositories: int
    active_cases: int
    pending_api_changes: int
    migrations_in_progress: int
    open_prs: int
    failed_verifications: int
    recent_notices: int

class ProviderChangeResponse(BaseModel):
    id: uuid.UUID
    provider: str
    classification: str
    summary: str
    effective_date: str | None = None
    sunset_date: str | None = None
    created_at: str | None = None

class ProviderChangeDetailResponse(ProviderChangeResponse):
    affected_entities: list[str]
    revision: int

class MaintenanceCaseResponse(BaseModel):
    id: uuid.UUID
    repository_id: uuid.UUID
    provider_change_id: uuid.UUID
    state: str
    created_at: str | None = None

class MaintenanceCaseDetailResponse(MaintenanceCaseResponse):
    base_revision_sha: str

class MigrationAttemptResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    patch_artifact_id: uuid.UUID
    model_name: str
    error_reason: str | None = None
    created_at: str | None = None

class VerificationRunResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    patch_artifact_id: uuid.UUID
    state: str
    audit_passed: bool | None = None
    created_at: str | None = None

class ActionResponse(BaseModel):
    status: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    auth_provider: str
    mfa_enabled: bool = False
    created_at: str | None = None

class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    account_type: str
    created_at: str | None = None

class AuthRequest(BaseModel):
    email: str
    name: str
    auth_provider: str
    auth_provider_id: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class AuthResponse(BaseModel):
    token: str | None = None
    mfa_token: str | None = None
    mfa_required: bool = False
    user: UserResponse | None = None
    organizations: list[OrganizationResponse] | None = None

class VerifyMFALoginRequest(BaseModel):
    mfa_token: str
    code: str
class IntegrationResponse(BaseModel):
    id: uuid.UUID
    provider: str
    status: str
    last_synced_at: str | None = None
    created_at: str | None = None

class CreateIntegrationRequest(BaseModel):
    provider: str
    configuration: dict[str, Any] | None = None

class GuardedAPIResponse(BaseModel):
    id: uuid.UUID
    integration_id: uuid.UUID
    name: str
    version: str
    status: str
    risk_level: str
    created_at: str | None = None

class CreateGuardedAPIRequest(BaseModel):
    integration_id: uuid.UUID
    name: str
    version: str
    risk_level: str = "LOW"

class ProviderNoticeResponse(BaseModel):
    id: uuid.UUID
    provider: str
    title: str
    description: str
    published_at: str | None = None
    effective_at: str | None = None
    severity: str
    affected_api: str | None = None
    notice_type: str
    status: str
    created_at: str | None = None
class OnboardingRequest(BaseModel):
    account_type: str # PERSONAL or ENTERPRISE
    organization_name: str

class PullRequestResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    repository_id: uuid.UUID
    patch_artifact_id: uuid.UUID
    github_pr_number: int
    github_pr_url: str
    state: str
    created_at: str | None = None

from typing import Any

class ActivityEventResponse(BaseModel):
    id: uuid.UUID
    actor: str
    event_type: str
    entity: str
    entity_id: str
    result: str
    metadata_payload: dict[str, Any] | None = None
    created_at: str | None = None
