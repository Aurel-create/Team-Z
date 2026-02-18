"""Script de seed — charge les datasets JSONL dans MongoDB.

Usage: uv run python -m backend.scripts.seed_all
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from backend.db.mongo import get_mongo_db

# Le dossier datasets est à la racine du projet Team-Z
DATASETS_DIR = Path(__file__).resolve().parents[4] / "datasets"

# Mapping : fichier JSONL → nom de collection MongoDB
COLLECTIONS = {
    "infos_personnels.jsonl": "infos",
    "experiences.jsonl": "experience",
    "skills.jsonl": "skills",
    "technologies.jsonl": "technos",
    "projets.jsonl": "projets",
    "parcours_scolaire.jsonl": "parcours_scolaire",
    "certifications.jsonl": "certifications",
    "hobbies.jsonl": "hobbies",
}


async def _load_jsonl(filepath: Path) -> list[dict]:
    """Lit un fichier JSONL et retourne une liste de documents."""
    docs = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
        # Certains fichiers (infos_personnels) sont un seul objet JSON, pas du JSONL
        if content.startswith("{"):
            try:
                doc = json.loads(content)
                docs.append(doc)
                return docs
            except json.JSONDecodeError:
                pass
        # Format JSONL classique : un JSON par ligne
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            docs.append(json.loads(line))
    return docs


async def seed_mongo():
    """Charge tous les fichiers JSONL du dossier datasets dans MongoDB."""
    db = get_mongo_db()

    for filename, collection_name in COLLECTIONS.items():
        filepath = DATASETS_DIR / filename
        if not filepath.exists():
            print(f"[seed] ⚠️  Fichier manquant : {filepath} — skip")
            continue

        collection = db[collection_name]

        # 1. Nettoyage (idempotence)
        await collection.delete_many({})

        # 2. Chargement
        docs = await _load_jsonl(filepath)

        # 3. Insertion
        if docs:
            await collection.insert_many(docs)
            print(f"[seed] ✅ {collection_name} — {len(docs)} document(s)")
        else:
            print(f"[seed] ⚠️  {collection_name} — 0 documents")

    print("[seed] MongoDB — OK")


async def main():
    print("=" * 50)
    print("Portfolio — Seed MongoDB")
    print("=" * 50)
    await seed_mongo()
    print("[seed] Terminé.")


if __name__ == "__main__":
    asyncio.run(main())