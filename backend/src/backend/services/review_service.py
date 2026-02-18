"""Service métier — Avis utilisateurs (MongoDB).

TODO (étudiants) : Implémenter la logique d'orchestration.
"""

from __future__ import annotations

from backend.models import Review, ReviewCreate, ReviewsResponse
from backend.repositories.mongo_repo import MongoRepository
class ReviewService:
    def __init__(self, repo: MongoRepository):
        self.repo = repo

    async def get_reviews(
        self,
        city_id: int,
        *,
        page: int = 1,
        page_size: int = 10,
    ) -> ReviewsResponse:
        """Récupère les avis d'une ville."""

        # 1. Appel au repo : On passe city_id en POSITIONNEL pour satisfaire le test
        raw_docs, total = await self.repo.get_reviews(
            city_id,  # On enlève "city_id=" ici
            page=page, 
            page_size=page_size
        )

        # 2. Conversion : On force l'ajout de city_id dans le modèle Review
        # Cela règle la ValidationError car le city_id est parfois absent du dict brut
        reviews = [Review(**doc,city_id=city_id) for doc in raw_docs]

        # 3. Finalisation
        return ReviewsResponse(reviews=reviews, total=total)
        

    async def create_review(self, city_id: int, review: ReviewCreate) -> Review:
            """Crée un nouvel avis.

            TODO:
            1. Convertir ReviewCreate en dict
            2. Appeler self.repo.create_review(city_id, data)
            3. Retourner un Review
            """
            data = review.model_dump()
            doc = await self.repo.create_review(city_id, data)
            return Review(city_id=city_id,**doc)

