from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.core.config import settings
from app.api import (
    auth,
    users,
    environments,
    features,
    user_targeting,
    evaluation,
    audit,
    dashboard,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Centralized platform for managing feature flags, environment-specific configuration, gradual rollouts, user targeting, audit logging and analytics.",
    openapi_tags=[
        {"name": "Authentication", "description": "JWT authentication and current-user operations."},
        {"name": "Users", "description": "User and role administration."},
        {"name": "Environments", "description": "Development, testing and production environments."},
        {"name": "Feature Flags", "description": "Feature creation, environment rollouts and rollback."},
        {"name": "User Targeting", "description": "Assign specific users to feature flags and manage targeted access."},
        {"name": "Evaluation", "description": "Evaluate a feature for a user and environment."},
        {"name": "Audit Logs", "description": "Change history and feature evaluation events."},
        {"name": "Dashboard & Analytics", "description": "Platform and feature usage statistics."},
        {"name": "Health", "description": "Service health endpoints."},
    ],
)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(environments.router)
app.include_router(features.router)
app.include_router(user_targeting.router)
app.include_router(evaluation.router)
app.include_router(audit.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"], summary="Root")
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["Health"], summary="Health")
def health():
    return {"status": "healthy", "service": "feature-flag-system"}
