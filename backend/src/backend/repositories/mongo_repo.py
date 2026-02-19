"""Module repository historique (non utilisé par les nouveaux routers)."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
