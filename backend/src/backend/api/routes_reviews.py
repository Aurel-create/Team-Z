"""Module historique conservé pour compatibilité."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["legacy"])


@router.get("/cities/{city_id}/reviews")
async def deprecated_reviews(city_id: int) -> dict[str, str | int]:
    return {
        "detail": "Deprecated in portfolio backend.",
        "city_id": city_id,
    }
