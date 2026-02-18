"""Pydantic models — réexporte les schemas pour l'application portfolio.

Ce fichier n'importe plus de `shared.schemas` pour éviter une dépendance externe
inexistante dans le contexte portfolio. On exporte les modèles locaux définis
dans `project.py` et `portfolio_entities.py`, et on ajoute un modèle simple
`HealthResponse` utilisé par l'endpoint /health.
"""

from datetime import datetime

from pydantic import BaseModel

from .project import ProjectCreate, ProjectResponse
from .portfolio_entities import (
    ExperienceCreate,
    ExperienceResponse,
    CertificationCreate,
    CertificationResponse,
    TechnologyCreate,
    TechnologyResponse,
    EducationCreate,
    EducationResponse,
    HobbyCreate,
    HobbyResponse,
    ContactCreate,
    ContactResponse,
)


class HealthResponse(BaseModel):
    status: str
    version: str
    checked_at: datetime | None = None


__all__ = [
    "ProjectCreate",
    "ProjectResponse",
    "ExperienceCreate",
    "ExperienceResponse",
    "CertificationCreate",
    "CertificationResponse",
    "TechnologyCreate",
    "TechnologyResponse",
    "EducationCreate",
    "EducationResponse",
    "HobbyCreate",
    "HobbyResponse",
    "ContactCreate",
    "ContactResponse",
    "HealthResponse",
]
