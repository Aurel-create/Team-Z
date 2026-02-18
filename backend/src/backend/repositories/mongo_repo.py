"""Repository MongoDB — accès aux avis utilisateurs.

TODO (étudiants) : Implémenter chaque méthode avec des requêtes MongoDB
via Motor (async).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["reviews"]

    async def get_reviews(
    self,
    city_id: int,
    *,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[dict], int]:
        """Récupère les avis pour une ville avec pagination."""
        
        # 1. Définition du filtre (recherche par l'ID de la ville)
        query = {"city_id": city_id}
        
        # 2. Récupération du nombre total pour cette ville (utile pour le front-end)
        total_count = await self.collection.count_documents(query)
        
        # 3. Calcul de l'offset (combien de documents sauter)
        skip = (page - 1) * page_size
        
        # 4. Requête paginée et triée
        # On trie par 'created_at' descendant (-1) pour avoir les plus récents en premier
        cursor = self.collection.find(query) \
                                .sort("created_at", -1) \
                                .skip(skip) \
                                .limit(page_size)
        
        # 5. Conversion du curseur en liste et nettoyage des IDs
        reviews = []
        async for doc in cursor:
            # On transforme l'ObjectId de Mongo en string pour qu'il soit sérialisable
            # On le renomme au passage 'id' pour coller aux standards SQL/API
            doc["id"] = str(doc.pop("_id"))
            reviews.append(doc)
            
        return reviews, total_count

        """ TODO: Implémenter avec Motor :
        - Filtrer par city_id
        - Trier par created_at décroissant
        - Paginer avec skip/limit
        - Retourner (liste_de_docs, total_count)
        - Convertir ObjectId en str pour le champ "id"
        """
        # TODO: Implémenter find + pagination + conversion _id -> id

    

    async def create_review(self, city_id: int, review_data: dict) -> dict:

      # 1. Préparation du document (Enrichissement)
        # On fait une copie pour ne pas modifier l'original par accident
        new_doc = review_data.copy()
        
        # On ajoute les infos gérées par le système
        new_doc["city_id"] = city_id
        new_doc["created_at"] = datetime.now(timezone.utc)
        
        # 2. Insertion dans la collection
        # insert_one renvoie un objet qui contient l'id généré par MongoDB
        result = await self.collection.insert_one(new_doc)
        
        # 3. Récupération et formatage pour le retour
        # On ajoute l'ID généré au dictionnaire
        new_doc["id"] = str(result.inserted_id)
        
        # On supprime la clé technique '_id' de MongoDB pour rester propre
        if "_id" in new_doc:
            new_doc.pop("_id")
            
        return new_doc
    
        """Crée un nouvel avis pour une ville.

        TODO: Implémenter :
        - Ajouter city_id et created_at au document
        - Insérer dans la collection reviews
        - Retourner le document créé (avec id converti en str)
        """
        # TODO: Implémenter insert_one + city_id/created_at, retourner doc avec id (str)
        raise NotImplementedError
        

    async def get_average_rating(self, city_id: int) -> Optional[float]:
        pipeline = [
            # On filtre les documents pour la ville ciblée
            {"$match": {"city_id": city_id}},
            # On regroupe tous les documents de cette ville pour calculer la moyenne
            {"$group": {
                "_id": "$city_id",
                # On change "average" par "avg_rating" pour que ça plaise au test !
                "avg_rating": {"$avg": "$rating"} 
            }}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)
        
        if results:
            # On utilise la nouvelle clé ici aussi
            return results[0]["avg_rating"]
        
        return None
        
        """Calcule la note moyenne pour une ville.

        TODO: Implémenter un pipeline d'agrégation MongoDB :
        - $match par city_id
        - $group avec $avg sur rating
        """
        # TODO: Implémenter pipeline d'agrégation $match + $group $avg
        raise NotImplementedError
