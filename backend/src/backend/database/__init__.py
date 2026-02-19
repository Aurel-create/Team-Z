from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase
from neo4j import AsyncDriver

from backend.core.config import get_settings
from backend.database.mongo_handler import MongoHandler
from backend.database.neo4j_handler import Neo4jHandler

_settings = get_settings()
_mongo_handler = MongoHandler(_settings.mongo_url, _settings.mongo_db)
_neo4j_handler = Neo4jHandler(
	_settings.neo4j_uri,
	_settings.neo4j_user,
	_settings.neo4j_password,
)


def get_mongo_database() -> AsyncIOMotorDatabase:
	return _mongo_handler.connect()


def get_neo4j_driver() -> AsyncDriver:
	return _neo4j_handler.connect()


async def close_databases() -> None:
	await _neo4j_handler.close()
	await _mongo_handler.close()


__all__ = [
	"MongoHandler",
	"Neo4jHandler",
	"get_mongo_database",
	"get_neo4j_driver",
	"close_databases",
]
