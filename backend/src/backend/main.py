"""SmartCity Explorer — FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes_projects import router as projects_router
from backend.api.routes_experiences import router as experiences_router
from backend.api.routes_certifications import router as certifications_router
from backend.api.routes_technologies import router as technologies_router
from backend.api.routes_education import router as education_router
from backend.api.routes_hobbies import router as hobbies_router
from backend.api.routes_contact import router as contact_router
from backend.core.config import get_settings
from backend.core.logging import setup_logging
from backend.db.neo4j import close_neo4j
from backend.models import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    await close_neo4j()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API du portfolio — gestion des projets, expériences, certifications, technologies, parcours et contact",
    lifespan=lifespan,
)

# CORS — permet au frontend Streamlit d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Error handlers ─────────────────────────────────────────────
@app.exception_handler(NotImplementedError)
async def not_implemented_handler(request: Request, exc: NotImplementedError):
    return JSONResponse(
        status_code=501,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Catch-all : erreurs non gérées → 500 propre (ex. DB indisponible)."""
    import logging

    logging.getLogger("backend").error("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ── Routes ─────────────────────────────────────────────────────
app.include_router(projects_router)
app.include_router(experiences_router)
app.include_router(certifications_router)
app.include_router(technologies_router)
app.include_router(education_router)
app.include_router(hobbies_router)
app.include_router(contact_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    """Health check."""
    return HealthResponse(status="ok", version=settings.app_version)
