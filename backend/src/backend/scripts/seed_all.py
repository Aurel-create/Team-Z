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



from backend.db.mongo import get_mongo_db
from backend.db.neo4j import get_neo4j_driver

DATASETS_DIR = Path(__file__).resolve().parents[3] / "datasets"


import csv


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
        "technologies.jsonl": "Technology"
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

            # Lecture du fichier JSONL
            nodes_data = []
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Aplatir les données pour Neo4j
                        flat_data = {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool))}
                        nodes_data.append(flat_data)
                        
                        if label == "Person" and not person_id:
                            person_id = data.get("id")

            if nodes_data:
                # Création en batch
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
                "Certification": "OBTAINED",
                "Skill": "MASTER",
                "Hobby": "PRACTICES",
                "Technology": "KNOWS"
            }
            
            for target_label, rel_type in relations_map.items():
                await session.run(f"""
                    MATCH (p:Person {{id: $pid}}), (t:{target_label})
                    MERGE (p)-[:{rel_type}]->(t)
                """, pid=person_id)

            # ---------------------------------------------------------
            # B) Projets ↔ Skills & Technologies
            # ---------------------------------------------------------
            print("[seed] Neo4j — Analyse sémantique des Projets...")
            await session.run("""
                MATCH (p:Project), (t:Technology)
                WHERE toLower(p.description) CONTAINS toLower(t.nom)
                MERGE (p)-[:USES_TECH]->(t)
            """)
            
            await session.run("""
                MATCH (p:Project), (s:Skill)
                WHERE toLower(p.description) CONTAINS toLower(s.nom)
                MERGE (p)-[:REQUIRES_SKILL]->(s)
            """)

            # ---------------------------------------------------------
            # C) Expériences ↔ Skills & Technologies
            # ---------------------------------------------------------
            print("[seed] Neo4j — Analyse sémantique des Expériences...")
            await session.run("""
                MATCH (e:Experience), (s:Skill)
                WHERE toLower(e.description) CONTAINS toLower(s.nom) OR toLower(e.nom) CONTAINS toLower(s.nom)
                MERGE (e)-[:APPLIED_SKILL]->(s)
            """)
            
            # NOUVEAU : Une expérience utilise des technos
            await session.run("""
                MATCH (e:Experience), (t:Technology)
                WHERE toLower(e.description) CONTAINS toLower(t.nom) OR toLower(e.nom) CONTAINS toLower(t.nom)
                MERGE (e)-[:USED_TECH]->(t)
            """)

            # ---------------------------------------------------------
            # D) Skills ↔ Categories (Organisation)
            # ---------------------------------------------------------
            print("[seed] Neo4j — Organisation des Skills par Catégorie...")
            await session.run("""
                MATCH (s:Skill)
                WHERE s.category IS NOT NULL AND s.category <> ""
                MERGE (c:Category {name: s.category})
                MERGE (s)-[:BELONGS_TO]->(c)
            """)

            # ---------------------------------------------------------
            # E) Certifications ↔ Skills & Technologies
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison des Certifications...")
            await session.run("""
                MATCH (c:Certification), (s:Skill)
                WHERE (toLower(c.nom) CONTAINS toLower(s.nom) OR toLower(c.description) CONTAINS toLower(s.nom))
                MERGE (c)-[:VALIDATES_SKILL]->(s)
            """)
            
            await session.run("""
                MATCH (c:Certification), (t:Technology)
                WHERE (toLower(c.nom) CONTAINS toLower(t.nom) OR toLower(c.description) CONTAINS toLower(t.nom))
                MERGE (c)-[:VALIDATES_TECH]->(t)
            """)

            # ---------------------------------------------------------
            # F) Éducation (Parcours Scolaire) ↔ Skills & Technologies
            # ---------------------------------------------------------
            print("[seed] Neo4j — Analyse sémantique de l'Éducation...")
            # NOUVEAU : On apprend des skills à l'école
            await session.run("""
                MATCH (ed:Education), (s:Skill)
                WHERE toLower(ed.description) CONTAINS toLower(s.nom) OR toLower(ed.degree) CONTAINS toLower(s.nom)
                MERGE (ed)-[:TAUGHT_SKILL]->(s)
            """)
            
            # NOUVEAU : On apprend des technos à l'école
            await session.run("""
                MATCH (ed:Education), (t:Technology)
                WHERE toLower(ed.description) CONTAINS toLower(t.nom) OR toLower(ed.degree) CONTAINS toLower(t.nom)
                MERGE (ed)-[:TAUGHT_TECH]->(t)
            """)

            # ---------------------------------------------------------
            # G) Skills ↔ Technologies (Le liant final)
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison entre Compétences et Technologies...")
            # NOUVEAU : Un Skill englobe ou implique une Technologie précise
            # Ex: Le Skill "Backend" implique la techno "Node.js" si mentionnée
            await session.run("""
                MATCH (s:Skill), (t:Technology)
                WHERE toLower(s.description) CONTAINS toLower(t.nom) OR toLower(s.nom) CONTAINS toLower(t.nom)
                MERGE (s)-[:INVOLVES_TECH]->(t)
            """)

        print("[seed] Neo4j — OK (Graphe enrichi et complètement interconnecté)")


async def main():
    print("=" * 50)
    print("SmartCity Explorer — Seed")
    print("=" * 50)
    await seed_mongo()
    await seed_neo4j()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())