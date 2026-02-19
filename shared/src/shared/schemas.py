"""Pydantic models partagés entre backend et frontend."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ── System ─────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


# ── Personal Info ──────────────────────────────────────────────

class Contact(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    liens_linkedin: Optional[str] = Field(None, alias="liens linkedin")
    telephone: Optional[str] = Field(None, alias="numéro de téléphone")
    email: Optional[str] = Field(None, alias="Adresse mail")


class PersonalInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    nom: str = Field("", alias="Nom")
    prenom: str = Field("", alias="Prenom")
    contact: Optional[Contact] = Field(None, alias="Contact")
    description: str = Field("", alias="Description")


# ── Experience ─────────────────────────────────────────────────

class Experience(BaseModel):
    id: str
    nom: str
    description: str = ""
    image: Optional[str] = None
    company: str = ""
    type_de_poste: str = ""
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    role: str = ""


# ── Skills ─────────────────────────────────────────────────────

class Skill(BaseModel):
    id: str
    nom: str
    category: str = ""
    description: str = ""


# ── Technos ────────────────────────────────────────────────────

class Techno(BaseModel):
    id: str
    nom: str
    image: Optional[str] = None


# ── Projets ────────────────────────────────────────────────────

class Projet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    nom: str
    date_debut: Optional[date] = Field(None, alias="date début")
    date_fin: Optional[date] = Field(None, alias="date fin")
    description: str = ""
    images: list[str] = []
    entreprise: str = ""
    collaborateurs: list[str] = []
    lien_github: Optional[str] = Field(None, alias="lien github")
    status: str = ""


class ProjetDetail(Projet):
    """Ajout liens Neo4j."""
    technologies: list[str] = []
    skills: list[str] = []


# ── Parcours scolaire ─────────────────────────────────────────

class ParcoursScolaire(BaseModel):
    id: str
    school_name: str
    degree: str = ""
    description: str = ""
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: str = ""


# ── Certifications ─────────────────────────────────────────────

class Certification(BaseModel):
    id: str
    nom: str
    image: Optional[str] = None
    description: str = ""
    obtention_date: Optional[date] = None


# ── Hobbies ────────────────────────────────────────────────────

class Hobby(BaseModel):
    id: str
    nom: str
    description: str = ""


# ── Cities (legacy) ────────────────────────────────────────────

class City(BaseModel):
    id: int
    name: str
    department: str = ""
    region: str = ""
    population: int = 0
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    overall_score: float = 0.0


class ScoreCategory(BaseModel):
    category: str
    score: float
    label: str = ""


class CityScores(BaseModel):
    city_id: int
    scores: list[ScoreCategory] = []
    overall: float = 0.0


class CityDetail(BaseModel):
    id: int
    name: str
    department: str = ""
    region: str = ""
    population: int = 0
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    overall_score: float = 0.0
    scores: list[ScoreCategory] = []


class CityListResponse(BaseModel):
    cities: list[City] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


# ── Reviews ────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    author: str
    rating: float = Field(..., ge=0, le=5)
    comment: str = ""


class Review(BaseModel):
    id: str = ""
    city_id: int = 0
    author: str = ""
    rating: float = 0.0
    comment: str = ""
    created_at: Optional[datetime] = None


class ReviewsResponse(BaseModel):
    reviews: list[Review] = []
    total: int = 0


# ── Recommendations ───────────────────────────────────────────

class RecommendationItem(BaseModel):
    city: City
    similarity_score: float = 0.0
    common_strengths: list[str] = []


class RecommendationsResponse(BaseModel):
    source_city: str
    recommendations: list[RecommendationItem] = []
