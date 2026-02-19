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

DATASETS_DIR = Path(__file__).resolve().parents[4] / "datasets"

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
            # B) Projets ↔ Technologies & Skills (Compétences)
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison forte: Projets ↔ Technologies & Compétences...")
            
            # 1. Project -> Technology (Si la techno est mentionnée dans le projet)
            await session.run("""
                MATCH (p:Project), (t:Technology)
                WHERE toLower(p.description) CONTAINS toLower(t.nom)
                   OR toLower(p.nom) CONTAINS toLower(t.nom)
                MERGE (p)-[:USES_TECHNOLOGY]->(t)
            """)
            
            # 2. Project -> Skill (Si la compétence ou sa catégorie est mentionnée dans le projet)
            await session.run("""
                MATCH (p:Project), (s:Skill)
                WHERE toLower(p.description) CONTAINS toLower(s.nom)
                   OR toLower(p.nom) CONTAINS toLower(s.nom)
                   OR toLower(p.description) CONTAINS toLower(s.category)
                MERGE (p)-[:REQUIRES_SKILL]->(s)
            """)

            # 3. Project -> Experience (Développé dans le cadre d'une entreprise)
            await session.run("""
                MATCH (p:Project), (e:Experience)
                WHERE toLower(p.entreprise) = toLower(e.company)
                   OR toLower(e.description) CONTAINS toLower(p.nom)
                MERGE (p)-[:DELIVERED_DURING_EXP]->(e)
            """)

            # 4. Project -> Education (Projet d'école/académique)
            await session.run("""
                MATCH (p:Project), (ed:Education)
                WHERE toLower(p.entreprise) CONTAINS toLower(ed.school_name)
                   OR toLower(p.description) CONTAINS toLower(ed.school_name)
                   OR toLower(p.description) CONTAINS "académique"
                   OR toLower(p.description) CONTAINS "école"
                MERGE (p)-[:ACADEMIC_PROJECT_OF]->(ed)
            """)

            # ---------------------------------------------------------
            # C) Expériences ↔ TOUT LE RESTE
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison riche des Expériences...")
            
            await session.run("""
                MATCH (e:Experience), (t:Technology)
                WHERE toLower(e.description) CONTAINS toLower(t.nom)
                   OR toLower(e.nom) CONTAINS toLower(t.nom)
                MERGE (e)-[:USED_TECH_AT_WORK]->(t)
            """)

            await session.run("""
                MATCH (e:Experience), (s:Skill)
                WHERE toLower(e.description) CONTAINS toLower(s.nom)
                   OR toLower(e.nom) CONTAINS toLower(s.nom)
                   OR toLower(e.role) CONTAINS toLower(s.category)
                MERGE (e)-[:APPLIED_SKILL]->(s)
            """)

            await session.run("""
                MATCH (e:Experience), (ed:Education)
                WHERE (toLower(e.type_de_poste) IN ["stage", "alternance", "internship"])
                  AND substring(toString(e.date_debut), 0, 4) = toString(ed.end_year)
                MERGE (e)-[:INTERNSHIP_FOR]->(ed)
            """)

            # ---------------------------------------------------------
            # D) Certifications ↔ TOUT LE RESTE
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison riche des Certifications...")
            
            await session.run("""
                MATCH (c:Certification), (t:Technology)
                WHERE toLower(c.nom) CONTAINS toLower(t.nom)
                   OR toLower(c.description) CONTAINS toLower(t.nom)
                MERGE (c)-[:CERTIFIES_TECH]->(t)
            """)

            await session.run("""
                MATCH (c:Certification), (s:Skill)
                WHERE toLower(c.nom) CONTAINS toLower(s.nom)
                   OR toLower(c.description) CONTAINS toLower(s.nom)
                   OR toLower(c.description) CONTAINS toLower(s.category)
                MERGE (c)-[:PROVES_SKILL]->(s)
            """)

            await session.run("""
                MATCH (c:Certification), (e:Experience)
                WHERE c.obtention_date IS NOT NULL AND e.date_debut IS NOT NULL
                  AND substring(toString(c.obtention_date), 0, 4) >= substring(toString(e.date_debut), 0, 4)
                  AND (e.date_fin IS NULL OR substring(toString(c.obtention_date), 0, 4) <= substring(toString(e.date_fin), 0, 4))
                MERGE (c)-[:OBTAINED_WHILE_AT]->(e)
            """)

            # ---------------------------------------------------------
            # E) Éducation ↔ Skills & Technologies
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison riche de l'Éducation...")
            
            await session.run("""
                MATCH (ed:Education), (t:Technology)
                WHERE toLower(ed.description) CONTAINS toLower(t.nom)
                   OR toLower(ed.degree) CONTAINS toLower(t.nom)
                MERGE (ed)-[:INTRODUCED_TECH]->(t)
            """)

            await session.run("""
                MATCH (ed:Education), (s:Skill)
                WHERE toLower(ed.description) CONTAINS toLower(s.nom)
                   OR toLower(ed.degree) CONTAINS toLower(s.nom)
                   OR toLower(ed.degree) CONTAINS toLower(s.category)
                MERGE (ed)-[:TAUGHT_SKILL]->(s)
            """)

            # ---------------------------------------------------------
            # F) Hobbies ↔ Skills & Projets
            # ---------------------------------------------------------
            print("[seed] Neo4j — Liaison riche des Hobbies...")
            
            await session.run("""
                MATCH (h:Hobby), (s:Skill)
                WHERE toLower(h.description) CONTAINS toLower(s.nom)
                   OR toLower(s.description) CONTAINS toLower(h.nom)
                MERGE (h)-[:CULTIVATES_SKILL]->(s)
            """)

            await session.run("""
                MATCH (p:Project), (h:Hobby)
                WHERE toLower(p.description) CONTAINS toLower(h.nom)
                   OR toLower(p.nom) CONTAINS toLower(h.nom)
                MERGE (p)-[:BORN_FROM_HOBBY]->(h)
            """)

            # ---------------------------------------------------------
            # G) Le cœur du réacteur : Meta-liens entre Skills et Techs
            # ---------------------------------------------------------
            print("[seed] Neo4j — Meta-liens finaux...")
            
            await session.run("""
                MATCH (s:Skill)
                WHERE s.category IS NOT NULL AND s.category <> ""
                MERGE (c:Category {name: s.category})
                MERGE (s)-[:BELONGS_TO_CATEGORY]->(c)
            """)

            await session.run("""
                MATCH (s:Skill), (t:Technology)
                WHERE toLower(s.description) CONTAINS toLower(t.nom)
                   OR toLower(s.nom) CONTAINS toLower(t.nom)
                MERGE (s)-[:IMPLEMENTED_VIA_TECH]->(t)
            """)
            
            await session.run("""
                MATCH (t1:Technology)<-[:USES_TECHNOLOGY]-(p:Project)-[:USES_TECHNOLOGY]->(t2:Technology)
                WHERE id(t1) < id(t2)
                MERGE (t1)-[rel:USED_TOGETHER_WITH]-(t2)
                ON CREATE SET rel.weight = 1
                ON MATCH SET rel.weight = rel.weight + 1
            """)

        print("[seed] Neo4j — OK (Graphe enrichi et complètement interconnecté)")

async def main():
    print("=" * 50)
    print("Portfolio — Seed")
    print("=" * 50)
    await seed_mongo()
    await seed_neo4j()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())
