"""Seed portfolio: injecte des fausses données MongoDB + relations Neo4j.

Usage:
    PYTHONPATH=src python -m backend.scripts.seed_portfolio
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from backend.database import close_databases, get_mongo_database, get_neo4j_driver


@dataclass
class SeedIds:
    person_id: str
    project_ids: list[str]
    experience_ids: list[str]
    education_ids: list[str]
    certification_ids: list[str]
    skill_ids: list[str]
    technology_ids: list[str]
    hobby_ids: list[str]


def _fake_infos_personnels() -> list[dict]:
    return [
        {
            "nom": "Dupont",
            "prenom": "Aurel",
            "contact": {
                "linkedin": "https://linkedin.com/in/aurel-dupont",
                "tel": "+33-6-12-34-56-78",
                "mail": "aurel.dupont@example.com",
            },
            "description": "Développeur backend orienté data et architecture polyglotte.",
        }
    ]


def _fake_skills() -> list[dict]:
    return [
        {"nom": "Python", "category": "backend", "description": "API et scripts data"},
        {"nom": "FastAPI", "category": "backend", "description": "Conception API REST"},
        {"nom": "MongoDB", "category": "database", "description": "Modélisation documentaire"},
        {"nom": "Neo4j", "category": "database", "description": "Requêtes Cypher et graphes"},
        {"nom": "Docker", "category": "devops", "description": "Conteneurisation et environnements"},
    ]


def _fake_technologies() -> list[dict]:
    return [
        {"nom": "FastAPI", "image": "https://dummyimg.com/fastapi.png"},
        {"nom": "MongoDB", "image": "https://dummyimg.com/mongodb.png"},
        {"nom": "Neo4j", "image": "https://dummyimg.com/neo4j.png"},
        {"nom": "Docker", "image": "https://dummyimg.com/docker.png"},
        {"nom": "React", "image": "https://dummyimg.com/react.png"},
    ]


def _fake_projects() -> list[dict]:
    return [
        {
            "nom": "Portfolio Data-Driven",
            "date_debut": "2026-01-10",
            "date_fin": None,
            "description": "Backend portfolio avec MongoDB + Neo4j.",
            "images": ["https://dummyimg.com/portfolio-1.png"],
            "entreprise": "Freelance",
            "collaborateurs": ["Alice", "Bob"],
            "lien_github": "https://github.com/example/portfolio-data-driven",
            "status": "en_cours",
        },
        {
            "nom": "Moteur de recommandations compétences",
            "date_debut": "2025-11-01",
            "date_fin": "2026-01-31",
            "description": "Recommandation de projets par skills via graphe.",
            "images": ["https://dummyimg.com/reco-1.png"],
            "entreprise": "Team-Z",
            "collaborateurs": ["Chloé"],
            "lien_github": "https://github.com/example/graph-reco",
            "status": "termine",
        },
    ]


def _fake_experiences() -> list[dict]:
    return [
        {
            "nom": "Backend Engineer",
            "description": "Conception API et modélisation des relations métier.",
            "image": "https://dummyimg.com/exp-backend.png",
            "company": "Tech Studio",
            "type_de_poste": "CDI",
            "date_debut": "2024-09-01",
            "date_fin": "2025-10-31",
            "role": "Lead Backend",
        },
        {
            "nom": "Data Engineer",
            "description": "Pipelines d'ingestion et transformations de données.",
            "image": "https://dummyimg.com/exp-data.png",
            "company": "DataWorks",
            "type_de_poste": "Freelance",
            "date_debut": "2023-03-01",
            "date_fin": "2024-08-31",
            "role": "Consultant",
        },
    ]


def _fake_education() -> list[dict]:
    return [
        {
            "school_name": "Université Lyon 1",
            "degree": "Master Informatique",
            "description": "Spécialité ingénierie logicielle.",
            "start_year": 2021,
            "end_year": 2023,
            "grade": "Bien",
        },
        {
            "school_name": "IUT Grenoble",
            "degree": "BUT Informatique",
            "description": "Bases programmation, BDD et réseaux.",
            "start_year": 2018,
            "end_year": 2021,
            "grade": "Très Bien",
        },
    ]


def _fake_certifications() -> list[dict]:
    return [
        {
            "nom": "Neo4j Certified Professional",
            "image": "https://dummyimg.com/cert-neo4j.png",
            "description": "Certification officielle Neo4j.",
            "obtention_date": "2025-06-15",
        },
        {
            "nom": "MongoDB Developer Associate",
            "image": "https://dummyimg.com/cert-mongo.png",
            "description": "Certification MongoDB développeur.",
            "obtention_date": "2025-04-10",
        },
    ]


def _fake_hobbies() -> list[dict]:
    return [
        {"nom": "Photographie", "description": "Street photography et paysages."},
        {"nom": "Course à pied", "description": "Semi-marathon et endurance."},
        {"nom": "Échecs", "description": "Tournois en ligne et en club."},
    ]


async def seed_mongo_collections() -> SeedIds:
    db = get_mongo_database()

    collections = [
        "infos_personnels",
        "projects",
        "experiences",
        "parcours_scolaire",
        "certifications",
        "skills",
        "technologies",
        "hobbies",
    ]
    for name in collections:
        await db[name].delete_many({})

    infos_result = await db["infos_personnels"].insert_many(_fake_infos_personnels())
    skill_result = await db["skills"].insert_many(_fake_skills())
    tech_result = await db["technologies"].insert_many(_fake_technologies())
    project_result = await db["projects"].insert_many(_fake_projects())
    exp_result = await db["experiences"].insert_many(_fake_experiences())
    edu_result = await db["parcours_scolaire"].insert_many(_fake_education())
    cert_result = await db["certifications"].insert_many(_fake_certifications())
    hobby_result = await db["hobbies"].insert_many(_fake_hobbies())

    return SeedIds(
        person_id=str(infos_result.inserted_ids[0]),
        project_ids=[str(value) for value in project_result.inserted_ids],
        experience_ids=[str(value) for value in exp_result.inserted_ids],
        education_ids=[str(value) for value in edu_result.inserted_ids],
        certification_ids=[str(value) for value in cert_result.inserted_ids],
        skill_ids=[str(value) for value in skill_result.inserted_ids],
        technology_ids=[str(value) for value in tech_result.inserted_ids],
        hobby_ids=[str(value) for value in hobby_result.inserted_ids],
    )


async def seed_neo4j_graph(seed_ids: SeedIds) -> None:
    driver = get_neo4j_driver()

    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")

        await session.run(
            """
            MERGE (p:Person {mongo_id: $mongo_id})
            SET p.nom = $nom,
                p.prenom = $prenom
            """,
            mongo_id=seed_ids.person_id,
            nom="Dupont",
            prenom="Aurel",
        )

        skill_names = ["Python", "FastAPI", "MongoDB", "Neo4j", "Docker"]
        for mongo_id, name in zip(seed_ids.skill_ids, skill_names):
            await session.run(
                """
                MERGE (s:Skill {mongo_id: $mongo_id})
                SET s.nom = $nom
                """,
                mongo_id=mongo_id,
                nom=name,
            )

        tech_names = ["FastAPI", "MongoDB", "Neo4j", "Docker", "React"]
        for mongo_id, name in zip(seed_ids.technology_ids, tech_names):
            await session.run(
                """
                MERGE (t:Technology {mongo_id: $mongo_id})
                SET t.nom = $nom
                """,
                mongo_id=mongo_id,
                nom=name,
            )

        project_names = [
            "Portfolio Data-Driven",
            "Moteur de recommandations compétences",
        ]
        for mongo_id, name in zip(seed_ids.project_ids, project_names):
            await session.run(
                """
                MERGE (pr:Project {mongo_id: $mongo_id})
                SET pr.nom = $nom
                """,
                mongo_id=mongo_id,
                nom=name,
            )

        experience_names = ["Backend Engineer", "Data Engineer"]
        for mongo_id, name in zip(seed_ids.experience_ids, experience_names):
            await session.run(
                """
                MERGE (e:Experience {mongo_id: $mongo_id})
                SET e.nom = $nom
                """,
                mongo_id=mongo_id,
                nom=name,
            )

        cert_names = ["Neo4j Certified Professional", "MongoDB Developer Associate"]
        for mongo_id, name in zip(seed_ids.certification_ids, cert_names):
            await session.run(
                """
                MERGE (c:Certification {mongo_id: $mongo_id})
                SET c.nom = $nom
                """,
                mongo_id=mongo_id,
                nom=name,
            )

        for project_id in seed_ids.project_ids:
            await session.run(
                """
                MATCH (p:Person {mongo_id: $person_id})
                MATCH (pr:Project {mongo_id: $project_id})
                MERGE (p)-[:WORKED_ON]->(pr)
                """,
                person_id=seed_ids.person_id,
                project_id=project_id,
            )

        # Project 1 uses FastAPI, MongoDB, Neo4j, Docker; Project 2 uses Python/FastAPI + Neo4j
        project_1, project_2 = seed_ids.project_ids
        fastapi_id, mongo_id, neo4j_id, docker_id, _react_id = seed_ids.technology_ids
        python_skill_id, fastapi_skill_id, mongodb_skill_id, neo4j_skill_id, docker_skill_id = seed_ids.skill_ids

        uses_pairs = [
            (project_1, fastapi_id),
            (project_1, mongo_id),
            (project_1, neo4j_id),
            (project_1, docker_id),
            (project_2, fastapi_id),
            (project_2, neo4j_id),
        ]
        for pr_id, tech_id in uses_pairs:
            await session.run(
                """
                MATCH (pr:Project {mongo_id: $project_id})
                MATCH (t:Technology {mongo_id: $technology_id})
                MERGE (pr)-[:USES_TECH]->(t)
                """,
                project_id=pr_id,
                technology_id=tech_id,
            )

        requires_pairs = [
            (project_1, python_skill_id),
            (project_1, fastapi_skill_id),
            (project_1, mongodb_skill_id),
            (project_1, neo4j_skill_id),
            (project_1, docker_skill_id),
            (project_2, python_skill_id),
            (project_2, fastapi_skill_id),
            (project_2, neo4j_skill_id),
        ]
        for pr_id, skill_id in requires_pairs:
            await session.run(
                """
                MATCH (pr:Project {mongo_id: $project_id})
                MATCH (s:Skill {mongo_id: $skill_id})
                MERGE (pr)-[:REQUIRES_SKILL]->(s)
                """,
                project_id=pr_id,
                skill_id=skill_id,
            )

        exp_1, exp_2 = seed_ids.experience_ids
        gained_pairs = [
            (exp_1, fastapi_skill_id),
            (exp_1, mongodb_skill_id),
            (exp_1, neo4j_skill_id),
            (exp_2, python_skill_id),
            (exp_2, docker_skill_id),
        ]
        for exp_id, skill_id in gained_pairs:
            await session.run(
                """
                MATCH (e:Experience {mongo_id: $experience_id})
                MATCH (s:Skill {mongo_id: $skill_id})
                MERGE (e)-[:GAINED_SKILL]->(s)
                """,
                experience_id=exp_id,
                skill_id=skill_id,
            )

        related_pairs = [(exp_1, project_1), (exp_2, project_2)]
        for exp_id, pr_id in related_pairs:
            await session.run(
                """
                MATCH (e:Experience {mongo_id: $experience_id})
                MATCH (pr:Project {mongo_id: $project_id})
                MERGE (e)-[:RELATED_TO_PROJECT]->(pr)
                """,
                experience_id=exp_id,
                project_id=pr_id,
            )

        cert_1, cert_2 = seed_ids.certification_ids
        validates_pairs = [
            (cert_1, "Technology", neo4j_id),
            (cert_1, "Skill", neo4j_skill_id),
            (cert_2, "Technology", mongo_id),
            (cert_2, "Skill", mongodb_skill_id),
        ]
        for cert_id, target_label, target_id in validates_pairs:
            if target_label == "Technology":
                await session.run(
                    """
                    MATCH (c:Certification {mongo_id: $certification_id})
                    MATCH (t:Technology {mongo_id: $target_id})
                    MERGE (c)-[:VALIDATES]->(t)
                    """,
                    certification_id=cert_id,
                    target_id=target_id,
                )
            else:
                await session.run(
                    """
                    MATCH (c:Certification {mongo_id: $certification_id})
                    MATCH (s:Skill {mongo_id: $target_id})
                    MERGE (c)-[:VALIDATES]->(s)
                    """,
                    certification_id=cert_id,
                    target_id=target_id,
                )


async def main() -> None:
    print("[seed-portfolio] Start")
    seed_ids = await seed_mongo_collections()
    await seed_neo4j_graph(seed_ids)
    print("[seed-portfolio] Mongo collections alimentées")
    print("[seed-portfolio] Neo4j relations créées")
    await close_databases()
    print("[seed-portfolio] Done")


if __name__ == "__main__":
    asyncio.run(main())
