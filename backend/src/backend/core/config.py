"""Configuration centralisée (lecture .env via pydantic-settings)."""

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
    app_name: str = "SmartCity Explorer API"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── PostgreSQL ─────────────────────────────────────────────
    postgres_url: str = "postgresql+asyncpg://user:password@localhost:5432/smartcity"

    # ── MongoDB ────────────────────────────────────────────────
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "smartcity"

    # ── Neo4j ──────────────────────────────────────────────────
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"


@lru_cache
def get_settings() -> Settings:
    return Settings()
