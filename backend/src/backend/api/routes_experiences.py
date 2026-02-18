# filepath: backend/src/backend/api/routes_experiences.py
"""Routes CRUD pour les expériences."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import ExperienceCreate, ExperienceResponse

router = APIRouter(prefix="/experiences", tags=["experiences"])


@router.get("/", response_model=List[ExperienceResponse])
async def list_experiences(service: PortfolioService = Depends(get_portfolio_service)):
    items = await service.list_entities("experiences")
    return items


@router.get("/{exp_id}", response_model=ExperienceResponse)
async def get_experience(exp_id: str, service: PortfolioService = Depends(get_portfolio_service)):
    item = await service.get_entity("experiences", exp_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Experience non trouvée")
    return item


@router.post("/", response_model=ExperienceResponse)
async def create_experience(payload: ExperienceCreate, service: PortfolioService = Depends(get_portfolio_service)):
    created = await service.create_entity("experiences", payload.dict())
    return created
