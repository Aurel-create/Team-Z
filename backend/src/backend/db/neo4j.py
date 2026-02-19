"""Compatibilité historique — redirige vers la nouvelle couche database."""

from __future__ import annotations

from neo4j import AsyncDriver

from backend.database import close_databases, get_neo4j_driver


async def close_neo4j() -> None:
    await close_databases()
