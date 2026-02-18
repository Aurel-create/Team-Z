# filepath: backend/src/backend/api/routes_contact.py
"""Route pour le formulaire de contact (POST uniquement)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from backend.api.deps import get_portfolio_service
from backend.services import PortfolioService
from backend.models import ContactCreate, ContactResponse

router = APIRouter(prefix="/contact", tags=["contact"])


def get_db():
    return get_mongo_db()


@router.post("/", response_model=ContactResponse)
async def submit_contact(payload: ContactCreate, service: PortfolioService = Depends(get_portfolio_service)):
    data = payload.dict()
    created = await service.create_entity("contacts", data)
    # convert created_at ISO->datetime if needed
    if isinstance(created.get("created_at"), str):
        try:
            created["created_at"] = datetime.fromisoformat(created["created_at"].replace("Z", "+00:00"))
        except Exception:
            pass
    return created
