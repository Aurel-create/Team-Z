"""Routes Projets avec synchronisation MongoDB + Neo4j."""

from __future__ import annotations

from datetime import date

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from backend.database import get_mongo_database, get_neo4j_driver
from backend.models import Project, ProjectCreate, ProjectUpdate
from backend.models.common import mongo_to_api

router = APIRouter(prefix="/projects", tags=["projects"])


def _serialize_project_payload(payload: dict) -> dict:
    clean = {}
    for key, value in payload.items():
        if isinstance(value, date):
            clean[key] = value.isoformat()
        else:
            clean[key] = value
    return clean


async def _sync_project_to_graph(project_id: str, data: dict) -> None:
    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (p:Project {mongo_id: $mongo_id})
            SET p.nom = $nom,
                p.description = $description,
                p.status = $status,
                p.entreprise = $entreprise,
                p.date_debut = $date_debut,
                p.date_fin = $date_fin,
                p.lien_github = $lien_github
            """,
            mongo_id=project_id,
            nom=data.get("nom"),
            description=data.get("description"),
            status=data.get("status"),
            entreprise=data.get("entreprise"),
            date_debut=data.get("date_debut"),
            date_fin=data.get("date_fin"),
            lien_github=data.get("lien_github"),
        )

        await session.run(
            """
            MATCH (p:Project {mongo_id: $project_id})
            OPTIONAL MATCH (person:Person)-[rel:WORKED_ON]->(p)
            DELETE rel
            """,
            project_id=project_id,
        )
        for person_id in data.get("person_ids", []):
            await session.run(
                """
                MATCH (p:Project {mongo_id: $project_id})
                MERGE (person:Person {mongo_id: $person_id})
                MERGE (person)-[:WORKED_ON]->(p)
                """,
                project_id=project_id,
                person_id=person_id,
            )

        await session.run(
            """
            MATCH (p:Project {mongo_id: $project_id})
            OPTIONAL MATCH (p)-[rel:USES_TECH]->(:Technology)
            DELETE rel
            """,
            project_id=project_id,
        )
        for tech_id in data.get("technology_ids", []):
            await session.run(
                """
                MATCH (p:Project {mongo_id: $project_id})
                MERGE (t:Technology {mongo_id: $tech_id})
                MERGE (p)-[:USES_TECH]->(t)
                """,
                project_id=project_id,
                tech_id=tech_id,
            )

        await session.run(
            """
            MATCH (p:Project {mongo_id: $project_id})
            OPTIONAL MATCH (p)-[rel:REQUIRES_SKILL]->(:Skill)
            DELETE rel
            """,
            project_id=project_id,
        )
        for skill_id in data.get("skill_ids", []):
            await session.run(
                """
                MATCH (p:Project {mongo_id: $project_id})
                MERGE (s:Skill {mongo_id: $skill_id})
                MERGE (p)-[:REQUIRES_SKILL]->(s)
                """,
                project_id=project_id,
                skill_id=skill_id,
            )


@router.get("", response_model=list[Project])
async def list_projects() -> list[Project]:
    collection = get_mongo_database()["projects"]
    docs = await collection.find().to_list(length=500)
    return [Project(**mongo_to_api(doc)) for doc in docs]


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str) -> Project:
    collection = get_mongo_database()["projects"]
    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="project_id invalide") from exc

    doc = await collection.find_one({"_id": object_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    return Project(**mongo_to_api(doc))


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate) -> Project:
    collection = get_mongo_database()["projects"]
    data = payload.model_dump()
    graph_data = _serialize_project_payload(data)
    document = {
        "nom": data["nom"],
        "date_debut": graph_data.get("date_debut"),
        "date_fin": graph_data.get("date_fin"),
        "description": data.get("description"),
        "images": data.get("images", []),
        "entreprise": data.get("entreprise"),
        "collaborateurs": data.get("collaborateurs", []),
        "lien_github": data.get("lien_github"),
        "status": data.get("status"),
    }

    result = await collection.insert_one(document)
    project_id = str(result.inserted_id)
    await _sync_project_to_graph(project_id, graph_data)

    created = await collection.find_one({"_id": result.inserted_id})
    if created is None:
        raise HTTPException(status_code=500, detail="Projet non créé")
    return Project(**mongo_to_api(created))


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, payload: ProjectUpdate) -> Project:
    collection = get_mongo_database()["projects"]
    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="project_id invalide") from exc

    existing = await collection.find_one({"_id": object_id})
    if existing is None:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    data = payload.model_dump(exclude_none=True)
    graph_data = _serialize_project_payload(data)

    mongo_updates = {
        key: value
        for key, value in graph_data.items()
        if key in {"nom", "date_debut", "date_fin", "description", "images", "entreprise", "collaborateurs", "lien_github", "status"}
    }

    if mongo_updates:
        await collection.update_one({"_id": object_id}, {"$set": mongo_updates})

    merged_graph_data = _serialize_project_payload({**mongo_to_api(existing), **graph_data})
    await _sync_project_to_graph(project_id, merged_graph_data)

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=500, detail="Projet introuvable après mise à jour")
    return Project(**mongo_to_api(updated))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str) -> None:
    collection = get_mongo_database()["projects"]
    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="project_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Projet introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (p:Project {mongo_id: $project_id})
            DETACH DELETE p
            """,
            project_id=project_id,
        )
