"""Module service historique (non utilisé par les nouveaux routers)."""

from __future__ import annotations

from backend.repositories.neo4j_repo import Neo4jRepository


class RecommendationService:
    def __init__(self, neo4j_repo: Neo4jRepository):
        self.neo4j_repo = neo4j_repo
