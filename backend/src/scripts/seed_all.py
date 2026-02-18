"""Script de seed — charge les datasets dans les bases de données.

Usage: python -m backend.scripts.seed_all

TODO (optionnel — étudiants ou fourni) :
1. Lire datasets/cities.csv et insérer dans PostgreSQL
2. Lire datasets/scores.csv et insérer dans PostgreSQL
3. Lire datasets/reviews.jsonl et insérer dans MongoDB
4. Créer les nœuds et relations dans Neo4j
"""

from __future__ import annotations

import asyncio
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from backend.db.mongo import get_mongo_db
from backend.db.postgres import get_session_factory
from backend.db.neo4j import get_neo4j_driver

DATASETS_DIR = Path(__file__).resolve().parents[5] / "datasets"

async def seed_mongo():
    """Charge reviews.jsonl dans MongoDB."""
    print(f"[seed] Chargement depuis {DATASETS_DIR / 'reviews.jsonl'}")
  
    db = get_mongo_db()
    
    # TODO: Vidage des avis dans la collection reviews
    # ✂️ SOLUTION START
    collection = db["reviews"]
    await collection.delete_many({})
    # ✂️ SOLUTION END

    reviews_path = DATASETS_DIR / "reviews.jsonl"
    docs = []
    with open(reviews_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc = json.loads(line)
            if isinstance(doc.get("created_at"), str):
                doc["created_at"] = datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00"))
            elif doc.get("created_at") is None:
                doc["created_at"] = datetime.now(timezone.utc)
            docs.append(doc)

    # TODO: Insertion des avis dans la collection reviews 
    # ✂️ SOLUTION START
    if docs:
        await collection.insert_many(docs)
    # ✂️ SOLUTION END
    print("[seed] MongoDB — OK")
   


async def seed_neo4j():
    """Crée le graphe de villes, critères et relations dans Neo4j."""
    
    driver = get_neo4j_driver()

    async with driver.session() as session:
        # TODO: Nettoyer le graphe (optionnel : supprimer nos nœuds)
        # ✂️ SOLUTION START
        await session.run("MATCH (n) DETACH DELETE n")
        # ✂️ SOLUTION END

        # 1) Créer les nœuds Criterion à partir des catégories distinctes des scores
  
        # Lire les catégories depuis scores.csv
        categories = set()
        scores_path = DATASETS_DIR / "scores.csv"
        with open(scores_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                categories.add(row.get("label") or row["category"])
        
        # TODO: Créer les nœuds Criterion à partir des catégories distinctes des scores
        # ✂️ SOLUTION START
        categories_query = """
        UNWIND $categories AS cat
        MERGE (c:Criterion {name: cat})
        """
        await session.run(categories_query, categories=list(categories))
        # ✂️ SOLUTION END

        # 2) Créer les nœuds City depuis cities.csv
        cities_path = DATASETS_DIR / "cities.csv"
        cities_rows = []
        with open(cities_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cities_rows.append({
                    "city_id": int(row["id"]),
                    "name": row["name"],
                    "department": row["department"],
                    "region": row["region"],
                    "population": int(row["population"]),
                    "overall_score": float(row.get("overall_score") or 0),
                })
        for city in cities_rows:
            # TODO: Créer les nœuds City à partir des villes de cities.csv
            # ✂️ SOLUTION START
            await session.run("""
                MERGE (c:City {city_id: $city_id})
                SET c.name = $name, c.department = $department, c.region = $region,
                    c.population = $population, c.overall_score = $overall_score
            """, **city)
            # ✂️ SOLUTION END

        # 3) STRONG_IN : ville -> critère quand score >= 7
        scores_path = DATASETS_DIR / "scores.csv"
        with open(scores_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if float(row["score"]) >= 7:
                    label = row.get("label") or row["category"]
                    await session.run("""
                        MATCH (city:City {city_id: $city_id})
                        MATCH (cr:Criterion {name: $label})
                        MERGE (city)-[:STRONG_IN]->(cr)
                    """, city_id=int(row["city_id"]), label=label)

        # 4) SIMILAR_TO : paires de villes avec critères forts en commun (score = 0.5 + 0.1 * nb_communs)
        await session.run("""
            MATCH (a:City)-[:STRONG_IN]->(c:Criterion)<-[:STRONG_IN]-(b:City)
            WHERE a.city_id < b.city_id
            WITH a, b, count(c) AS common
            CREATE (a)-[:SIMILAR_TO {score: 0.5 + 0.1 * common}]->(b)
            CREATE (b)-[:SIMILAR_TO {score: 0.5 + 0.1 * common}]->(a)
        """)
    print("[seed] Neo4j — OK")
    # ✂️ SOLUTION END


async def main():
    print("=" * 50)
    print("SmartCity Explorer — Seed")
    print("=" * 50)
    await seed_postgres()
    await seed_mongo()
    await seed_neo4j()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())
