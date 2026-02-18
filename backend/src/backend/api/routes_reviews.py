"""Routes API — Avis utilisateurs (MongoDB)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.db.mongo import get_mongo_db
from backend.models import Review, ReviewCreate, ReviewsResponse
from backend.repositories.mongo_repo import MongoRepository
from backend.services.review_service import ReviewService

router = APIRouter(tags=["reviews"])


def _get_service() -> ReviewService:
    db = get_mongo_db()
    return ReviewService(repo=MongoRepository(db))


@router.get("/cities/{city_id}/reviews", response_model=ReviewsResponse)
async def get_reviews(
    city_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    service: ReviewService = Depends(_get_service),
):
    """Récupère les avis d'une ville."""
    return await service.get_reviews(city_id, page=page, page_size=page_size)


@router.post("/cities/{city_id}/reviews", response_model=Review, status_code=201)
async def create_review(
    city_id: int,
    review: ReviewCreate,
    service: ReviewService = Depends(_get_service),
):
    """Ajoute un nouvel avis pour une ville."""
    return await service.create_review(city_id, review)
