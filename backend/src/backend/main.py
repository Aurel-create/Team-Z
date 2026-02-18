"""SmartCity Explorer — FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes_cities import router as cities_router
from backend.api.routes_reviews import router as reviews_router
from backend.api.routes_reco import router as reco_router
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
    description="API pour explorer et comparer les villes françaises",
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
app.include_router(cities_router)
app.include_router(reviews_router)
app.include_router(reco_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    """Health check."""
    return HealthResponse(status="ok", version=settings.app_version)
