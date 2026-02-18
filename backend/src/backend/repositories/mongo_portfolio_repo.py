# filepath: backend/src/backend/repositories/mongo_portfolio_repo.py
"""Repository MongoDB pour les entités du portfolio (projects, technologies, experiences, certifications)."""

from __future__ import annotations

from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class PortfolioMongoRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.projects = db["projects"]
        self.technologies = db["technologies"]
        self.experiences = db["experiences"]
        self.certifications = db["certifications"]

    async def _normalize_id(self, doc: dict) -> dict:
        if doc is None:
            return None
        # expose un champ "id" lisible
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def get_project_by_id(self, project_id) -> Optional[dict]:
        """Récupère un projet par son champ `id` (ou ObjectId en string)."""
        query = {"id": project_id}
        doc = await self.projects.find_one(query)
        if doc is None and isinstance(project_id, str):
            try:
                doc = await self.projects.find_one({"_id": ObjectId(project_id)})
            except Exception:
                doc = None
        return await self._normalize_id(doc)

    async def get_entity_by_collection_and_id(self, collection_name: str, id_value) -> Optional[dict]:
        """Récupère un document depuis une collection nommée par `collection_name` et un `id` ou ObjectId string."""
        col = self.db[collection_name]
        query = {"id": id_value}
        doc = await col.find_one(query)
        if doc is None and isinstance(id_value, str):
            try:
                doc = await col.find_one({"_id": ObjectId(id_value)})
            except Exception:
                doc = None
        return await self._normalize_id(doc)
