"""Module service historique (non utilisé par les nouveaux routers)."""

from __future__ import annotations

from backend.repositories.mongo_repo import MongoRepository


class ReviewService:
    def __init__(self, repo: MongoRepository):
        self.repo = repo

