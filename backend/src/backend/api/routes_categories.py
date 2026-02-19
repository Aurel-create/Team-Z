from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import List, Dict

from backend.db.mongo import get_mongo_db
from backend.repositories.mongo_repo import MongoRepository
from backend.models import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
async def list_categories():
    db = get_mongo_db()
    repo = MongoRepository(db)
    cats = await repo.col_educations.database["categories"].find().to_list(length=None)
    if cats is None:
        return []
    out = []
    for c in cats:
        c["id"] = str(c.pop("_id"))
        out.append(c)
    return out


@router.get("/{cat_id}", response_model=CategoryResponse)
async def get_category(cat_id: str):
    db = get_mongo_db()
    repo = MongoRepository(db)
    doc = await repo.col_educations.database["categories"].find_one({"_id": __import__("bson").ObjectId(cat_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Category not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/", response_model=CategoryResponse)
async def create_category(payload: CategoryCreate):
    db = get_mongo_db()
    repo = MongoRepository(db)
    data = payload.model_dump()
    res = await repo.col_educations.database["categories"].insert_one(data)
    data["id"] = str(res.inserted_id)
    return data


@router.delete("/{cat_id}")
async def delete_category(cat_id: str):
    db = get_mongo_db()
    repo = MongoRepository(db)
    res = await repo.col_educations.database["categories"].delete_one({"_id": __import__("bson").ObjectId(cat_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"ok": True}


@router.get("/with-technologies")
async def categories_with_techs():
    db = get_mongo_db()
    repo = MongoRepository(db)
    cats = await repo.col_educations.database["categories"].find().to_list(length=None)
    techs = await repo.get_technologies()

    mapping: Dict[str, dict] = {str(c["_id"]): {"id": str(c["_id"]), "name": c.get("name"), "description": c.get("description"), "technologies": []} for c in cats}
    uncategorized = {"id": "__uncat__", "name": "Uncategorized", "technologies": []}

    for t in techs:
        cid = t.get("category_id")
        if cid and cid in mapping:
            mapping[cid]["technologies"].append(t)
        else:
            uncategorized["technologies"].append(t)

    out = list(mapping.values())
    if uncategorized["technologies"]:
        out.append(uncategorized)
    return out
