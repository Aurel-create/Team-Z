"""Utilitaires de conversion MongoDB -> API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from bson import ObjectId


def _normalize_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {k: _normalize_value(v) for k, v in value.items()}
    return value


def mongo_to_api(document: dict[str, Any]) -> dict[str, Any]:
    doc = {k: _normalize_value(v) for k, v in document.items()}
    mongo_id = doc.pop("_id", None)
    if mongo_id is not None:
        doc["id"] = str(mongo_id)
    return doc
