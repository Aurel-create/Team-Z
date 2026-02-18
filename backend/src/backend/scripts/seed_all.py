"""Script de seed — charge les datasets dans les bases de données.

Usage: python -m backend.scripts.seed_all

TODO (à compléter après les connexions DB) :
1. seed_postgres : charger cities.csv et scores.csv dans PostgreSQL (tables, INSERT)
2. seed_mongo : charger reviews.jsonl dans la collection MongoDB reviews
3. seed_neo4j : créer le graphe (nœuds City, Criterion, relations STRONG_IN, SIMILAR_TO)
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


import csv
from sqlalchemy import text

async def seed_postgres():
    SessionLocal = get_session_factory()

    async with SessionLocal() as session:

        # Création tables
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department TEXT,
                region TEXT,
                population INTEGER,
                description TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                overall_score DOUBLE PRECISION
            );
        """))

        await session.execute(text("""
    CREATE TABLE IF NOT EXISTS scores (
        city_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        label TEXT,
        score DOUBLE PRECISION NOT NULL
    )
"""))

        await session.commit()


        # 🔥 SUPPRESSION avant insertion (important pour le test)
        await session.execute(text("DELETE FROM scores;"))
        await session.execute(text("DELETE FROM cities;"))

        await session.commit()

        cities_path = DATASETS_DIR / "cities.csv"
        with open(cities_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = row.get("latitude")
                lon = row.get("longitude")
                osc = row.get("overall_score")
                await session.execute(
                    text("""
            INSERT INTO cities (
                id, name, department, region,
                population, description,
                latitude, longitude, overall_score
            )
            VALUES (
                :id, :name, :department, :region,
                :population, :description,
                :latitude, :longitude, :overall_score
            );
        """),
                    {
                        "id": int(row["id"]),
                        "name": row["name"],
                        "department": row["department"],
                        "region": row["region"],
                        "population": int(row["population"]),
                        "description": row.get("description") or "",
                        "latitude": float(lat) if lat else None,
                        "longitude": float(lon) if lon else None,
                        "overall_score": float(osc) if osc else 0.0,
                    },
                )
        await session.commit()

        scores_path = DATASETS_DIR / "scores.csv"
        with open(scores_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                await session.execute(
                    text("""
    INSERT INTO scores (city_id, category, label, score)
    VALUES (:city_id, :category, :label, :score)
"""),
                    {
                        "city_id": int(row["city_id"]),
                        "category": row["category"],
                        "label": row.get("label") or "",
                        "score": float(row["score"]),
                    },
                )



        await session.commit()


async def seed_mongo():
    """Charge reviews.jsonl dans MongoDB."""
    # TODO: Utiliser get_mongo_db(), collection reviews : delete_many puis charger reviews.jsonl (insert_many)
    db= get_mongo_db()
    collection = db["reviews"]
    reviews_path = DATASETS_DIR / "reviews.jsonl"
    # 1. Nettoyage de la collection existante (Idempotence)
    await collection.delete_many({})

   # 2. Lecture et parsing des documents
    docs = []
    with open(reviews_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Transformation de la ligne JSON en dictionnaire Python (document)
            doc = json.loads(line)
            
            # Conversion du champ created_at pour valider les tests unitaires
            if "created_at" in doc and isinstance(doc["created_at"], str):
                # Gestion du format ISO (remplacement du Z par l'offset UTC)
                doc["created_at"] = datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00"))
            elif "created_at" not in doc:
                doc["created_at"] = datetime.now(timezone.utc)
                
            docs.append(doc)

    # 3. Insertion massive (Bulk insert)
    if docs:
        await collection.insert_many(docs)
        print(f"[seed] {len(docs)} documents insérés avec succès.")

    print("[seed] MongoDB — OK")

async def seed_neo4j():
    """Crée le graphe de villes, critères et relations dans Neo4j."""
    driver = get_neo4j_driver()

    cities = []
    with open(DATASETS_DIR / "cities.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cities.append(row)

    scores = []
    with open(DATASETS_DIR / "scores.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            scores.append(row)

    criteria = {score["category"] for score in scores}

    async with driver.session() as session:

        await session.run("MATCH (n) DETACH DELETE n")

        for name in criteria:
            await session.run(
                "MERGE (c:Criterion {name: $name})",
                name=name,
            )

        for city in cities:
            await session.run(
                "MERGE (c:City {city_id: $city_id, name: $name, department: $department, "
                "region: $region, population: $population, overall_score: $overall_score})",
                city_id=int(city["id"]),
                name=city["name"],
                department=city["department"],
                region=city["region"],
                population=city["population"],
                overall_score=city["overall_score"],
            )

        for score in scores:
            if float(score["score"]) >= 7:
                await session.run(
                    "MATCH (city:City {city_id: $city_id}), (crit:Criterion {name: $name}) "
                    "MERGE (city)-[:STRONG_IN]->(crit)",
                    city_id=int(score["city_id"]),
                    name=score["category"],
                )

        await session.run(
            "MATCH (c1:City)-[:STRONG_IN]->(crit:Criterion)<-[:STRONG_IN]-(c2:City) "
            "WHERE c1.city_id < c2.city_id "
            "WITH c1, c2, count(crit) AS common_criteria "
            "WITH c1, c2, CASE "
            "WHEN 0.5 + 0.1 * common_criteria > 1.0 THEN 1.0 "
            "ELSE 0.5 + 0.1 * common_criteria "
            "END AS final_score "
            "MERGE (c1)-[:SIMILAR_TO {score: final_score}]->(c2) "
            "MERGE (c2)-[:SIMILAR_TO {score: final_score}]->(c1)"
        )
    print("[seed] Neo4j — OK")


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