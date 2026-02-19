"""Lancement du serveur FastAPI SmartCity Explorer."""

import uvicorn

from backend.core.config import get_settings


def main():
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
