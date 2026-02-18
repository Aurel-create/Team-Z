# Team-Z — Portfolio Backend (FastAPI)

API backend pour un portfolio personnel. Ce dépôt contient une API FastAPI qui stocke les données principales dans MongoDB et gère les relations (projets ↔ technologies, expériences ↔ technologies, certifications ↔ technologies) dans Neo4j.

Objectif
- Prototype propre et professionnel pour exposer projets, expériences, certifications, technologies, parcours scolaire, hobbies et un formulaire de contact.
- MongoDB pour les documents (collections : `projects`, `technologies`, `experiences`, `certifications`, `education`, `hobbies`, `contacts`).
- Neo4j pour le graphe de relations (nœuds créés depuis Mongo, relations `USES` / `RELATED_TO`, etc.).

Stack
- Python 3.11+
- FastAPI
- Motor (MongoDB async client)
- Neo4j Python driver
- Uvicorn (ASGI server)
- Docker Compose pour Mongo + Neo4j + mongo-express (UI)

Fichiers importants
- `backend/src/backend/main.py` — point d'entrée FastAPI
- `backend/src/backend/api/` — routes (projects, experiences, certifications, technologies, education, hobbies, contact)
- `backend/src/backend/models/` — Pydantic models
- `backend/src/backend/repositories/` — accès Mongo / Neo4j
- `backend/src/backend/services/` — logique métier (PortfolioService)
- `backend/src/backend/scripts/seed_all.py` — script de seed pour Mongo & Neo4j
- `docker-compose.yml` — services Docker (mongo, mongo-express, neo4j)
- `datasets/` — exemples de données JSON pour seed
- `.env.example` — variables d'environnement (copier en `.env` et adapter)

Installation & exécution locale (PowerShell)
1) Copier l'exemple de variables d'environnement :

   Copy-Item .env.example .env

   Éditez `.env` si besoin pour ajuster mots de passe ou URIs.

2) Démarrer les services Docker (MongoDB + Neo4j + mongo-express) :

   docker-compose up -d

   - Mongo : port 27017
   - mongo-express (UI) : http://localhost:8081
   - Neo4j Browser : http://localhost:7474 (Bolt : 7687)

3) Installer les dépendances Python :

   python -m pip install -r requirements.txt

4) Remplir la base et créer le graphe (seed) :

   python -m backend.scripts.seed_all

   Le script lit les fichiers dans `datasets/` et :
   - purge et remplit les collections Mongo
   - crée les nœuds Neo4j (Project, Technology, Experience, Certification, ...)
   - crée des relations simples (Project -[:USES]-> Technology, etc.)

5) Lancer l'API :

   # depuis la racine du repo (PowerShell)
   $env:PYTHONPATH = (Join-Path $PWD 'backend\src')
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI / Docs
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

Endpoints principaux (exemples)
- GET  /projects
- GET  /projects/{id}
- POST /projects
- GET  /technologies
- POST /technologies
- GET  /experiences
- POST /experiences
- GET  /certifications
- POST /certifications
- GET  /education
- POST /education
- GET  /hobbies
- POST /hobbies
- POST /contact

Notes & recommandations
- Le seed purge le graphe Neo4j (MATCH (n) DETACH DELETE n) — n'utilise qu'en local.
- Si tu veux des recommandations basées graphe, il est possible d'ajouter des helpers Neo4j (exposés dans `backend/src/backend/repositories/neo4j_repo.py`).
- Le projet a été adapté depuis un template plus ancien — certaines références (ex. `shared`) ont été retirées. Si tu veux restaurer d'autres fonctionnalités, je peux t'aider à les réintégrer.

Dépannage rapide
- Erreurs d'import : assure-toi que `PYTHONPATH` inclut `backend/src` ou installe le paquet backend en editable mode.
- Connexions DB : vérifie les variables dans `.env`.

Prochaines étapes suggérées
- Ajouter tests unitaires pour les routes principales.
- Ajouter CI (lint & tests) et script Docker pour le service FastAPI si tu veux déployer.
- Intégrer authentification (JWT) si besoin pour administrer le contenu.

Si tu veux, j'intègre automatiquement ces instructions dans un script PowerShell `scripts/start.ps1` pour démarrer tout (Docker, seed, uvicorn). Dis-moi si tu veux que je le crée.