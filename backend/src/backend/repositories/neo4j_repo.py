"""Repository Neo4j — graphe de similarité et recommandations.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes Cypher
via le driver Neo4j async.
"""

from __future__ import annotations

from neo4j import AsyncDriver


class Neo4jRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def get_similar_cities(
        self,
        city_id: int,
        k: int = 5,
    ) -> list[dict]:
        """Trouve les K villes les plus similaires via le graphe.

        TODO: Implémenter la requête Cypher :
        - MATCH sur le nœud City avec city_id
        - Traverser les relations SIMILAR_TO (pondérées)
          OU exploiter les relations STRONG_IN vers des critères communs
        - Retourner les K villes les plus proches avec :
          * city (dict des propriétés)
          * similarity_score
          * common_strengths (liste de critères communs via STRONG_IN)

        Exemple de structure de graphe attendue :
          (City)-[:STRONG_IN]->(Criterion)
          (City)-[:SIMILAR_TO {score: 0.87}]->(City)
        """
        # TODO: Implémenter requête Cypher MATCH SIMILAR_TO, retourner city + similarity_score + common_strengths
        async with self.driver.session() as session:
            query = """
            MATCH (city:City {city_id: $city_id})
            MATCH (city)-[sim:SIMILAR_TO]->(similar:City)
            WITH similar, sim.score as similarity_score
            ORDER BY similarity_score DESC
            LIMIT $k
            MATCH (similar)-[:STRONG_IN]->(criterion:Criterion)
            WITH similar, similarity_score, collect(criterion.name) as common_strengths
            RETURN {
              city_id: similar.city_id,
              name: similar.name,
              properties: similar
            } as city, similarity_score, common_strengths
            """
            result = await session.run(query, city_id=city_id, k=k)
            records = await result.data()
            return [
                {
                    "city": record["city"],
                    "similarity_score": record["similarity_score"],
                    "common_strengths": record["common_strengths"],
                }
                for record in records
            ]

    async def get_city_strengths(self, city_id: int) -> list[str]:
        """Récupère les points forts d'une ville (relations STRONG_IN).

        TODO: Implémenter :
        - MATCH (c:City {city_id: $city_id})-[:STRONG_IN]->(cr:Criterion)
        - RETURN cr.name
        """
        # TODO: Implémenter requête Cypher MATCH STRONG_IN -> Criterion, RETURN name
        async with self.driver.session() as session:
            query = """
          MATCH (city:City {city_id: $city_id})-[:STRONG_IN]->(criterion:Criterion)
          RETURN criterion.name as name
          """
            result = await session.run(query, city_id=city_id)
            records = await result.data() 
            return [record["name"] for record in records]

    async def get_technologies_for_project(self, project_mongo_id: str) -> list[str]:
        """Retourne la liste des mongo_id (ou names) des technologies liées à un projet."""
        async with self.driver.session() as session:
            query = """
            MATCH (p:Project {mongo_id: $proj_id})-[:USES]->(t:Technology)
            RETURN collect(t.mongo_id) as ids, collect(t.name) as names
            """
            result = await session.run(query, proj_id=project_mongo_id)
            records = await result.data()
            if not records:
                return []
            rec = records[0]
            ids = rec.get("ids") or []
            names = rec.get("names") or []
            # prefer mongo ids when present, otherwise names
            return [i if i is not None else n for i, n in zip(ids + [None] * (len(names) - len(ids)), names)]

    async def get_projects_for_technology(self, tech_identifier: str) -> list[str]:
        """Retourne les mongo_id des projets qui utilisent une technologie (par mongo_id ou nom)."""
        async with self.driver.session() as session:
            query = """
            MATCH (p:Project)-[:USES]->(t:Technology)
            WHERE t.mongo_id = $ident OR toLower(t.name) = toLower($ident)
            RETURN collect(p.mongo_id) as proj_ids
            """
            result = await session.run(query, ident=tech_identifier)
            records = await result.data()
            if not records:
                return []
            return records[0].get("proj_ids") or []

