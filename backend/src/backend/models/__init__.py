"""Pydantic models — réexporte les schemas partagés + modèles spécifiques backend."""

from shared.schemas import (  # noqa: F401
    City,
    CityDetail,
    CityListResponse,
    CityScores,
    HealthResponse,
    RecommendationItem,
    RecommendationsResponse,
    Review,
    ReviewCreate,
    ReviewsResponse,
    ScoreCategory,
)

__all__ = [
    "City",
    "CityDetail",
    "CityListResponse",
    "CityScores",
    "HealthResponse",
    "RecommendationItem",
    "RecommendationsResponse",
    "Review",
    "ReviewCreate",
    "ReviewsResponse",
    "ScoreCategory",
]
