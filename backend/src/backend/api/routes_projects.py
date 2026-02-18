# filepath: backend/src/backend/api/routes_projects.py
"""Routes CRUD pour les projets."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(service: PortfolioService = Depends(get_portfolio_service)):
    items = await service.list_entities("projects")
    return items


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, service: PortfolioService = Depends(get_portfolio_service)):
    project = await service.get_entity("projects", project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return project


@router.post("/", response_model=ProjectResponse)
async def create_project(payload: ProjectCreate, service: PortfolioService = Depends(get_portfolio_service)):
    created = await service.create_entity("projects", payload.dict())
    return created
