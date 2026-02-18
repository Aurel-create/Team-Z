# filepath: backend/src/backend/models/project.py
"""Pydantic models pour les projets."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = []
    link: Optional[str] = None


class ProjectCreate(ProjectBase):
    created_at: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: str
    created_at: Optional[datetime] = None
