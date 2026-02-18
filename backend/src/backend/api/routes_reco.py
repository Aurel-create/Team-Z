"""Routes API — Recommandations (Neo4j)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.neo4j import get_neo4j_driver
from backend.db.postgres import get_db
from backend.models import RecommendationsResponse
from backend.repositories.neo4j_repo import Neo4jRepository
from backend.repositories.postgres_repo import PostgresRepository
from backend.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


def _get_service(session: AsyncSession = Depends(get_db)) -> RecommendationService:
    driver = get_neo4j_driver()
    return RecommendationService(
        neo4j_repo=Neo4jRepository(driver),
        postgres_repo=PostgresRepository(session),
    )


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    city_id: int = Query(..., description="ID de la ville source"),
    k: int = Query(5, ge=1, le=20, description="Nombre de recommandations"),
    service: RecommendationService = Depends(_get_service),
):
    """Recommandations de villes similaires basées sur le graphe Neo4j."""
    result = await service.get_recommendations(city_id, k=k)
    if result is None:
        raise HTTPException(status_code=404, detail="Ville non trouvée")
    return result
