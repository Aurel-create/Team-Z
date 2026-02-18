"""Repository PostgreSQL — accès aux villes et scores.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes SQL
via SQLAlchemy async (ou raw SQL avec asyncpg).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Colonnes autorisées pour le tri (protection contre l'injection SQL)
_ALLOWED_SORT = {"overall_score", "population", "name", "department", "region"}


class PostgresRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cities(
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
    ) -> tuple[list[dict], int]:
        """Recherche de villes avec filtres, tri et pagination.

        TODO: Implémenter la requête SQL avec :
        - Filtre ILIKE sur le nom de ville (search)
        - Filtre exact sur region et department
        - Filtre >= sur population
        - Tri dynamique (overall_score, population, name…)
        - Pagination OFFSET/LIMIT
        - Retourner (liste_de_dicts, total_count)
        """
        # TODO: Implémenter la requête SQL (filtres, tri, pagination, count)
        if sort_by not in _ALLOWED_SORT:
            sort_by = "overall_score"
        sort_direction = "ASC" if sort_order.lower() == "asc" else "DESC"
        filters = []
        params = {}
        if search:
            filters.append("name ILIKE :search")
            params["search"] = f"%{search}%"
        if region:
            filters.append("region = :region")
            params["region"] = region
        if department:
            filters.append("department = :department")
            params["department"] = department
        if min_population is not None:
            filters.append("population >= :min_population")
            params["min_population"] = min_population
        where_clause = " AND ".join(filters) if filters else "1=1"
        count_query = text(f"""
            SELECT COUNT(*)
            FROM cities
            WHERE {where_clause}
        """)
        count_result = await self.session.execute(count_query, params)
        total = count_result.scalar_one()

        query = text(f"""
            SELECT id, name, department, region, population, 
               description, latitude, longitude, overall_score
            FROM cities
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_direction}
            OFFSET :offset LIMIT :limit
        """)
        data_params = dict(params)
        data_params["offset"] = (page - 1) * page_size
        data_params["limit"] = page_size
        result = await self.session.execute(query, data_params)
        rows = result.mappings().all()
        return [dict(row) for row in rows], total
        

    async def get_city_by_id(self, city_id: int) -> Optional[dict]:
        """Récupère les détails d'une ville par son ID.

        TODO: Implémenter la requête SQL pour récupérer une ville
        avec toutes ses colonnes (name, department, region, population,
        description, latitude, longitude, overall_score).
        """
        query = text("""
            SELECT id, name, department, region, population, 
               description, latitude, longitude, overall_score
            FROM cities
            WHERE id = :city_id
        """)
        result = await self.session.execute(query, {"city_id": city_id})
        row = result.mappings().first()

        if row is None:
            return None

        return dict(row)

    async def get_city_scores(self, city_id: int) -> list[dict]:
        """Récupère les scores par catégorie pour une ville.

        TODO: Implémenter la jointure entre cities et scores.
        Retourner une liste de dicts: [{"category": ..., "score": ..., "label": ...}]
        """
        # TODO: Implémenter SELECT scores pour une ville (table scores)
        query = text("""
            SELECT s.category, s.score, s.label
            FROM scores s
            WHERE s.city_id = :city_id
            ORDER BY s.category
        """)
        result = await self.session.execute(query, {"city_id": city_id})
        rows = result.mappings().all()

        return [dict(row) for row in rows]
        
