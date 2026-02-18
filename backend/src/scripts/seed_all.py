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


from backend.db.mongo import get_mongo_db
from backend.db.neo4j import get_neo4j_driver

DATASETS_DIR = Path(__file__).resolve().parents[3] / "datasets"

async def seed_mongo():
    """Charge toutes les collections JSONL dans MongoDB."""
    db = get_mongo_db()
    
    # Mapping : "nom_du_fichier.jsonl" : "nom_de_la_collection_mongo"
    # Assurez-vous que les fichiers existent bien dans DATASETS_DIR
    collections_map = {
        "infos_personnels.jsonl": "personal_infos",
        "projets.jsonl": "projects",
        "experiences.jsonl": "experiences",
        "parcours_scolaire.jsonl": "educations",
        "certifications.jsonl": "certifications",
        "skills.jsonl": "skills",
        "hobbies.jsonl": "hobbies",
        "technologies.jsonl": "technologies"
    }

    for filename, col_name in collections_map.items():
        file_path = DATASETS_DIR / filename
        
        if not file_path.exists():
            print(f"[seed] ⚠️  Fichier ignoré (introuvable) : {filename}")
            continue

        print(f"[seed] Traitement de {col_name} depuis {filename}...")
        
        # ✂️ SOLUTION START
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
                    # Conservation de votre logique de date
                    if isinstance(doc.get("created_at"), str):
                        doc["created_at"] = datetime.fromisoformat(doc["created_at"].replace("Z", "+00:00"))
                    elif doc.get("created_at") is None:
                        doc["created_at"] = datetime.now(timezone.utc)
                    
                    docs.append(doc)
                except json.JSONDecodeError:
                    print(f"[seed] Erreur de décodage JSON dans {filename}")

        if docs:
            await collection.insert_many(docs)
            print(f"[seed] ✅ {len(docs)} insérés dans '{col_name}'")
        # ✂️ SOLUTION END

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
            
            # A) Hub Central : Person -> Tout le reste
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

            # B) Liens Contextuels : Project -> Technology / Skill (via description)
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

            # C) Experience -> Skill
            print("[seed] Neo4j — Analyse sémantique des Expériences...")
            await session.run("""
                MATCH (e:Experience), (s:Skill)
                WHERE toLower(e.description) CONTAINS toLower(s.nom)
                MERGE (e)-[:APPLIED_SKILL]->(s)
            """)

            # ---------------------------------------------------------
            # NOUVEAUTÉS DEMANDÉES
            # ---------------------------------------------------------

            # D) Skill -> Category (Regroupement des Skills)
            # On extrait la propriété "category" des Skills pour créer des nœuds Category
            print("[seed] Neo4j — Organisation des Skills par Catégorie...")
            await session.run("""
                MATCH (s:Skill)
                WHERE s.category IS NOT NULL AND s.category <> ""
                MERGE (c:Category {name: s.category})
                MERGE (s)-[:BELONGS_TO]->(c)
            """)

            # E) Certification -> Skill / Technology (Validation)
            # Si le nom ou la description de la certif mentionne un skill/tech
            print("[seed] Neo4j — Liaison des Certifications...")
            await session.run("""
                MATCH (c:Certification), (s:Skill)
                WHERE (toLower(c.nom) CONTAINS toLower(s.nom) OR toLower(c.description) CONTAINS toLower(s.nom))
                MERGE (c)-[:VALIDATES]->(s)
            """)
            
            await session.run("""
                MATCH (c:Certification), (t:Technology)
                WHERE (toLower(c.nom) CONTAINS toLower(t.nom) OR toLower(c.description) CONTAINS toLower(t.nom))
                MERGE (c)-[:VALIDATES]->(t)
            """)

        print("[seed] Neo4j — OK (Graphe enrichi et complet)")


async def main():
    print("=" * 50)
    print("SmartCity Explorer — Seed")
    print("=" * 50)
    await seed_mongo()
    await seed_neo4j()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())
