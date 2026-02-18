"""Service métier — Recommandations (Neo4j).

TODO (étudiants) : Implémenter la logique d'orchestration.
"""

from __future__ import annotations

from typing import Optional

from backend.models import City, RecommendationItem, RecommendationsResponse
from backend.repositories.neo4j_repo import Neo4jRepository
from backend.repositories.mongo_repo import MongoRepository


class RecommendationService:
    def __init__(self, neo4j_repo: Neo4jRepository, mongo_repo: MongoRepository):
        self.neo4j_repo = neo4j_repo
        self.mongo_repo = mongo_repo

    async def get_recommendations(
        self,
        city_id: int,
        k: int = 5,
    ) -> Optional[RecommendationsResponse]:
        """Recommandations de villes similaires.

        TODO:
        1. Vérifier que la ville source existe (postgres_repo.get_city_by_id)
        2. Appeler neo4j_repo.get_similar_cities(city_id, k)
        3. Pour chaque résultat, enrichir avec les infos Postgres si besoin
        4. Construire et retourner un RecommendationsResponse
        """
        source = await self.mongo_repo.get_city_by_id(city_id)
        if source is None:
            return None
        # Appeler neo4j_repo.get_similar_cities(city_id, k)
        neo4j_results = await self.neo4j_repo.get_similar_cities(city_id, k=k)

        items = []
        for rec in neo4j_results:
            city_data = rec["city"]
            # Enrichir avec les données MongoDB si le graphe n'a pas tout
            target_id = city_data.get("city_id")
            if target_id:
                mongo_data = await self.mongo_repo.get_city_by_id(target_id)
                if mongo_data:
                    city_data = mongo_data

            items.append(
                RecommendationItem(
                    city=City(
                        id=city_data.get("id", city_data.get("city_id", 0)),
                        name=city_data.get("name", ""),
                        department=city_data.get("department", ""),
                        region=city_data.get("region", ""),
                        population=city_data.get("population", 0),
                        overall_score=city_data.get("overall_score", 0.0),
                    ),
                    similarity_score=rec["similarity_score"],
                    common_strengths=rec["common_strengths"],
                )
            )

        return RecommendationsResponse(
            source_city=source["name"],
            recommendations=items,
        )
