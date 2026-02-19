"""Module repository historique (non utilisé par les nouveaux routers)."""

from __future__ import annotations

from neo4j import AsyncDriver


class Neo4jRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver
        
