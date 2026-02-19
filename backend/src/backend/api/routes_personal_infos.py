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


# ── Helpers ────────────────────────────────────────────────────

def _fix_id(doc: dict) -> dict:
    """Convertit _id MongoDB en str id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def _find_all(collection_name: str) -> list[dict]:
    """Récupère tous les documents d'une collection."""
    db = get_mongo_db()
    cursor = db[collection_name].find()
    return [_fix_id(doc) async for doc in cursor]


async def _find_one(collection_name: str) -> Optional[dict]:
    """Récupère un seul document d'une collection."""
    db = get_mongo_db()
    doc = await db[collection_name].find_one()
    return _fix_id(doc) if doc else None


# ── Info personnelle (document unique) ─────────────────────────

@router.get("", response_model=PersonalInfo)
async def get_personal_infos():
    """Récupère les informations personnelles."""
    db = get_mongo_db()
    doc = await db["infos"].find_one()
    print(doc)
    if doc is None:
        raise HTTPException(status_code=404, detail="Aucune info personnelle trouvée")
    return PersonalInfo.model_validate(doc)