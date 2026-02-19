"""Portfolio Data-Driven — FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import get_settings
from backend.core.logging import setup_logging
from backend.database import close_databases
from backend.routers import (
    experiences_router,
    profile_router,
    projects_router,
    skills_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    await close_databases()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend portfolio avec persistance polyglotte MongoDB + Neo4j",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────
app.include_router(projects_router)
app.include_router(experiences_router)
app.include_router(skills_router)
app.include_router(profile_router)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": settings.app_version}
