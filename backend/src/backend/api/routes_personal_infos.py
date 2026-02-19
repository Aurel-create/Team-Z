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

@router.get("", response_model=PersonalInfo)
async def get_personal_infos():
    """Récupère les informations personnelles."""
    db = get_mongo_db()
    doc = await db["personal_infos"].find_one()
    if doc is None:
        raise HTTPException(status_code=404, detail="Aucune info personnelle trouvée")
    return PersonalInfo.model_validate(doc)

@router.get("/certifications", response_model=list[Certification])
async def get_certifications():
    "Récupère les certifications."
    db = get_mongo_db()
    docs = await db["certifications"].find().to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucune certification trouvée")
    return [Certification.model_validate(doc) for doc in docs]

