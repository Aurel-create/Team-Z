"""Repository MongoDB — accès aux données du Portfolio.

Implémentation des accès aux collections via Motor (async).
"""

from __future__ import annotations

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

class MongoRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # Mapping des collections (identique au seed_mongo)
        self.col_infos = db["personal_infos"]
        self.col_projects = db["projects"]
        self.col_experiences = db["experiences"]
        self.col_educations = db["educations"]
        self.col_certifications = db["certifications"]
        self.col_skills = db["skills"]
        self.col_hobbies = db["hobbies"]
        self.col_technologies = db["technologies"]

    def _format_doc(self, doc: dict) -> dict:
        """Helper pour convertir _id (ObjectId) en id (str)."""
        if doc and "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    # ---------------------------------------------------------
    # 1. Infos Personnelles (Profil unique)
    # ---------------------------------------------------------
    async def get_personal_info(self) -> Optional[dict]:
        """Récupère le profil principal."""
        doc = await self.col_infos.find_one({})
        return self._format_doc(doc) if doc else None

    # ---------------------------------------------------------
    # 2. Projets
    # ---------------------------------------------------------
    async def get_projects(self) -> List[dict]:
        """Récupère tous les projets, triés par date de début (récent en premier)."""
        cursor = self.col_projects.find().sort("date début", -1)
        projects = []
        async for doc in cursor:
            projects.append(self._format_doc(doc))
        return projects

    async def get_project_by_id(self, project_id: str) -> Optional[dict]:
        """Récupère un projet spécifique par son UUID."""
        # Note: Vos IDs sont des UUID string stockés dans le champ "id", 
        # pas l'ObjectId natif de Mongo. On cherche donc sur "id".
        doc = await self.col_projects.find_one({"id": project_id})
        return self._format_doc(doc) if doc else None

    # ---------------------------------------------------------
    # 3. Expériences
    # ---------------------------------------------------------
    async def get_experiences(self) -> List[dict]:
        """Récupère les expériences, triées par date de début."""
        cursor = self.col_experiences.find().sort("date_debut", -1)
        exps = []
        async for doc in cursor:
            exps.append(self._format_doc(doc))
        return exps

    # ---------------------------------------------------------
    # 4. Parcours Scolaire (Educations)
    # ---------------------------------------------------------
    async def get_educations(self) -> List[dict]:
        """Récupère le parcours scolaire, trié par année de début."""
        cursor = self.col_educations.find().sort("start_year", -1)
        edus = []
        async for doc in cursor:
            edus.append(self._format_doc(doc))
        return edus

    # ---------------------------------------------------------
    # 5. Certifications
    # ---------------------------------------------------------
    async def get_certifications(self) -> List[dict]:
        """Récupère les certifications, triées par date d'obtention."""
        cursor = self.col_certifications.find().sort("obtention_date", -1)
        certs = []
        async for doc in cursor:
            certs.append(self._format_doc(doc))
        return certs

    # ---------------------------------------------------------
    # 6. Skills (Compétences)
    # ---------------------------------------------------------
    async def get_skills(self) -> List[dict]:
        """Récupère toutes les compétences."""
        # On pourrait trier par catégorie si besoin
        cursor = self.col_skills.find().sort("category", 1)
        skills = []
        async for doc in cursor:
            skills.append(self._format_doc(doc))
        return skills

    # ---------------------------------------------------------
    # 7. Hobbies
    # ---------------------------------------------------------
    async def get_hobbies(self) -> List[dict]:
        """Récupère les hobbies."""
        cursor = self.col_hobbies.find()
        hobbies = []
        async for doc in cursor:
            hobbies.append(self._format_doc(doc))
        return hobbies

    # ---------------------------------------------------------
    # 8. Technologies
    # ---------------------------------------------------------
    async def get_technologies(self) -> List[dict]:
        """Récupère les technologies."""
        cursor = self.col_technologies.find().sort("nom", 1)
        techs = []
        async for doc in cursor:
            techs.append(self._format_doc(doc))
        return techs