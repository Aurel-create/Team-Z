"""Schémas Pydantic du portfolio data-driven."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MongoDocument(BaseModel):
    id: str


class Contact(BaseModel):
    linkedin: str | None = None
    tel: str | None = None
    mail: str | None = None


class InfosPersonnelsBase(BaseModel):
    nom: str
    prenom: str
    contact: Contact = Field(default_factory=Contact)
    description: str | None = None


class InfosPersonnelsCreate(InfosPersonnelsBase):
    pass


class InfosPersonnelsUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    contact: Contact | None = None
    description: str | None = None


class InfosPersonnels(InfosPersonnelsBase, MongoDocument):
    pass


class ProjectBase(BaseModel):
    nom: str
    date_debut: date | None = None
    date_fin: date | None = None
    description: str | None = None
    images: list[str] = Field(default_factory=list)
    entreprise: str | None = None
    collaborateurs: list[str] = Field(default_factory=list)
    lien_github: str | None = None
    status: str | None = None


class ProjectCreate(ProjectBase):
    person_ids: list[str] = Field(default_factory=list)
    technology_ids: list[str] = Field(default_factory=list)
    skill_ids: list[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    nom: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    description: str | None = None
    images: list[str] | None = None
    entreprise: str | None = None
    collaborateurs: list[str] | None = None
    lien_github: str | None = None
    status: str | None = None
    person_ids: list[str] | None = None
    technology_ids: list[str] | None = None
    skill_ids: list[str] | None = None


class Project(ProjectBase, MongoDocument):
    model_config = ConfigDict(from_attributes=True)


class ExperienceBase(BaseModel):
    nom: str
    description: str | None = None
    image: str | None = None
    company: str | None = None
    type_de_poste: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    role: str | None = None


class ExperienceCreate(ExperienceBase):
    skill_ids: list[str] = Field(default_factory=list)
    project_ids: list[str] = Field(default_factory=list)


class ExperienceUpdate(BaseModel):
    nom: str | None = None
    description: str | None = None
    image: str | None = None
    company: str | None = None
    type_de_poste: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    role: str | None = None
    skill_ids: list[str] | None = None
    project_ids: list[str] | None = None


class Experience(ExperienceBase, MongoDocument):
    pass


class EducationBase(BaseModel):
    school_name: str
    degree: str
    description: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    grade: str | None = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    school_name: str | None = None
    degree: str | None = None
    description: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    grade: str | None = None


class Education(EducationBase, MongoDocument):
    pass


class SkillBase(BaseModel):
    nom: str
    category: str | None = None
    description: str | None = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    nom: str | None = None
    category: str | None = None
    description: str | None = None


class Skill(SkillBase, MongoDocument):
    pass


class TechnologyBase(BaseModel):
    nom: str
    image: str | None = None


class TechnologyCreate(TechnologyBase):
    pass


class TechnologyUpdate(BaseModel):
    nom: str | None = None
    image: str | None = None


class Technology(TechnologyBase, MongoDocument):
    pass


class CertificationBase(BaseModel):
    nom: str
    image: str | None = None
    description: str | None = None
    obtention_date: date | None = None


class CertificationCreate(CertificationBase):
    validates_skill_ids: list[str] = Field(default_factory=list)
    validates_technology_ids: list[str] = Field(default_factory=list)


class CertificationUpdate(BaseModel):
    nom: str | None = None
    image: str | None = None
    description: str | None = None
    obtention_date: date | None = None
    validates_skill_ids: list[str] | None = None
    validates_technology_ids: list[str] | None = None


class Certification(CertificationBase, MongoDocument):
    pass


class HobbyBase(BaseModel):
    nom: str
    description: str | None = None


class HobbyCreate(HobbyBase):
    pass


class HobbyUpdate(BaseModel):
    nom: str | None = None
    description: str | None = None


class Hobby(HobbyBase, MongoDocument):
    pass


class GlobalPortfolioResponse(BaseModel):
    infos_personnels: list[InfosPersonnels] = Field(default_factory=list)
    projets: list[Project] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    parcours_scolaire: list[Education] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    technologies: list[Technology] = Field(default_factory=list)
    hobbies: list[Hobby] = Field(default_factory=list)
