# filepath: backend/src/backend/services/portfolio_service.py
"""Service générique pour les entités du portfolio (projects, technologies, ...).

Ce service centralise les opérations CRUD courantes en s'appuyant sur
`PortfolioMongoRepository`. Il expose aussi de petites méthodes utilitaires
pour intégrer le graphe Neo4j via `RecommendationService` si nécessaire.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.services.recommendation_service import RecommendationService

from backend.repositories.mongo_portfolio_repo import PortfolioMongoRepository


class PortfolioService:
    def __init__(self, mongo_repo: PortfolioMongoRepository, reco_service: "RecommendationService" | None = None):
        self.mongo = mongo_repo
        self.reco = reco_service

    # --- Generic CRUD operations -------------------------------------------------
    async def list_entities(self, collection: str, *, filter: Dict[str, Any] | None = None, page: int = 1, page_size: int = 100) -> List[Dict[str, Any]]:
        col = self.mongo.db[collection]
        query = filter or {}
        skip = (page - 1) * page_size
        cursor = col.find(query).skip(skip).limit(page_size)
        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            items.append(doc)
        return items

    async def get_entity(self, collection: str, id_value: str) -> Optional[Dict[str, Any]]:
        return await self.mongo.get_entity_by_collection_and_id(collection, id_value)

    async def create_entity(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        col = self.mongo.db[collection]
        # Do not allow _id in payload
        data = {k: v for k, v in data.items() if k != "_id"}
        result = await col.insert_one(data)
        created = await col.find_one({"_id": result.inserted_id})
        created["id"] = str(created.pop("_id"))
        return created

    async def update_entity(self, collection: str, id_value: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        col = self.mongo.db[collection]
        # try by explicit id field first, else by _id
        query = {"id": id_value}
        res = await col.update_one(query, {"$set": data})
        if res.matched_count == 0:
            try:
                from bson import ObjectId

                query = {"_id": ObjectId(id_value)}
                res = await col.update_one(query, {"$set": data})
            except Exception:
                return None
        if res.matched_count == 0:
            return None
        # return updated
        doc = await col.find_one(query)
        if doc is None:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    async def delete_entity(self, collection: str, id_value: str) -> bool:
        col = self.mongo.db[collection]
        query = {"id": id_value}
        res = await col.delete_one(query)
        if res.deleted_count == 0:
            try:
                from bson import ObjectId

                res = await col.delete_one({"_id": ObjectId(id_value)})
            except Exception:
                return False
        return res.deleted_count > 0

    # --- Portfolio-specific helpers ---------------------------------------------
    async def get_project_technologies(self, project_mongo_id: str) -> List[Dict[str, Any]]:
        """Si le service de reco est fourni, retourne les technologies liées à un projet en enrichissant via Mongo."""
        if self.reco is None:
            return []
        return await self.reco.get_project_related_technologies(project_mongo_id)

    async def get_projects_using_technology(self, tech_identifier: str) -> List[Dict[str, Any]]:
        if self.reco is None:
            return []
        return await self.reco.get_projects_using_technology(tech_identifier)
