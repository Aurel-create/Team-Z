# filepath: backend/src/backend/models/portfolio_entities.py
"""Pydantic models pour les autres entités du portfolio."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class ExperienceBase(BaseModel):
    title: str
    company: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: str


class CertificationBase(BaseModel):
    title: str
    issuer: Optional[str] = None
    date: Optional[date] = None
    link: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationResponse(CertificationBase):
    id: str


class TechnologyBase(BaseModel):
    name: str
    description: Optional[str] = None


class TechnologyCreate(TechnologyBase):
    pass


class TechnologyResponse(TechnologyBase):
    id: str


class EducationBase(BaseModel):
    school: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: str


class HobbyBase(BaseModel):
    name: str
    description: Optional[str] = None


class HobbyCreate(HobbyBase):
    pass


class HobbyResponse(HobbyBase):
    id: str


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class ContactResponse(ContactCreate):
    id: str
    created_at: Optional[datetime] = None
