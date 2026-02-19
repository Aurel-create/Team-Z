"""Routes API — Portfolio / Informations personnelles (MongoDB)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.db.mongo import get_mongo_db
from backend.models import (
    Certification,
    Contact,
    Experience,
    Hobby,
    ParcoursScolaire,
    PersonalInfo,
    Projet,
    Skill,
    Techno,
)

router = APIRouter(prefix="/personal-infos", tags=["personal-infos"])


# ── Info personnelles (document unique) ─────────────────────────

@router.get(
    "",
    response_model=PersonalInfo,
    summary="Informations personnelles",
    description="Retourne les informations personnelles (nom, prénom, contact, description) depuis MongoDB.",
    response_description="Document unique contenant les informations personnelles.",
    responses={404: {"description": "Aucune information personnelle trouvée en base de données."}},
)
async def get_personal_infos():
    db = get_mongo_db()
    doc = await db["personal_infos"].find_one({}, {"_id": 0})
    if doc is None:
        raise HTTPException(status_code=404, detail="Aucune info personnelle trouvée")
    return PersonalInfo.model_validate(doc)


# ── Certifications ─────────────────────────────────────────────

@router.get(
    "/certifications",
    response_model=list[Certification],
    summary="Liste des certifications",
    description="Retourne la liste complète des certifications obtenues depuis MongoDB.",
    response_description="Liste des certifications avec nom, image, description et date d'obtention.",
    responses={404: {"description": "Aucune certification trouvée en base de données."}},
)
async def get_certifications():
    db = get_mongo_db()
    docs = await db["certifications"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucune certification trouvée")
    return [Certification.model_validate(doc) for doc in docs]
