import time
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

import app.config as config
from app.core.source_diagnostics import (
    EMPTY_RESPONSE,
    ERROR,
    HTTP_ERROR,
    OK,
    PARSE_ERROR,
    RATE_LIMITED,
    TIMEOUT,
    make_cache_metadata,
    make_source_diagnostic,
)
from app.services.cache import _cache_key, get_cached, set_cached


class RipeStatClient:
    def __init__(self, db: Session):
        self.db = db

    def get(self, endpoint: str, params: dict) -> dict:
        payload, _diagnostic = self.get_with_diagnostics(endpoint, params)
        return payload or {"error": "empty response", "endpoint": endpoint, "params": params}

    def get_with_diagnostics(self, endpoint: str, params: dict, force_refresh: bool = False) -> tuple[dict | None, dict]:
        started = time.perf_counter()
        cache_key = _cache_key(endpoint, params)
        if config.settings.demo_mode:
            payload = self._get_demo_data(endpoint, params)
            cache_meta = make_cache_metadata(cached=False)
            return payload, make_source_diagnostic(
                name=f"RIPEstat {endpoint}",
                endpoint=endpoint,
                status=OK,
                message="Demo data returned",
                duration_ms=int((time.perf_counter() - started) * 1000),
                **cache_meta,
                details={"demo_mode": True, "force_refresh": force_refresh, "cache_key": cache_key},
            )

        if not force_refresh:
            cached_payload = get_cached(self.db, endpoint, params)
            if cached_payload:
                payload = cached_payload if isinstance(cached_payload, dict) else {"payload": cached_payload}
                # backward compatibility: older cache may store raw payload
                if "payload" in payload and "fetched_at" in payload:
                    wrapped = payload
                else:
                    wrapped = {"payload": payload, "fetched_at": datetime.now(UTC).isoformat(), "ttl_seconds": config.settings.cache_ttl_seconds, "cache_key": cache_key}

                fetched_dt = datetime.fromisoformat(wrapped["fetched_at"]).replace(tzinfo=UTC)
                age_seconds = max(0, int((datetime.now(UTC) - fetched_dt).total_seconds()))
                ttl = int(wrapped.get("ttl_seconds") or config.settings.cache_ttl_seconds)
                expires_at = (fetched_dt + timedelta(seconds=ttl)).isoformat()
                cache_meta = make_cache_metadata(True, age_seconds, ttl, wrapped["fetched_at"], expires_at)
                return wrapped.get("payload"), make_source_diagnostic(
                    name=f"RIPEstat {endpoint}",
                    endpoint=endpoint,
                    status=OK,
                    message="RIPEstat response served from cache",
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    **cache_meta,
                    details={"cache_key": cache_key, "fetched_at": wrapped["fetched_at"], "expires_at": expires_at, "force_refresh": False},
                )

        url = f"{config.settings.ripestat_base_url.rstrip('/')}/{endpoint}/data.json"
        try:
            with httpx.Client(timeout=config.settings.http_timeout_seconds) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 429:
                    return {"error": "rate limited", "endpoint": endpoint, "params": params}, make_source_diagnostic(
                        name=f"RIPEstat {endpoint}", endpoint=endpoint, status=RATE_LIMITED, message="RIPEstat rate limit reached", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", http_status=resp.status_code, error_type="http_429", details={"cache_key": cache_key, "force_refresh": force_refresh}
                    )
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as exc:
            return {"error": str(exc), "endpoint": endpoint, "params": params}, make_source_diagnostic(
                name=f"RIPEstat {endpoint}", endpoint=endpoint, status=TIMEOUT, message="RIPEstat did not respond before timeout", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", error_type=type(exc).__name__, details={"cache_key": cache_key, "force_refresh": force_refresh}
            )
        except httpx.HTTPStatusError as exc:
            return {"error": str(exc), "endpoint": endpoint, "params": params}, make_source_diagnostic(
                name=f"RIPEstat {endpoint}", endpoint=endpoint, status=HTTP_ERROR, message="RIPEstat responded with HTTP error", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", http_status=exc.response.status_code, error_type=type(exc).__name__, details={"cache_key": cache_key, "force_refresh": force_refresh}
            )
        except ValueError as exc:
            return {"error": str(exc), "endpoint": endpoint, "params": params}, make_source_diagnostic(
                name=f"RIPEstat {endpoint}", endpoint=endpoint, status=PARSE_ERROR, message="RIPEstat response could not be parsed as JSON", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", error_type=type(exc).__name__, details={"cache_key": cache_key, "force_refresh": force_refresh}
            )
        except Exception as exc:
            return {"error": str(exc), "endpoint": endpoint, "params": params}, make_source_diagnostic(
                name=f"RIPEstat {endpoint}", endpoint=endpoint, status=ERROR, message="RIPEstat request failed", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", error_type=type(exc).__name__, details={"cache_key": cache_key, "force_refresh": force_refresh}
            )

        if not data:
            return data, make_source_diagnostic(
                name=f"RIPEstat {endpoint}", endpoint=endpoint, status=EMPTY_RESPONSE, message="RIPEstat returned an empty response", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", details={"cache_key": cache_key, "force_refresh": force_refresh}
            )

        fetched_at = datetime.now(UTC).isoformat()
        ttl = config.settings.cache_ttl_seconds
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl)).isoformat()
        set_cached(self.db, endpoint, params, {"payload": data, "fetched_at": fetched_at, "ttl_seconds": ttl, "cache_key": cache_key})
        cache_meta = make_cache_metadata(False, None, ttl, fetched_at, expires_at)
        return data, make_source_diagnostic(
            name=f"RIPEstat {endpoint}", endpoint=endpoint, status=OK, message="RIPEstat response received", duration_ms=int((time.perf_counter() - started) * 1000), **cache_meta, details={"cache_key": cache_key, "fetched_at": fetched_at, "expires_at": expires_at, "force_refresh": force_refresh}
        )

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
                    "organisation": "Demo Networks Ltd.",
                    "as-name": "DEMO-AS",
                    "prefixes": [
                        {"prefix": "192.0.2.0/24"},
                        {"prefix": "198.51.100.0/24"},
                        {"prefix": "203.0.113.0/24"},
                        {"prefix": "2001:db8::/32"},
                    ],
                },
                "demo_mode": True,
            }
        if endpoint == "as-overview" and resource == "AS4491":
            return {
                "data": {
                    "resource": "AS4491",
                    "holder": "DEMO: CNC Group CHINA169 Backbone",
                    "announced": False,
                },
                "demo_mode": True,
            }
        if endpoint == "announced-prefixes" and resource == "AS4491":
            return {
                "data": {
                    "resource": "AS4491",
                    "prefixes": [],
                },
                "demo_mode": True,
            }
        if endpoint == "whois":
            return {
                "data": {
                    "resource": resource,
                    "records": [{"key": "organisation", "value": "Demo Networks Ltd."}, {"key": "netname", "value": "DEMO-NET"}],
                    "holder": "Demo Networks Ltd.",
                },
                "demo_mode": True,
            }
        if endpoint == "routing-status":
            demo_routing = {
                "192.0.2.0/24": {"data": {"routes": [{"origin": "AS3320"}]}, "demo_mode": True},
                "198.51.100.0/24": {"data": {"routes": [{"origin": "AS64496"}]}, "demo_mode": True},
                "203.0.113.0/24": {"data": {"visibility": [{"prefix": "203.0.113.0/24"}]}, "demo_mode": True},
                "203.0.114.0/24": {"error": "demo upstream timeout", "demo_mode": True},
            }
            return demo_routing.get(resource.lower(), {"data": {}, "demo_mode": True})

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
