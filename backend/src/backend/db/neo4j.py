"""Connexion Neo4j via le driver officiel."""

from __future__ import annotations

from neo4j import AsyncGraphDatabase, AsyncDriver

from backend.core.config import get_settings

_driver: AsyncDriver | None = None


def get_neo4j_driver() -> AsyncDriver:
    """Retourne le driver Neo4j (singleton). À compléter : créer le driver avec AsyncGraphDatabase.driver(uri, auth=(user, password))."""
    global _driver
    settings = get_settings()
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(settings.neo4j_uri,auth=(settings.neo4j_user, settings.neo4j_password))
    return _driver


async def close_neo4j() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
