# API — Contrat du projet

Ce document décrit le contrat d'API exposé par l'application FastAPI du dépôt.

## Base
- Serveur: FastAPI
- CORS: toutes origines autorisées (aucune auth par défaut)
- Health: `GET /health` → `HealthResponse { status, version }`
- Root: `GET /` → message

## Modèles (références)
Les schémas Pydantic sont ré-exportés depuis `backend.models` (définis dans `shared.schemas`).
Principaux modèles référencés:
- PersonalInfo, Certification, Contact, Experience, Hobby, ParcoursScolaire, Projet, ProjetDetail, Skill, Techno
- CategoryCreate, CategoryResponse
- Review, ReviewCreate, ReviewsResponse
- RecommendationsResponse
- HealthResponse

## Gestion des erreurs
- 404 lorsque la ressource est introuvable.
- 500 pour erreurs internes (handler global).
- 501 pour `NotImplementedError`.

---

## Routes — Personal infos
- GET /personal-infos
  - Renvoie: `PersonalInfo` (200) ou 404
- GET /personal-infos/certifications
  - Renvoie: `list[Certification]` (200) ou 404

## Routes — Portfolio (préfixe `/portfolio`)
- GET /portfolio/skills
  - Renvoie: `list[Skill]` (200) ou 404
- GET /portfolio/projets
  - Renvoie: `list[Projet]` (200) ou 404
- GET /portfolio/projets/details
  - Description: projets enrichis (fusion MongoDB + Neo4j)
  - Renvoie: `list[ProjetDetail]` (200) ou 404
- GET /portfolio/technologies
  - Renvoie: `list[Techno]` (200) ou 404
- GET /portfolio/hobbies
  - Renvoie: `list[Hobby]` (200) ou 404
- GET /portfolio/experiences
  - Renvoie: `list[Experience]` (200) ou 404
- GET /portfolio/parcours-scolaire
  - Renvoie: `list[ParcoursScolaire]` (200) ou 404

## Routes — Categories (préfixe `/categories`)
- GET /categories/
  - Renvoie: `list[CategoryResponse]` (200)
- GET /categories/{cat_id}
  - Path: `cat_id` (str)
  - Renvoie: `CategoryResponse` (200) ou 404
- POST /categories/
  - Body: `CategoryCreate`
  - Renvoie: `CategoryResponse` (201)
- DELETE /categories/{cat_id}
  - Renvoie: `{ "ok": true }` (200) ou 404
- GET /categories/with-technologies
  - Description: renvoie les catégories avec la liste des technologies associées (group-by côté API).
  - Renvoie: liste d'objets `{ id, name, description?, technologies: [Techno...] }` (200)

## Routes — Reviews
- GET /cities/{city_id}/reviews
  - Path: `city_id` (int)
  - Query: `page` (int, default 1), `page_size` (int, default 10)
  - Renvoie: `ReviewsResponse` (200)
- POST /cities/{city_id}/reviews
  - Body: `ReviewCreate`
  - Renvoie: `Review` (201)

## Routes — Recommendations
- GET /recommendations
  - Query: `city_id` (int, required), `k` (int, default 5, 1..20)
  - Renvoie: `RecommendationsResponse` (200) ou 404

---

## Notes d'intégration
- Les endpoints qui enrichissent via Neo4j (ex. `/portfolio/projets/details`, recommandations) consultent Neo4j via `backend.db.neo4j`.
- Les données primaires sont stockées en MongoDB (collections: `projects`, `technologies`, `skills`, `educations`, `experiences`, `certifications`, `hobbies`, `personal_infos`).
- Pour que les technologies apparaissent sous une catégorie, chaque document `technologies` doit contenir `category_id` (id Mongo) ; sinon elles sont groupées sous "Uncategorized".
- Le script de seed (`backend/src/backend/scripts/seed_all.py`) charge MongoDB et peut enrichir le graphe Neo4j.

## Exemples rapides
- GET /portfolio/technologies
  - Réponse 200: `[ { "nom": "FastAPI", "version": "...", ... }, ... ]`
- POST /categories/ (body `CategoryCreate`)
  - Exemple body: `{ "name": "Frontend", "description": "UI frameworks" }`
  - Réponse 201: `{ "id": "6423...", "name": "Frontend", "description": "UI frameworks" }`

## Conseils pour tests & debug
- Vérifier `/health` après le démarrage.
- Utiliser les endpoints Mongo pour confirmer la présence de `category_id` sur les technologies avant d'attendre des relations Neo4j.
- Si vous souhaitez que les catégories existent aussi dans Neo4j, activer la logique de création/linking dans `seed_all.py` ou exécuter un script de linking.

---

Fichier généré automatiquement. Mettez-le à jour si le contrat évolue.
