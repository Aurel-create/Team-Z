from backend.routers.experiences import router as experiences_router
from backend.routers.profile import router as profile_router
from backend.routers.projects import router as projects_router
from backend.routers.skills import router as skills_router

__all__ = [
    "experiences_router",
    "profile_router",
    "projects_router",
    "skills_router",
]
