"""FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware import TenantIdentificationMiddleware
from .routes import cases, health, webhooks


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Guardian",
        description="Autonomous API maintenance control plane",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TenantIdentificationMiddleware)

    app.include_router(health.router, prefix="/health", tags=["system"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["github"])
    app.include_router(cases.router, prefix="/api/v1/cases", tags=["cases"])
    
    from .routes import dashboard, provider_changes, repositories, auth, integrations, guarded_apis, notices, pull_requests, activity, organizations, usage, notifications, mfa
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
    app.include_router(usage.router, prefix="/api/v1/usage", tags=["usage"])
    app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
    app.include_router(mfa.router, prefix="/api/v1/mfa", tags=["mfa"])
    app.include_router(repositories.router, prefix="/api/v1/repositories", tags=["repositories"])
    app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
    app.include_router(guarded_apis.router, prefix="/api/v1/apis", tags=["apis"])
    app.include_router(notices.router, prefix="/api/v1/notices", tags=["notices"])
    app.include_router(pull_requests.router, prefix="/api/v1/pull-requests", tags=["pull-requests"])
    app.include_router(activity.router, prefix="/api/v1/activity", tags=["activity"])
    app.include_router(dashboard.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(provider_changes.router, prefix="/api/v1/provider-changes", tags=["provider-changes"])

    return app


app = create_app()
