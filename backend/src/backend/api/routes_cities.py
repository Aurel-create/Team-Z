"""Routes API — Villes et scores."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.postgres import get_db
from backend.models import CityDetail, CityListResponse, CityScores
from backend.repositories.postgres_repo import PostgresRepository
from backend.services.city_service import CityService

router = APIRouter(prefix="/cities", tags=["cities"])


def _get_service(session: AsyncSession = Depends(get_db)) -> CityService:
    return CityService(repo=PostgresRepository(session))


@router.get("", response_model=CityListResponse)
async def list_cities(
    search: Optional[str] = Query(None, description="Recherche par nom de ville"),
    region: Optional[str] = Query(None, description="Filtrer par région"),
    department: Optional[str] = Query(None, description="Filtrer par département"),
    min_population: Optional[int] = Query(None, ge=0, description="Population minimum"),
    sort_by: str = Query("overall_score", description="Champ de tri"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CityService = Depends(_get_service),
):
    """Recherche de villes avec filtres, tri et pagination."""
    return await service.search_cities(
        search=search,
        region=region,
        department=department,
        min_population=min_population,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.get("/{city_id}", response_model=CityDetail)
async def get_city(
    city_id: int,
    service: CityService = Depends(_get_service),
):
    """Détails complets d'une ville."""
    city = await service.get_city_detail(city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    return city


@router.get("/{city_id}/scores", response_model=CityScores)
async def get_city_scores(
    city_id: int,
    service: CityService = Depends(_get_service),
):
    """Scores qualité de vie d'une ville."""
    scores = await service.get_city_scores(city_id)
    if scores is None:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    return scores
