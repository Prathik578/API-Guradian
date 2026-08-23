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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TenantIdentificationMiddleware)

    app.include_router(health.router, prefix="/health", tags=["system"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["github"])
    app.include_router(cases.router, prefix="/api/v1/cases", tags=["cases"])

    return app


app = create_app()
