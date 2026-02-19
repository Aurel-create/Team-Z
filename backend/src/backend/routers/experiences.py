"""Routes Expériences avec synchronisation MongoDB + Neo4j."""

from __future__ import annotations

from datetime import date

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from backend.database import get_mongo_database, get_neo4j_driver
from backend.models import Experience, ExperienceCreate, ExperienceUpdate
from backend.models.common import mongo_to_api

router = APIRouter(prefix="/experiences", tags=["experiences"])


def _serialize_payload(payload: dict) -> dict:
    clean = {}
    for key, value in payload.items():
        if isinstance(value, date):
            clean[key] = value.isoformat()
        else:
            clean[key] = value
    return clean


async def _sync_experience_to_graph(experience_id: str, data: dict) -> None:
    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (e:Experience {mongo_id: $mongo_id})
            SET e.nom = $nom,
                e.description = $description,
                e.company = $company,
                e.type_de_poste = $type_de_poste,
                e.role = $role,
                e.date_debut = $date_debut,
                e.date_fin = $date_fin
            """,
            mongo_id=experience_id,
            nom=data.get("nom"),
            description=data.get("description"),
            company=data.get("company"),
            type_de_poste=data.get("type_de_poste"),
            role=data.get("role"),
            date_debut=data.get("date_debut"),
            date_fin=data.get("date_fin"),
        )

        await session.run(
            """
            MATCH (e:Experience {mongo_id: $experience_id})
            OPTIONAL MATCH (e)-[rel:GAINED_SKILL]->(:Skill)
            DELETE rel
            """,
            experience_id=experience_id,
        )
        for skill_id in data.get("skill_ids", []):
            await session.run(
                """
                MATCH (e:Experience {mongo_id: $experience_id})
                MERGE (s:Skill {mongo_id: $skill_id})
                MERGE (e)-[:GAINED_SKILL]->(s)
                """,
                experience_id=experience_id,
                skill_id=skill_id,
            )

        await session.run(
            """
            MATCH (e:Experience {mongo_id: $experience_id})
            OPTIONAL MATCH (e)-[rel:RELATED_TO_PROJECT]->(:Project)
            DELETE rel
            """,
            experience_id=experience_id,
        )
        for project_id in data.get("project_ids", []):
            await session.run(
                """
                MATCH (e:Experience {mongo_id: $experience_id})
                MERGE (p:Project {mongo_id: $project_id})
                MERGE (e)-[:RELATED_TO_PROJECT]->(p)
                """,
                experience_id=experience_id,
                project_id=project_id,
            )


@router.get("", response_model=list[Experience])
async def list_experiences() -> list[Experience]:
    collection = get_mongo_database()["experiences"]
    docs = await collection.find().to_list(length=500)
    return [Experience(**mongo_to_api(doc)) for doc in docs]


@router.get("/{experience_id}", response_model=Experience)
async def get_experience(experience_id: str) -> Experience:
    collection = get_mongo_database()["experiences"]
    try:
        object_id = ObjectId(experience_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="experience_id invalide") from exc

    doc = await collection.find_one({"_id": object_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Expérience introuvable")
    return Experience(**mongo_to_api(doc))


@router.post("", response_model=Experience, status_code=status.HTTP_201_CREATED)
async def create_experience(payload: ExperienceCreate) -> Experience:
    collection = get_mongo_database()["experiences"]
    data = payload.model_dump()
    serialized = _serialize_payload(data)

    document = {
        "nom": data["nom"],
        "description": data.get("description"),
        "image": data.get("image"),
        "company": data.get("company"),
        "type_de_poste": data.get("type_de_poste"),
        "date_debut": serialized.get("date_debut"),
        "date_fin": serialized.get("date_fin"),
        "role": data.get("role"),
    }

    result = await collection.insert_one(document)
    experience_id = str(result.inserted_id)
    await _sync_experience_to_graph(experience_id, serialized)

    created = await collection.find_one({"_id": result.inserted_id})
    if created is None:
        raise HTTPException(status_code=500, detail="Expérience non créée")
    return Experience(**mongo_to_api(created))


@router.put("/{experience_id}", response_model=Experience)
async def update_experience(experience_id: str, payload: ExperienceUpdate) -> Experience:
    collection = get_mongo_database()["experiences"]
    try:
        object_id = ObjectId(experience_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="experience_id invalide") from exc

    existing = await collection.find_one({"_id": object_id})
    if existing is None:
        raise HTTPException(status_code=404, detail="Expérience introuvable")

    data = payload.model_dump(exclude_none=True)
    serialized = _serialize_payload(data)

    mongo_updates = {
        key: value
        for key, value in serialized.items()
        if key in {"nom", "description", "image", "company", "type_de_poste", "date_debut", "date_fin", "role"}
    }

    if mongo_updates:
        await collection.update_one({"_id": object_id}, {"$set": mongo_updates})

    merged_graph_data = _serialize_payload({**mongo_to_api(existing), **serialized})
    await _sync_experience_to_graph(experience_id, merged_graph_data)

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=500, detail="Expérience introuvable après mise à jour")
    return Experience(**mongo_to_api(updated))


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(experience_id: str) -> None:
    collection = get_mongo_database()["experiences"]
    try:
        object_id = ObjectId(experience_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="experience_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expérience introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (e:Experience {mongo_id: $experience_id})
            DETACH DELETE e
            """,
            experience_id=experience_id,
        )
