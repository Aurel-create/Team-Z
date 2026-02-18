"""Service métier — Villes et scores.

TODO (étudiants) : Implémenter la logique d'orchestration.
Le service fait le lien entre les routes API et les repositories.
"""

from __future__ import annotations

from typing import Optional

from backend.models import City, CityDetail, CityListResponse, CityScores, ScoreCategory
from backend.repositories.postgres_repo import PostgresRepository


class CityService:
    def __init__(self, repo: PostgresRepository):
        self.repo = repo

    async def search_cities(
        self,
        *,
        search: Optional[str] = None,
        region: Optional[str] = None,
        department: Optional[str] = None,
        min_population: Optional[int] = None,
        sort_by: str = "overall_score",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> CityListResponse:
        """Recherche de villes avec filtres.

        TODO: Appeler self.repo.get_cities(...) et convertir en CityListResponse.
        """
        # TODO: Appeler self.repo.get_cities(...) et convertir en CityListResponse.
         
        rows , total = await self.repo.get_cities(search=search, region=region,department=department, min_population=min_population,sort_by= sort_by,sort_order = sort_order,page=page, page_size=page_size)
        cities = [City(**row) for row in rows]
        return CityListResponse(cities=cities, total=total, page=page, page_size=page_size)

    async def get_city_detail(self, city_id: int) -> Optional[CityDetail]:
        """Détails complets d'une ville (infos + scores).

        TODO:
        1. Appeler self.repo.get_city_by_id(city_id)
        2. Appeler self.repo.get_city_scores(city_id)
        3. Combiner dans un CityDetail
        """
        row = await self.repo.get_city_by_id(city_id)
        if row is None:
            return None

        score_rows = await self.repo.get_city_scores(city_id)
        scores = [ScoreCategory(**s) for s in score_rows]

        return CityDetail(**row, scores=scores)

    async def get_city_scores(self, city_id: int) -> Optional[CityScores]:
        """Scores d'une ville.

        TODO: Appeler self.repo.get_city_scores(city_id) et convertir en CityScores.
        """
        row = await self.repo.get_city_by_id(city_id)
        if row is None:
            return None

        score_rows = await self.repo.get_city_scores(city_id)
        scores = [ScoreCategory(**s) for s in score_rows]

        overall = row.get("overall_score", 0.0)
        return CityScores(city_id=city_id, scores=scores, overall=overall)
