# filepath: backend/src/backend/api/routes_technologies.py
"""Routes CRUD pour les technologies."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import TechnologyCreate, TechnologyResponse

router = APIRouter(prefix="/technologies", tags=["technologies"])


@router.get("/", response_model=List[TechnologyResponse])
async def list_technologies(service: PortfolioService = Depends(get_portfolio_service)):
    items = await service.list_entities("technologies")
    return items


@router.get("/{tech_id}", response_model=TechnologyResponse)
async def get_technology(tech_id: str, service: PortfolioService = Depends(get_portfolio_service)):
    item = await service.get_entity("technologies", tech_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Technology non trouvée")
    return item


@router.post("/", response_model=TechnologyResponse)
async def create_technology(payload: TechnologyCreate, service: PortfolioService = Depends(get_portfolio_service)):
    created = await service.create_entity("technologies", payload.dict())
    return created
