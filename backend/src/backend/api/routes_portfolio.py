"""Routes API — Portfolio / Skills, Projets, Technologies, Hobbies, Expériences, Parcours (MongoDB)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.db.mongo import get_mongo_db
from backend.db.neo4j import get_neo4j_driver
from backend.models import Experience, Hobby, ParcoursScolaire, Projet, ProjetDetail, Skill, Techno

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# ── Skills ──────────────────────────────────────────────────────

@router.get("/skills", response_model=list[Skill])
async def get_skills():
    """Récupère toutes les compétences."""
    db = get_mongo_db()
    docs = await db["skills"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun skill trouvé")
    return [Skill.model_validate(doc) for doc in docs]


# ── Projets ─────────────────────────────────────────────────────

@router.get("/projets", response_model=list[Projet])
async def get_projets():
    """Récupère tous les projets."""
    db = get_mongo_db()
    docs = await db["projects"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun projet trouvé")
    return [Projet.model_validate(doc) for doc in docs]


@router.get("/projets/details", response_model=list[ProjetDetail])
async def get_projets_details():
    """Récupère tous les projets enrichis avec leurs technologies et compétences (Neo4j)."""
    db = get_mongo_db()
    docs = await db["projects"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun projet trouvé")

    # Récupérer les technologies et compétences liées depuis Neo4j
    driver = get_neo4j_driver()
    async with driver.session() as session:
        tech_result = await session.run("""
            MATCH (p:Project)-[:USES_TECHNOLOGY]->(t:Technology)
            RETURN p.nom AS projet, collect(t.nom) AS technologies
        """)
        tech_records = [r async for r in tech_result]

        skill_result = await session.run("""
            MATCH (p:Project)-[:REQUIRES_SKILL]->(s:Skill)
            RETURN p.nom AS projet, collect(s.nom) AS skills
        """)
        skill_records = [r async for r in skill_result]

    tech_map = {r["projet"]: r["technologies"] for r in tech_records}
    skill_map = {r["projet"]: r["skills"] for r in skill_records}

    # Fusionner MongoDB + Neo4j
    projets = []
    for doc in docs:
        projet = Projet.model_validate(doc)
        projets.append(ProjetDetail(
            **projet.model_dump(),
            technologies=tech_map.get(projet.nom, []),
            skills=skill_map.get(projet.nom, []),
        ))

    return projets


# ── Technologies ────────────────────────────────────────────────

@router.get("/technologies", response_model=list[Techno])
async def get_technologies():
    """Récupère toutes les technologies."""
    db = get_mongo_db()
    docs = await db["technologies"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucune technologie trouvée")
    return [Techno.model_validate(doc) for doc in docs]


# ── Hobbies ─────────────────────────────────────────────────────

@router.get("/hobbies", response_model=list[Hobby])
async def get_hobbies():
    """Récupère tous les hobbies."""
    db = get_mongo_db()
    docs = await db["hobbies"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun hobby trouvé")
    return [Hobby.model_validate(doc) for doc in docs]


# ── Expériences ─────────────────────────────────────────────────

@router.get("/experiences", response_model=list[Experience])
async def get_experiences():
    """Récupère toutes les expériences."""
    db = get_mongo_db()
    docs = await db["experiences"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucune expérience trouvée")
    return [Experience.model_validate(doc) for doc in docs]


# ── Parcours scolaire ──────────────────────────────────────────

@router.get("/parcours-scolaire", response_model=list[ParcoursScolaire])
async def get_parcours_scolaire():
    """Récupère le parcours scolaire."""
    db = get_mongo_db()
    docs = await db["educations"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun parcours scolaire trouvé")
    return [ParcoursScolaire.model_validate(doc) for doc in docs]

