"""Gestionnaire MongoDB (Motor)."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoHandler:
    def __init__(self, uri: str, db_name: str):
        self._uri = uri
        self._db_name = db_name
        self._client: AsyncIOMotorClient | None = None

    def connect(self) -> AsyncIOMotorDatabase:
        if self._client is None:
            self._client = AsyncIOMotorClient(self._uri)
        return self._client[self._db_name]

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
