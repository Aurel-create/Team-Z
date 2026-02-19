# Team-Z — Portfolio Data-Driven Backend

Backend unique en FastAPI avec persistance polyglotte :
- MongoDB : stockage complet des documents métier.
- Neo4j : intelligence relationnelle entre entités via `mongo_id`.

## Stack
- FastAPI (Python)
- Motor (MongoDB async)
- Neo4j Driver officiel async
- Docker Compose (MongoDB + Neo4j)

## Structure principale
- `backend/src/backend/main.py` : entrée FastAPI + routers modulaires.
- `backend/src/backend/database.py` : point central de connexion DB.
- `backend/src/backend/database/mongo_handler.py` : handler Motor.
- `backend/src/backend/database/neo4j_handler.py` : handler Neo4j.
- `backend/src/backend/routers/projects.py` : CRUD Projet + synchro graphe.
- `backend/src/backend/routers/experiences.py` : CRUD Expérience + synchro graphe.
- `backend/src/backend/routers/skills.py` : CRUD Skill/Technology/Certification + recherche graphe.
- `backend/src/backend/routers/profile.py` : Infos perso, parcours, hobbies + endpoint global.
- `backend/src/backend/models/schemas.py` : modèles Pydantic de toutes les collections.

## Collections MongoDB
- `infos_personnels`
- `projects`
- `experiences`
- `parcours_scolaire`
- `certifications`
- `skills`
- `technologies`
- `hobbies`

Tous les `_id` MongoDB sont convertis en `id` (string) côté API.

## Graphe Neo4j (mongo_id obligatoire)
Relations gérées :
- `(Person)-[:WORKED_ON]->(Project)`
- `(Project)-[:USES_TECH]->(Technology)`
- `(Project)-[:REQUIRES_SKILL]->(Skill)`
- `(Experience)-[:GAINED_SKILL]->(Skill)`
- `(Experience)-[:RELATED_TO_PROJECT]->(Project)`
- `(Certification)-[:VALIDATES]->(Technology)`
- `(Certification)-[:VALIDATES]->(Skill)`

Chaque nœud Neo4j porte une propriété `mongo_id` correspondant au `_id` MongoDB stringifié.

## Endpoints clés demandés
### 1) POST `/projects`
Crée un projet dans MongoDB puis :
- crée/met à jour le nœud `Project {mongo_id}` dans Neo4j,
- crée les relations vers Person/Technology/Skill selon les IDs fournis.

Payload exemple :
```json
{
	"nom": "Portfolio API",
	"date_debut": "2026-01-10",
	"description": "Backend FastAPI polyglotte",
	"entreprise": "Freelance",
	"collaborateurs": ["Alice", "Bob"],
	"lien_github": "https://github.com/user/repo",
	"status": "en_cours",
	"person_ids": ["65f1..."],
	"technology_ids": ["65f2..."],
	"skill_ids": ["65f3..."]
}
```

### 2) GET `/skills/{name}/projects`
Algorithme :
1. Requête Cypher sur Neo4j pour trouver les `Project.mongo_id` reliés au `Skill.nom`.
2. Requête MongoDB (`_id IN [...]`) pour renvoyer les détails complets des projets.

## Endpoint global portfolio
- `GET /profile/global`

Agrège toutes les collections pour la page d'accueil du portfolio.

## Plan de travail équipe (4 membres)
### Membre 1 — Infrastructure & Core
- FastAPI, config, handlers DB, docker-compose.
- Modèles Pydantic de base.

### Membre 2 — Projets & Expériences
- CRUD complet `projects` / `experiences`.
- Synchro relation `Experience -> RELATED_TO_PROJECT -> Project`.

### Membre 3 — Compétences & Savoir-faire
- CRUD `skills`, `technologies`, `certifications`.
- Recherche `GET /skills/{name}/projects` via Cypher + Mongo.

### Membre 4 — Profil, Parcours & Agrégation
- CRUD `infos_personnels`, `parcours_scolaire`, `hobbies`.
- Endpoint d'agrégation `GET /profile/global`.

## Lancer en local
### 1) Démarrer les bases
```bash
docker compose up -d
```

### 2) Installer dépendances backend
```bash
cd backend
pip install -e .
```

### 3) Lancer l'API
```bash
PYTHONPATH=src uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Swagger
- `http://localhost:8000/docs`

## Frontend React
L'interface frontend principale est disponible dans :
- `frontend_react`

### Lancer le frontend
```bash
cd frontend_react
npm install
npm run dev
```

Frontend branché sur l'API FastAPI avec :
- UI livre interactif en double-page
- Navigation fluide par clic sur la page gauche/droite
- Vue globale (`GET /profile/global`)
- Projets (`GET /projects`)
- Expériences (`GET /experiences`)
- Compétences -> projets liés (`GET /skills/{name}/projects`)
- Healthcheck (`GET /health`)

## Seed portfolio (fausses données)
Pour injecter un dataset de test dans toutes les collections MongoDB et reconstruire les relations Neo4j :

```bash
cd backend
PYTHONPATH=src python -m backend.scripts.seed_portfolio
```

Script utilisé :
- `backend/src/backend/scripts/seed_portfolio.py`

Ce seed crée des données de test pour :
- `infos_personnels`, `projects`, `experiences`, `parcours_scolaire`, `certifications`, `skills`, `technologies`, `hobbies`
- et les relations Neo4j : `WORKED_ON`, `USES_TECH`, `REQUIRES_SKILL`, `GAINED_SKILL`, `RELATED_TO_PROJECT`, `VALIDATES`.