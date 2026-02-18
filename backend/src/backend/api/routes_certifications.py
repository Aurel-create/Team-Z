# filepath: backend/src/backend/api/routes_certifications.py
"""Routes CRUD pour les certifications."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import CertificationCreate, CertificationResponse

router = APIRouter(prefix="/certifications", tags=["certifications"])


@router.get("/", response_model=List[CertificationResponse])
async def list_certifications(service: PortfolioService = Depends(get_portfolio_service)):
    items = await service.list_entities("certifications")
    return items


@router.get("/{cert_id}", response_model=CertificationResponse)
async def get_certification(cert_id: str, service: PortfolioService = Depends(get_portfolio_service)):
    item = await service.get_entity("certifications", cert_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Certification non trouvée")
    return item


@router.post("/", response_model=CertificationResponse)
async def create_certification(payload: CertificationCreate, service: PortfolioService = Depends(get_portfolio_service)):
    created = await service.create_entity("certifications", payload.dict())
    return created
