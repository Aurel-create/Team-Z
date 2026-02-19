"""Compatibilité historique — redirige vers la nouvelle couche database."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.database import get_mongo_database


def get_mongo_db() -> AsyncIOMotorDatabase:
    return get_mongo_database()
