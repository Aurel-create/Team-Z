"""Routes compétences : SKILL, TECHNOLOGIE, CERTIFICATION + recherche graphe."""

from __future__ import annotations

from datetime import date

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from backend.database import get_mongo_database, get_neo4j_driver
from backend.models import (
    Certification,
    CertificationCreate,
    CertificationUpdate,
    Project,
    Skill,
    SkillCreate,
    SkillUpdate,
    Technology,
    TechnologyCreate,
    TechnologyUpdate,
)
from backend.models.common import mongo_to_api

router = APIRouter(tags=["skills-and-tech"])


def _serialize_payload(payload: dict) -> dict:
    clean = {}
    for key, value in payload.items():
        if isinstance(value, date):
            clean[key] = value.isoformat()
        else:
            clean[key] = value
    return clean


@router.post("/skills", response_model=Skill, status_code=status.HTTP_201_CREATED)
async def create_skill(payload: SkillCreate) -> Skill:
    collection = get_mongo_database()["skills"]
    doc = payload.model_dump()
    result = await collection.insert_one(doc)
    mongo_id = str(result.inserted_id)

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (s:Skill {mongo_id: $mongo_id})
            SET s.nom = $nom,
                s.category = $category,
                s.description = $description
            """,
            mongo_id=mongo_id,
            nom=doc.get("nom"),
            category=doc.get("category"),
            description=doc.get("description"),
        )

    created = await collection.find_one({"_id": result.inserted_id})
    return Skill(**mongo_to_api(created))


@router.get("/skills", response_model=list[Skill])
async def list_skills() -> list[Skill]:
    docs = await get_mongo_database()["skills"].find().to_list(length=500)
    return [Skill(**mongo_to_api(doc)) for doc in docs]


@router.put("/skills/{skill_id}", response_model=Skill)
async def update_skill(skill_id: str, payload: SkillUpdate) -> Skill:
    collection = get_mongo_database()["skills"]
    try:
        object_id = ObjectId(skill_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="skill_id invalide") from exc

    updates = payload.model_dump(exclude_none=True)
    if updates:
        await collection.update_one({"_id": object_id}, {"$set": updates})

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=404, detail="Skill introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (s:Skill {mongo_id: $mongo_id})
            SET s.nom = $nom,
                s.category = $category,
                s.description = $description
            """,
            mongo_id=skill_id,
            nom=updated.get("nom"),
            category=updated.get("category"),
            description=updated.get("description"),
        )

    return Skill(**mongo_to_api(updated))


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str) -> None:
    collection = get_mongo_database()["skills"]
    try:
        object_id = ObjectId(skill_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="skill_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Skill introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (s:Skill {mongo_id: $skill_id})
            DETACH DELETE s
            """,
            skill_id=skill_id,
        )


@router.post("/technologies", response_model=Technology, status_code=status.HTTP_201_CREATED)
async def create_technology(payload: TechnologyCreate) -> Technology:
    collection = get_mongo_database()["technologies"]
    doc = payload.model_dump()
    result = await collection.insert_one(doc)
    mongo_id = str(result.inserted_id)

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (t:Technology {mongo_id: $mongo_id})
            SET t.nom = $nom,
                t.image = $image
            """,
            mongo_id=mongo_id,
            nom=doc.get("nom"),
            image=doc.get("image"),
        )

    created = await collection.find_one({"_id": result.inserted_id})
    return Technology(**mongo_to_api(created))


@router.get("/technologies", response_model=list[Technology])
async def list_technologies() -> list[Technology]:
    docs = await get_mongo_database()["technologies"].find().to_list(length=500)
    return [Technology(**mongo_to_api(doc)) for doc in docs]


@router.put("/technologies/{technology_id}", response_model=Technology)
async def update_technology(technology_id: str, payload: TechnologyUpdate) -> Technology:
    collection = get_mongo_database()["technologies"]
    try:
        object_id = ObjectId(technology_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="technology_id invalide") from exc

    updates = payload.model_dump(exclude_none=True)
    if updates:
        await collection.update_one({"_id": object_id}, {"$set": updates})

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=404, detail="Technologie introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (t:Technology {mongo_id: $mongo_id})
            SET t.nom = $nom,
                t.image = $image
            """,
            mongo_id=technology_id,
            nom=updated.get("nom"),
            image=updated.get("image"),
        )

    return Technology(**mongo_to_api(updated))


@router.delete("/technologies/{technology_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_technology(technology_id: str) -> None:
    collection = get_mongo_database()["technologies"]
    try:
        object_id = ObjectId(technology_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="technology_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Technologie introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (t:Technology {mongo_id: $technology_id})
            DETACH DELETE t
            """,
            technology_id=technology_id,
        )


@router.post("/certifications", response_model=Certification, status_code=status.HTTP_201_CREATED)
async def create_certification(payload: CertificationCreate) -> Certification:
    collection = get_mongo_database()["certifications"]
    data = payload.model_dump()
    serialized = _serialize_payload(data)

    doc = {
        "nom": data["nom"],
        "image": data.get("image"),
        "description": data.get("description"),
        "obtention_date": serialized.get("obtention_date"),
    }
    result = await collection.insert_one(doc)
    certification_id = str(result.inserted_id)

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (c:Certification {mongo_id: $mongo_id})
            SET c.nom = $nom,
                c.image = $image,
                c.description = $description,
                c.obtention_date = $obtention_date
            """,
            mongo_id=certification_id,
            nom=doc.get("nom"),
            image=doc.get("image"),
            description=doc.get("description"),
            obtention_date=doc.get("obtention_date"),
        )

        for skill_id in data.get("validates_skill_ids", []):
            await session.run(
                """
                MATCH (c:Certification {mongo_id: $certification_id})
                MERGE (s:Skill {mongo_id: $skill_id})
                MERGE (c)-[:VALIDATES]->(s)
                """,
                certification_id=certification_id,
                skill_id=skill_id,
            )

        for technology_id in data.get("validates_technology_ids", []):
            await session.run(
                """
                MATCH (c:Certification {mongo_id: $certification_id})
                MERGE (t:Technology {mongo_id: $technology_id})
                MERGE (c)-[:VALIDATES]->(t)
                """,
                certification_id=certification_id,
                technology_id=technology_id,
            )

    created = await collection.find_one({"_id": result.inserted_id})
    return Certification(**mongo_to_api(created))


@router.get("/certifications", response_model=list[Certification])
async def list_certifications() -> list[Certification]:
    docs = await get_mongo_database()["certifications"].find().to_list(length=500)
    return [Certification(**mongo_to_api(doc)) for doc in docs]


@router.put("/certifications/{certification_id}", response_model=Certification)
async def update_certification(certification_id: str, payload: CertificationUpdate) -> Certification:
    collection = get_mongo_database()["certifications"]
    try:
        object_id = ObjectId(certification_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="certification_id invalide") from exc

    updates = _serialize_payload(payload.model_dump(exclude_none=True))
    if updates:
        mongo_updates = {k: v for k, v in updates.items() if k in {"nom", "image", "description", "obtention_date"}}
        if mongo_updates:
            await collection.update_one({"_id": object_id}, {"$set": mongo_updates})

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=404, detail="Certification introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (c:Certification {mongo_id: $mongo_id})
            SET c.nom = $nom,
                c.image = $image,
                c.description = $description,
                c.obtention_date = $obtention_date
            """,
            mongo_id=certification_id,
            nom=updated.get("nom"),
            image=updated.get("image"),
            description=updated.get("description"),
            obtention_date=updated.get("obtention_date"),
        )

        if "validates_skill_ids" in updates:
            await session.run(
                """
                MATCH (c:Certification {mongo_id: $certification_id})
                OPTIONAL MATCH (c)-[rel:VALIDATES]->(:Skill)
                DELETE rel
                """,
                certification_id=certification_id,
            )
            for skill_id in updates["validates_skill_ids"]:
                await session.run(
                    """
                    MATCH (c:Certification {mongo_id: $certification_id})
                    MERGE (s:Skill {mongo_id: $skill_id})
                    MERGE (c)-[:VALIDATES]->(s)
                    """,
                    certification_id=certification_id,
                    skill_id=skill_id,
                )

        if "validates_technology_ids" in updates:
            await session.run(
                """
                MATCH (c:Certification {mongo_id: $certification_id})
                OPTIONAL MATCH (c)-[rel:VALIDATES]->(:Technology)
                DELETE rel
                """,
                certification_id=certification_id,
            )
            for technology_id in updates["validates_technology_ids"]:
                await session.run(
                    """
                    MATCH (c:Certification {mongo_id: $certification_id})
                    MERGE (t:Technology {mongo_id: $technology_id})
                    MERGE (c)-[:VALIDATES]->(t)
                    """,
                    certification_id=certification_id,
                    technology_id=technology_id,
                )

    return Certification(**mongo_to_api(updated))


@router.delete("/certifications/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(certification_id: str) -> None:
    collection = get_mongo_database()["certifications"]
    try:
        object_id = ObjectId(certification_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="certification_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Certification introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (c:Certification {mongo_id: $certification_id})
            DETACH DELETE c
            """,
            certification_id=certification_id,
        )


@router.get("/skills/{name}/projects", response_model=list[Project])
async def get_projects_by_skill_name(name: str) -> list[Project]:
    driver = get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (s:Skill)
            WHERE toLower(s.nom) = toLower($name)
            MATCH (s)<-[:REQUIRES_SKILL]-(p:Project)
            RETURN DISTINCT p.mongo_id AS mongo_id
            """,
            name=name,
        )
        records = await result.data()

    mongo_ids = [record["mongo_id"] for record in records if record.get("mongo_id")]
    if not mongo_ids:
        return []

    object_ids = []
    for mongo_id in mongo_ids:
        try:
            object_ids.append(ObjectId(mongo_id))
        except Exception:
            continue

    if not object_ids:
        return []

    projects_collection = get_mongo_database()["projects"]
    docs = await projects_collection.find({"_id": {"$in": object_ids}}).to_list(length=500)
    return [Project(**mongo_to_api(doc)) for doc in docs]
