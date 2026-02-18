"""Connexion MongoDB via Motor (async)."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.core.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Retourne la base MongoDB (singleton). À compléter : créer le client Motor avec settings.mongo_url, retourner client[settings.mongo_db]."""
    global _client
    settings = get_settings()
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_url)
    return _client[settings.mongo_db]
