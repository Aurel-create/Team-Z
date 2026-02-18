"""Configuration centralisée (lecture .env via pydantic-settings).

Ce fichier expose les variables d'environnement utilisées par l'application
portfolio : connexion MongoDB (document store principal) et Neo4j (graphe de
relations). Les valeurs par défaut sont adaptées à l'exécution via Docker
Compose (services nommés `mongo` et `neo4j`).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────
    app_name: str = "Portfolio API"
    app_version: str = "0.1.0"
    debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ── MongoDB ────────────────────────────────────────────────
    # URL complet (utilisé prioritairement). Par défaut pointe vers le service
    # `mongo` exposé par docker-compose.
    mongo_url: str = "mongodb://mongo:27017"
    # Nom de la base de données
    mongo_db: str = "user0"
    # Identifiants (optionnels, selon configuration de Mongo)
    mongo_user: str = "user0"
    mongo_password: str = "user0"

    # ── Neo4j ──────────────────────────────────────────────────
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "user0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
