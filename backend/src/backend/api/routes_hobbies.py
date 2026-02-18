# filepath: backend/src/backend/api/routes_hobbies.py
"""Routes CRUD pour les hobbies"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import HobbyCreate, HobbyResponse

router = APIRouter(prefix="/hobbies", tags=["hobbies"])


@router.get("/", response_model=List[HobbyResponse])
async def list_hobbies(service: PortfolioService = Depends(get_portfolio_service)):
    items = await service.list_entities("hobbies")
    return items


@router.get("/{hobby_id}", response_model=HobbyResponse)
async def get_hobby(hobby_id: str, service: PortfolioService = Depends(get_portfolio_service)):
    item = await service.get_entity("hobbies", hobby_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Hobby non trouvé")
    return item


@router.post("/", response_model=HobbyResponse)
async def create_hobby(payload: HobbyCreate, service: PortfolioService = Depends(get_portfolio_service)):
    created = await service.create_entity("hobbies", payload.dict())
    return created
