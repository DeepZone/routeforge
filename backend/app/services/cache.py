import json
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import ApiCache


def _cache_key(endpoint: str, params: dict) -> str:
    return f"{endpoint}:{json.dumps(params, sort_keys=True)}"


def get_cached(db: Session, endpoint: str, params: dict) -> dict | None:
    key = _cache_key(endpoint, params)
    item = db.query(ApiCache).filter(ApiCache.cache_key == key).first()
    if not item or item.expires_at < datetime.utcnow():
        return None
    return item.response_json


def set_cached(db: Session, endpoint: str, params: dict, data: dict) -> None:
    key = _cache_key(endpoint, params)
    now = datetime.utcnow()
    exp = now + timedelta(seconds=settings.cache_ttl_seconds)
    item = db.query(ApiCache).filter(ApiCache.cache_key == key).first()
    if item:
        item.response_json = data
        item.created_at = now
        item.expires_at = exp
    else:
        db.add(ApiCache(cache_key=key, response_json=data, created_at=now, expires_at=exp))
    db.commit()
