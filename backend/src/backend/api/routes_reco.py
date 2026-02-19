"""Module historique conservé pour compatibilité."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["legacy"])


@router.get("/recommendations")
async def deprecated_recommendations() -> dict[str, str]:
    return {"detail": "Deprecated. Use /skills/{name}/projects for graph-based recommendations."}
