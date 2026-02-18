# filepath: backend/src/backend/api/deps.py
"""Dependencies pour les routes — construction des services réutilisables."""

from __future__ import annotations

from fastapi import Depends

from backend.db.mongo import get_mongo_db
from backend.repositories.mongo_portfolio_repo import PortfolioMongoRepository
from backend.services import PortfolioService


def get_portfolio_service() -> PortfolioService:
    db = get_mongo_db()
    repo = PortfolioMongoRepository(db)
    # No recommendation service for now
    return PortfolioService(repo, reco_service=None)
