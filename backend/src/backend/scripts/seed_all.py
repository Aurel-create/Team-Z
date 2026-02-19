"""Script de seed — charge les datasets dans les bases de données.

Usage: python -m backend.scripts.seed_all

1. seed_mongo : charge tous les JSONL du portfolio dans MongoDB
2. seed_neo4j : crée le graphe complet dans Neo4j
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.db.mongo import get_mongo_db
from backend.db.neo4j import get_neo4j_driver

DATASETS_DIR = Path(__file__).resolve().parents[4] / "datasets"


async def seed_mongo():
    """Charge toutes les collections JSONL dans MongoDB."""
    db = get_mongo_db()

    # Mapping : "nom_du_fichier.jsonl" : "nom_de_la_collection_mongo"
    collections_map = {
        "infos_personnels.jsonl": "personal_infos",
        "projets.jsonl": "projects",
        "experiences.jsonl": "experiences",
        "parcours_scolaire.jsonl": "educations",
        "certifications.jsonl": "certifications",
        "skills.jsonl": "skills",
        "hobbies.jsonl": "hobbies",
        "technologies.jsonl": "technologies",
    }

    for filename, col_name in collections_map.items():
        file_path = DATASETS_DIR / filename
        if not file_path.exists():
            print(f"[seed] ⚠️  Fichier ignoré (introuvable) : {filename}")
            continue

        print(f"[seed] Traitement de {col_name} depuis {filename}...")

        collection = db[col_name]
        await collection.delete_many({})  # Reset de la collection

        docs = []
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    doc = json.loads(line)
                    if isinstance(doc.get("created_at"), str):
                        doc["created_at"] = datetime.fromisoformat(
                            doc["created_at"].replace("Z", "+00:00")
                        )
                    elif doc.get("created_at") is None:
                        doc["created_at"] = datetime.now(timezone.utc)

                    docs.append(doc)
                except json.JSONDecodeError:
                    print(f"[seed] Erreur de décodage JSON dans {filename}")

        if docs:
            await collection.insert_many(docs)
            print(f"[seed] ✅ {len(docs)} insérés dans '{col_name}'")

    print("[seed] MongoDB — Global OK")


async def seed_neo4j():
    """Charge les données JSONL du portfolio dans Neo4j et crée les relations."""
    driver = get_neo4j_driver()

    # Mapping: Fichier JSONL -> Label Neo4j
    files_mapping = {
        "infos_personnels.jsonl": "Person",
        "projets.jsonl": "Project",
        "experiences.jsonl": "Experience",
        "parcours_scolaire.jsonl": "Education",
        "certifications.jsonl": "Certification",
        "skills.jsonl": "Skill",
        "hobbies.jsonl": "Hobby",
        "technologies.jsonl": "Technology",
    }

    async with driver.session() as session:
        print("[seed] Neo4j — Nettoyage du graphe...")
        # 1. Reset complet
        await session.run("MATCH (n) DETACH DELETE n")

        # 2. Chargement des Nœuds
        person_id = None

        for filename, label in files_mapping.items():
            file_path = DATASETS_DIR / filename
            if not file_path.exists():
                continue

            nodes_data = []
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        flat_data = {
                            k: v
                            for k, v in data.items()
                            if isinstance(v, (str, int, float, bool))
                        }
                        nodes_data.append(flat_data)

                        if label == "Person" and not person_id:
                            person_id = data.get("id")

            if nodes_data:
                query = f"""
                UNWIND $batch AS row
                MERGE (n:{label} {{id: row.id}})
                SET n += row
                """
                await session.run(query, batch=nodes_data)
                print(f"[seed] Neo4j — {len(nodes_data)} nœuds '{label}' créés.")

        # 3. Création des Relations
        if person_id:
            print("[seed] Neo4j — Création des relations...")

            # ---------------------------------------------------------
            # A) Hub Central : Person -> Tout le reste
            # ---------------------------------------------------------
            relations_map = {
                "Project": "CREATED",
                "Experience": "WORKED_AT",
                "Education": "STUDIED_AT",
                "Certification": "CERTIFIED_IN",
                "Skill": "MASTER",
                "Hobby": "PRACTICES",
                "Technology": "KNOWS",
            }

            for target_label, rel_type in relations_map.items():
                await session.run(
                    f"""
                    MATCH (p:Person {{id: $pid}}), (t:{target_label})
                    MERGE (p)-[:{rel_type}]->(t)
                """,
                    pid=person_id,
                )

            # ---------------------------------------------------------
            # B) Projets ↔ Skills & Technologies
            # ---------------------------------------------------------
            print("[seed] Neo4j — Analyse sémantique des Projets...")
            await session.run("""
                MATCH (p:Project), (t:Technology)
                WHERE toLower(p.description) CONTAINS toLower(t.nom)
                   OR toLower(p.description) CONTAINS toLower(t.name)
                MERGE (p)-[:USES]->(t)
            """)

            await session.run("""
                MATCH (p:Project), (s:Skill)
                WHERE toLower(p.description) CONTAINS toLower(s.nom)
                   OR toLower(p.description) CONTAINS toLower(s.name)
                MERGE (p)-[:REQUIRES]->(s)
            """)

            # ---------------------------------------------------------
            # C) Expériences ↔ Skills
            # ---------------------------------------------------------
            print("[seed] Neo4j — Analyse sémantique des Expériences...")
            await session.run("""
                MATCH (e:Experience), (s:Skill)
                WHERE toLower(e.description) CONTAINS toLower(s.nom)
                MERGE (e)-[:USED_SKILL]->(s)
            """)

        print("[seed] Neo4j — OK (Graphe complet généré)")


async def main():
    print("=" * 50)
    print("SmartCity Explorer — Seed")
    print("=" * 50)
    await seed_mongo()
    await seed_neo4j()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())