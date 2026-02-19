"""Routes API — Portfolio / Skills, Projets, Technologies, Hobbies, Expériences, Parcours (MongoDB + Neo4j)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.db.mongo import get_mongo_db
from backend.db.neo4j import get_neo4j_driver
from backend.models import Experience, Hobby, ParcoursScolaire, Projet, ProjetDetail, Skill, Techno

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# ── Skills ──────────────────────────────────────────────────────

@router.get(
    "/skills",
    response_model=list[Skill],
    summary="Liste des compétences",
    description="Retourne la liste complète des compétences depuis MongoDB.",
    response_description="Liste des compétences avec id, nom, catégorie et description.",
    responses={404: {"description": "Aucune compétence trouvée en base de données."}},
)
async def get_skills():
    db = get_mongo_db()
    docs = await db["skills"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun skill trouvé")
    return [Skill.model_validate(doc) for doc in docs]


# ── Projets ─────────────────────────────────────────────────────

@router.get(
    "/projets",
    response_model=list[Projet],
    summary="Liste des projets",
    description="Retourne la liste complète des projets depuis MongoDB (sans agrégation Neo4j).",
    response_description="Liste des projets avec nom, dates, description, entreprise et collaborateurs.",
    responses={404: {"description": "Aucun projet trouvé en base de données."}},
)
async def get_projets():
    db = get_mongo_db()
    docs = await db["projects"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun projet trouvé")
    return [Projet.model_validate(doc) for doc in docs]


@router.get(
    "/projets/details",
    response_model=list[ProjetDetail],
    summary="Liste des projets enrichis (MongoDB + Neo4j)",
    description=(
        "Retourne les projets depuis MongoDB, enrichis avec les technologies "
        "et compétences liées via les relations USES_TECHNOLOGY et REQUIRES_SKILL du graphe Neo4j."
    ),
    response_description="Liste des projets avec technologies et compétences agrégées depuis Neo4j.",
    responses={404: {"description": "Aucun projet trouvé en base de données."}},
)
async def get_projets_details():
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

@router.get(
    "/technologies",
    response_model=list[Techno],
    summary="Liste des technologies",
    description="Retourne la liste complète des technologies maîtrisées depuis MongoDB.",
    response_description="Liste des technologies avec id, nom et image.",
    responses={404: {"description": "Aucune technologie trouvée en base de données."}},
)
async def get_technologies():
    db = get_mongo_db()
    docs = await db["technologies"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucune technologie trouvée")
    return [Techno.model_validate(doc) for doc in docs]


# ── Hobbies ─────────────────────────────────────────────────────

@router.get(
    "/hobbies",
    response_model=list[Hobby],
    summary="Liste des hobbies",
    description="Retourne la liste complète des loisirs et centres d'intérêt depuis MongoDB.",
    response_description="Liste des hobbies avec id, nom et description.",
    responses={404: {"description": "Aucun hobby trouvé en base de données."}},
)
async def get_hobbies():
    db = get_mongo_db()
    docs = await db["hobbies"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun hobby trouvé")
    return [Hobby.model_validate(doc) for doc in docs]


# ── Expériences ─────────────────────────────────────────────────

@router.get(
    "/experiences",
    response_model=list[Experience],
    summary="Liste des expériences professionnelles",
    description="Retourne la liste complète des expériences professionnelles depuis MongoDB.",
    response_description="Liste des expériences avec nom, entreprise, rôle, dates et description.",
    responses={404: {"description": "Aucune expérience trouvée en base de données."}},
)
async def get_experiences():
    db = get_mongo_db()
    docs = await db["experiences"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucune expérience trouvée")
    return [Experience.model_validate(doc) for doc in docs]


# ── Parcours scolaire ──────────────────────────────────────────

@router.get(
    "/parcours-scolaire",
    response_model=list[ParcoursScolaire],
    summary="Liste du parcours scolaire",
    description="Retourne la liste complète du parcours scolaire depuis MongoDB.",
    response_description="Liste des formations avec école, diplôme, années et description.",
    responses={404: {"description": "Aucun parcours scolaire trouvé en base de données."}},
)
async def get_parcours_scolaire():
    db = get_mongo_db()
    docs = await db["educations"].find({}, {"_id": 0}).to_list()
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun parcours scolaire trouvé")
    return [ParcoursScolaire.model_validate(doc) for doc in docs]
