"""Configuration centralisée (lecture .env via pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── App ────────────────────────────────────────────────────
    app_name: str = "Portfolio Data-Driven API"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── MongoDB ────────────────────────────────────────────────
    mongo_url: str = "mongodb://user0:user0@mongo:27017"
    mongo_db: str = "portfolio"

    # ── Neo4j ──────────────────────────────────────────────────
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "user0000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
