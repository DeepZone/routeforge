import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.services.cache import get_cached, set_cached


class RipeStatClient:
    def __init__(self, db: Session):
        self.db = db

    def get(self, endpoint: str, params: dict) -> dict:
        if settings.demo_mode:
            return self._get_demo_data(endpoint, params)
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

    def _get_demo_data(self, endpoint: str, params: dict) -> dict:
        resource = str(params.get("resource", "")).upper()
        if endpoint == "as-overview" and resource == "AS3320":
            return {
                "data": {
                    "resource": "AS3320",
                    "holder": "DEMO: Deutsche Telekom AG",
                    "announced": True,
                },
                "demo_mode": True,
            }
        if endpoint == "announced-prefixes" and resource == "AS3320":
            return {
                "data": {
                    "resource": "AS3320",
                    "prefixes": [
                        {"prefix": "192.0.2.0/24"},
                        {"prefix": "198.51.100.0/24"},
                        {"prefix": "203.0.113.0/24"},
                        {"prefix": "2001:db8::/32"},
                    ],
                },
                "demo_mode": True,
            }
        if endpoint == "rpki-validation":
            prefix = str(params.get("resource", "")).lower()
            origin_param = params.get('prefix') or params.get('origin_asn') or params.get('origin')
            origin = str(origin_param or '').strip().upper()
            statuses = {
                ("192.0.2.0/24", "AS3320"): "valid",
                ("198.51.100.0/24", "AS3320"): "invalid_asn",
                ("203.0.113.0/24", "AS3320"): "invalid_length",
                ("2001:db8::/32", "AS3320"): "unknown",
            }
            status = statuses.get((prefix, origin), "unknown")
            return {"data": {"status": status}, "demo_mode": True}
        return {"error": f"No demo data for endpoint '{endpoint}'", "endpoint": endpoint, "params": params, "demo_mode": True}
