"""Script de seed pour le portfolio — charge les données dans MongoDB et crée
les nœuds/relations de base dans Neo4j.

Usage: python -m backend.scripts.seed_all

Le script attend des fichiers de dataset (JSONL ou JSON) dans le dossier
`datasets/` à la racine du workspace. Fichiers attendus (optionnels) :
- projects.jsonl ou projects.json
- technologies.jsonl ou technologies.json
- experiences.jsonl ou experiences.json
- certifications.jsonl ou certifications.json
- education.jsonl ou education.json
- hobbies.jsonl ou hobbies.json
- contacts.jsonl ou contacts.json

Le comportement :
- Pour chaque collection, on purge les documents existants puis on insère
  les documents du dataset s'ils existent.
- Ensuite on parcourt les collections et on crée des nœuds Neo4j pour chaque
  document (label selon la collection) avec la propriété `mongo_id` et `name`/`title`.
- On crée des relations simples basées sur les champs `technologies`, `projects`,
  `experiences`, `certifications` présents dans les documents.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.db.mongo import get_mongo_db
from backend.db.neo4j import get_neo4j_driver

# find the repository/workspace root by walking up until we find a `datasets` folder or docker-compose.yml
p = Path(__file__).resolve()
WORKSPACE_ROOT = p
for _ in range(10):
    if (WORKSPACE_ROOT / "datasets").exists() or (WORKSPACE_ROOT / "docker-compose.yml").exists():
        break
    if WORKSPACE_ROOT.parent == WORKSPACE_ROOT:
        break
    WORKSPACE_ROOT = WORKSPACE_ROOT.parent

DATASETS_DIR = WORKSPACE_ROOT / "datasets"
if not DATASETS_DIR.exists():
    # fallback: try one level up from the script (safe fallback), but warn the user
    fallback = Path(__file__).resolve().parent.parent.parent.parent / "datasets"
    if fallback.exists():
        DATASETS_DIR = fallback
    else:
        print(f"[seed] Warning: datasets/ not found under detected workspace root {WORKSPACE_ROOT}; expected at {DATASETS_DIR}")


def _load_dataset(path: Path) -> List[Dict[str, Any]]:
    """Charge un dataset JSONL ou JSON. Retourne une liste de dicts (peut être vide)."""
    if not path.exists():
        return []
    docs: List[Dict[str, Any]] = []
    try:
        if path.suffix == ".jsonl":
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    docs.append(json.loads(line))
        else:
            # json (liste)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    docs = data
                elif isinstance(data, dict):
                    # allow single object -> wrap
                    docs = [data]
    except Exception as exc:
        print(f"[seed] Erreur lecture {path}: {exc}")
    return docs


async def seed_mongo_portfolio():
    """Charge les collections portfolio dans MongoDB depuis datasets/."""
    db: AsyncIOMotorDatabase = get_mongo_db()

    collections = [
        ("projects", ["projects.jsonl", "projects.json"]),
        ("technologies", ["technologies.jsonl", "technologies.json"]),
        ("experiences", ["experiences.jsonl", "experiences.json"]),
        ("certifications", ["certifications.jsonl", "certifications.json"]),
        ("education", ["education.jsonl", "education.json"]),
        ("hobbies", ["hobbies.jsonl", "hobbies.json"]),
        ("contacts", ["contacts.jsonl", "contacts.json"]),
    ]

    for col_name, filenames in collections:
        col = db[col_name]
        print(f"[seed] Purge collection {col_name}...")
        await col.delete_many({})

        # find the first existing dataset file
        docs: List[Dict[str, Any]] = []
        for fn in filenames:
            path = DATASETS_DIR / fn
            docs = _load_dataset(path)
            if docs:
                print(f"[seed] Chargement {len(docs)} docs depuis {path}")
                break

        if not docs:
            print(f"[seed] Aucun dataset trouvé pour {col_name} — collection vide.")
            continue

        # basic normalization: ensure dates/ids are not strings where possible
        for d in docs:
            # remove existing id keys to let Mongo set _id, but keep 'id' if explicit
            if "_id" in d:
                d.pop("_id")
            # convert any nested ObjectId-like strings? keep simple here
        if docs:
            try:
                await col.insert_many(docs)
                print(f"[seed] Inserted {len(docs)} into {col_name}")
            except Exception as exc:
                print(f"[seed] Erreur insertion dans {col_name}: {exc}")

    print("[seed] MongoDB portfolio — OK")


async def seed_neo4j_portfolio():
    """Crée les nœuds et relations de base dans Neo4j à partir des collections Mongo."""
    driver = get_neo4j_driver()
    db = get_mongo_db()

    async with driver.session() as session:
        # purge minimal du graphe (attention : supprime tout)
        print("[seed] Neo4j — purge du graphe (MATCH (n) DETACH DELETE n)")
        await session.run("MATCH (n) DETACH DELETE n")

        # 1) créer les nœuds Technology
        print("[seed] Neo4j — création des nœuds Technology")
        async for tech in db["technologies"].find():
            tech_id = str(tech.get("_id"))
            name = tech.get("name") or tech.get("title") or f"tech-{tech_id}"
            props = {k: v for k, v in tech.items() if k != "_id"}
            await session.run(
                "MERGE (t:Technology {mongo_id: $mongo_id}) SET t.name = $name, t.props = $props",
                mongo_id=tech_id,
                name=name,
                props=json.dumps(props),
            )

        # 2) créer les nœuds Project
        print("[seed] Neo4j — création des nœuds Project")
        async for proj in db["projects"].find():
            proj_id = str(proj.get("_id"))
            title = proj.get("title") or proj.get("name") or f"project-{proj_id}"
            props = {k: v for k, v in proj.items() if k != "_id"}
            await session.run(
                "MERGE (p:Project {mongo_id: $mongo_id}) SET p.title = $title, p.props = $props",
                mongo_id=proj_id,
                title=title,
                props=json.dumps(props),
            )

        # 3) créer les nœuds Experience
        print("[seed] Neo4j — création des nœuds Experience")
        async for exp in db["experiences"].find():
            exp_id = str(exp.get("_id"))
            title = exp.get("title") or exp.get("position") or f"exp-{exp_id}"
            props = {k: v for k, v in exp.items() if k != "_id"}
            await session.run(
                "MERGE (e:Experience {mongo_id: $mongo_id}) SET e.title = $title, e.props = $props",
                mongo_id=exp_id,
                title=title,
                props=json.dumps(props),
            )

        # 4) créer les nœuds Certification
        print("[seed] Neo4j — création des nœuds Certification")
        async for cert in db["certifications"].find():
            cert_id = str(cert.get("_id"))
            title = cert.get("title") or cert.get("name") or f"cert-{cert_id}"
            props = {k: v for k, v in cert.items() if k != "_id"}
            await session.run(
                "MERGE (c:Certification {mongo_id: $mongo_id}) SET c.title = $title, c.props = $props",
                mongo_id=cert_id,
                title=title,
                props=json.dumps(props),
            )

        # 5) autres nœuds (education, hobbies, contacts) — créés mais peu reliés
        print("[seed] Neo4j — création des nœuds Education/Hobby/Contact")
        async for edu in db["education"].find():
            eid = str(edu.get("_id"))
            name = edu.get("school") or edu.get("name") or f"edu-{eid}"
            props = {k: v for k, v in edu.items() if k != "_id"}
            await session.run(
                "MERGE (ed:Education {mongo_id: $mongo_id}) SET ed.name = $name, ed.props = $props",
                mongo_id=eid,
                name=name,
                props=json.dumps(props),
            )
        async for h in db["hobbies"].find():
            hid = str(h.get("_id"))
            name = h.get("name") or f"hobby-{hid}"
            props = {k: v for k, v in h.items() if k != "_id"}
            await session.run(
                "MERGE (hb:Hobby {mongo_id: $mongo_id}) SET hb.name = $name, hb.props = $props",
                mongo_id=hid,
                name=name,
                props=json.dumps(props),
            )
        async for c in db["contacts"].find():
            cid = str(c.get("_id"))
            name = c.get("name") or f"contact-{cid}"
            props = {k: v for k, v in c.items() if k != "_id"}
            await session.run(
                "MERGE (ct:Contact {mongo_id: $mongo_id}) SET ct.name = $name, ct.props = $props",
                mongo_id=cid,
                name=name,
                props=json.dumps(props),
            )

        # 6) créer les relations Project -[:USES]-> Technology (si project.technologies present)
        print("[seed] Neo4j — création des relations Project USES Technology")
        async for proj in db["projects"].find():
            proj_id = str(proj.get("_id"))
            techs = proj.get("technologies") or []
            # techs may be list of names or list of ids; handle names primarily
            for t in techs:
                # try to match by name first, then by mongo_id
                await session.run(
                    "MATCH (p:Project {mongo_id: $proj_id})\n"
                    "OPTIONAL MATCH (t:Technology {name: $tname})\n"
                    "OPTIONAL MATCH (t2:Technology {mongo_id: $tname})\n"
                    "WITH p, COALESCE(t, t2) as tech WHERE p IS NOT NULL AND tech IS NOT NULL\n"
                    "MERGE (p)-[:USES]->(tech)",
                    proj_id=proj_id,
                    tname=str(t),
                )

        # 7) Experience -[:USES]->Technology
        print("[seed] Neo4j — création des relations Experience USES Technology")
        async for exp in db["experiences"].find():
            exp_id = str(exp.get("_id"))
            techs = exp.get("technologies") or []
            for t in techs:
                await session.run(
                    "MATCH (e:Experience {mongo_id: $exp_id})\n"
                    "OPTIONAL MATCH (t:Technology {name: $tname})\n"
                    "OPTIONAL MATCH (t2:Technology {mongo_id: $tname})\n"
                    "WITH e, COALESCE(t, t2) as tech WHERE e IS NOT NULL AND tech IS NOT NULL\n"
                    "MERGE (e)-[:USES]->(tech)",
                    exp_id=exp_id,
                    tname=str(t),
                )

        # 8) Certification -[:RELATED_TO]->Technology (if present)
        print("[seed] Neo4j — création des relations Certification RELATED_TO Technology")
        async for cert in db["certifications"].find():
            cert_id = str(cert.get("_id"))
            techs = cert.get("technologies") or []
            for t in techs:
                await session.run(
                    "MATCH (c:Certification {mongo_id: $cert_id})\n"
                    "OPTIONAL MATCH (t:Technology {name: $tname})\n"
                    "OPTIONAL MATCH (t2:Technology {mongo_id: $tname})\n"
                    "WITH c, COALESCE(t, t2) as tech WHERE c IS NOT NULL AND tech IS NOT NULL\n"
                    "MERGE (c)-[:RELATED_TO]->(tech)",
                    cert_id=cert_id,
                    tname=str(t),
                )

    print("[seed] Neo4j portfolio — OK")


async def main():
    print("=" * 50)
    print("Portfolio — Seed")
    print("=" * 50)

    await seed_mongo_portfolio()
    await seed_neo4j_portfolio()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())