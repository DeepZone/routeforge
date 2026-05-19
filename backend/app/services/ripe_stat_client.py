import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.services.cache import get_cached, set_cached


class RipeStatClient:
    def __init__(self, db: Session):
        self.db = db

    def get(self, endpoint: str, params: dict) -> dict:
        cached = get_cached(self.db, endpoint, params)
        if cached:
            return cached
        url = f"{settings.ripestat_base_url.rstrip('/')}/{endpoint}/data.json"
        try:
            with httpx.Client(timeout=settings.http_timeout_seconds) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            return {"error": str(exc), "endpoint": endpoint, "params": params}
        set_cached(self.db, endpoint, params, data)
        return data
