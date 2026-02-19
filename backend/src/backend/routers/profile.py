"""Routes Profil : infos personnelles, parcours scolaire, hobbies, agrégation."""

from __future__ import annotations

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from backend.database import get_mongo_database, get_neo4j_driver
from backend.models import (
    Education,
    EducationCreate,
    EducationUpdate,
    GlobalPortfolioResponse,
    Hobby,
    HobbyCreate,
    HobbyUpdate,
    InfosPersonnels,
    InfosPersonnelsCreate,
    InfosPersonnelsUpdate,
)
from backend.models.common import mongo_to_api

router = APIRouter(prefix="/profile", tags=["profile"])


async def _sync_person(person_id: str, payload: dict) -> None:
    contact = payload.get("contact") or {}
    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MERGE (p:Person {mongo_id: $mongo_id})
            SET p.nom = $nom,
                p.prenom = $prenom,
                p.description = $description,
                p.linkedin = $linkedin,
                p.tel = $tel,
                p.mail = $mail
            """,
            mongo_id=person_id,
            nom=payload.get("nom"),
            prenom=payload.get("prenom"),
            description=payload.get("description"),
            linkedin=contact.get("linkedin"),
            tel=contact.get("tel"),
            mail=contact.get("mail"),
        )


@router.post("/infos", response_model=InfosPersonnels, status_code=status.HTTP_201_CREATED)
async def create_infos(payload: InfosPersonnelsCreate) -> InfosPersonnels:
    collection = get_mongo_database()["infos_personnels"]
    data = payload.model_dump()
    result = await collection.insert_one(data)
    mongo_id = str(result.inserted_id)
    await _sync_person(mongo_id, data)

    created = await collection.find_one({"_id": result.inserted_id})
    return InfosPersonnels(**mongo_to_api(created))


@router.get("/infos", response_model=list[InfosPersonnels])
async def list_infos() -> list[InfosPersonnels]:
    docs = await get_mongo_database()["infos_personnels"].find().to_list(length=50)
    return [InfosPersonnels(**mongo_to_api(doc)) for doc in docs]


@router.put("/infos/{info_id}", response_model=InfosPersonnels)
async def update_infos(info_id: str, payload: InfosPersonnelsUpdate) -> InfosPersonnels:
    collection = get_mongo_database()["infos_personnels"]
    try:
        object_id = ObjectId(info_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="info_id invalide") from exc

    updates = payload.model_dump(exclude_none=True)
    if updates:
        await collection.update_one({"_id": object_id}, {"$set": updates})

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=404, detail="Profil introuvable")

    await _sync_person(info_id, mongo_to_api(updated))
    return InfosPersonnels(**mongo_to_api(updated))


@router.delete("/infos/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_infos(info_id: str) -> None:
    collection = get_mongo_database()["infos_personnels"]
    try:
        object_id = ObjectId(info_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="info_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profil introuvable")

    driver = get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            """
            MATCH (p:Person {mongo_id: $info_id})
            DETACH DELETE p
            """,
            info_id=info_id,
        )


@router.post("/education", response_model=Education, status_code=status.HTTP_201_CREATED)
async def create_education(payload: EducationCreate) -> Education:
    collection = get_mongo_database()["parcours_scolaire"]
    result = await collection.insert_one(payload.model_dump())
    created = await collection.find_one({"_id": result.inserted_id})
    return Education(**mongo_to_api(created))


@router.get("/education", response_model=list[Education])
async def list_education() -> list[Education]:
    docs = await get_mongo_database()["parcours_scolaire"].find().to_list(length=200)
    return [Education(**mongo_to_api(doc)) for doc in docs]


@router.put("/education/{education_id}", response_model=Education)
async def update_education(education_id: str, payload: EducationUpdate) -> Education:
    collection = get_mongo_database()["parcours_scolaire"]
    try:
        object_id = ObjectId(education_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="education_id invalide") from exc

    updates = payload.model_dump(exclude_none=True)
    if updates:
        await collection.update_one({"_id": object_id}, {"$set": updates})

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=404, detail="Parcours introuvable")

    return Education(**mongo_to_api(updated))


@router.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(education_id: str) -> None:
    collection = get_mongo_database()["parcours_scolaire"]
    try:
        object_id = ObjectId(education_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="education_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Parcours introuvable")


@router.post("/hobbies", response_model=Hobby, status_code=status.HTTP_201_CREATED)
async def create_hobby(payload: HobbyCreate) -> Hobby:
    collection = get_mongo_database()["hobbies"]
    result = await collection.insert_one(payload.model_dump())
    created = await collection.find_one({"_id": result.inserted_id})
    return Hobby(**mongo_to_api(created))


@router.get("/hobbies", response_model=list[Hobby])
async def list_hobbies() -> list[Hobby]:
    docs = await get_mongo_database()["hobbies"].find().to_list(length=200)
    return [Hobby(**mongo_to_api(doc)) for doc in docs]


@router.put("/hobbies/{hobby_id}", response_model=Hobby)
async def update_hobby(hobby_id: str, payload: HobbyUpdate) -> Hobby:
    collection = get_mongo_database()["hobbies"]
    try:
        object_id = ObjectId(hobby_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="hobby_id invalide") from exc

    updates = payload.model_dump(exclude_none=True)
    if updates:
        await collection.update_one({"_id": object_id}, {"$set": updates})

    updated = await collection.find_one({"_id": object_id})
    if updated is None:
        raise HTTPException(status_code=404, detail="Hobby introuvable")

    return Hobby(**mongo_to_api(updated))


@router.delete("/hobbies/{hobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hobby(hobby_id: str) -> None:
    collection = get_mongo_database()["hobbies"]
    try:
        object_id = ObjectId(hobby_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="hobby_id invalide") from exc

    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hobby introuvable")


@router.get("/global", response_model=GlobalPortfolioResponse)
async def get_global_portfolio() -> GlobalPortfolioResponse:
    db = get_mongo_database()

    infos = [InfosPersonnels(**mongo_to_api(doc)) for doc in await db["infos_personnels"].find().to_list(length=20)]
    projects = [
        {
            **mongo_to_api(doc),
            "date_debut": mongo_to_api(doc).get("date_debut"),
            "date_fin": mongo_to_api(doc).get("date_fin"),
        }
        for doc in await db["projects"].find().to_list(length=500)
    ]
    experiences = [
        {
            **mongo_to_api(doc),
            "date_debut": mongo_to_api(doc).get("date_debut"),
            "date_fin": mongo_to_api(doc).get("date_fin"),
        }
        for doc in await db["experiences"].find().to_list(length=500)
    ]
    parcours = [Education(**mongo_to_api(doc)) for doc in await db["parcours_scolaire"].find().to_list(length=200)]

    from backend.models import Certification, Experience, Project, Skill, Technology

    certifications = [Certification(**mongo_to_api(doc)) for doc in await db["certifications"].find().to_list(length=200)]
    skills = [Skill(**mongo_to_api(doc)) for doc in await db["skills"].find().to_list(length=500)]
    technologies = [Technology(**mongo_to_api(doc)) for doc in await db["technologies"].find().to_list(length=500)]
    hobbies = [Hobby(**mongo_to_api(doc)) for doc in await db["hobbies"].find().to_list(length=200)]

    return GlobalPortfolioResponse(
        infos_personnels=infos,
        projets=[Project(**doc) for doc in projects],
        experiences=[Experience(**doc) for doc in experiences],
        parcours_scolaire=parcours,
        certifications=certifications,
        skills=skills,
        technologies=technologies,
        hobbies=hobbies,
    )
