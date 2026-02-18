# filepath: backend/src/backend/api/routes_education.py
"""Routes CRUD pour le parcours scolaire (education)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import EducationCreate, EducationResponse

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/", response_model=List[EducationResponse])
async def list_education(service: PortfolioService = Depends(get_portfolio_service)):
    items = await service.list_entities("education")
    return items


@router.get("/{edu_id}", response_model=EducationResponse)
async def get_education(edu_id: str, service: PortfolioService = Depends(get_portfolio_service)):
    item = await service.get_entity("education", edu_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Parcours non trouvé")
    return item


@router.post("/", response_model=EducationResponse)
async def create_education(payload: EducationCreate, service: PortfolioService = Depends(get_portfolio_service)):
    created = await service.create_entity("education", payload.dict())
    return created
