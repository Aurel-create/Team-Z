"""Routes API — Informations personnelles (MongoDB)."""

from __future__ import annotations

from fastapi import APIRouter

from backend.db.mongo import get_mongo_db
from backend.models import PersonalInfo

router = APIRouter(prefix="/personal-infos", tags=["personal-infos"])


@router.get("", response_model=PersonalInfo)
async def get_personal_infos():
    """Récupère les informations personnelles."""
    db = get_mongo_db()
    doc = await db["infos"].find_one()
    if doc is None:
        return PersonalInfo(id="", nom="", prenom="")
    doc["id"] = str(doc.pop("_id"))
    return PersonalInfo.model_validate(doc)