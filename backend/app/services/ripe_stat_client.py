import time
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

import app.config as config
from app.core.source_diagnostics import EMPTY_RESPONSE, ERROR, HTTP_ERROR, OK, PARSE_ERROR, RATE_LIMITED, TIMEOUT, make_cache_metadata, make_source_diagnostic
from app.services.cache import _cache_key, get_cached, set_cached


class RipeStatClient:
    def __init__(self, db: Session):
        self.db = db

    def get(self, endpoint: str, params: dict) -> dict:
        payload, _diagnostic = self.get_with_diagnostics(endpoint, params)
        return payload or {"error": "empty response", "endpoint": endpoint, "params": params}

    def _read_cache_entry(self, endpoint: str, params: dict):
        cached_payload = get_cached(self.db, endpoint, params)
        if not cached_payload:
            return None
        if isinstance(cached_payload, dict) and "payload" in cached_payload:
            payload = cached_payload.get("payload")
            fetched_at = cached_payload.get("fetched_at")
            ttl = int(cached_payload.get("ttl_seconds") or config.settings.cache_ttl_seconds)
        else:
            payload = cached_payload
            fetched_at = None
            ttl = int(config.settings.cache_ttl_seconds)
        age_seconds = None
        expires_at = None
        if isinstance(fetched_at, str):
            try:
                fetched_dt = datetime.fromisoformat(fetched_at)
                if fetched_dt.tzinfo is None:
                    fetched_dt = fetched_dt.replace(tzinfo=UTC)
                age_seconds = max(0, int((datetime.now(UTC) - fetched_dt).total_seconds()))
                expires_at = (fetched_dt + timedelta(seconds=ttl)).isoformat()
            except ValueError:
                fetched_at = None
        return {"payload": payload, "fetched_at": fetched_at, "ttl": ttl, "age_seconds": age_seconds, "expires_at": expires_at}

    def get_with_diagnostics(self, endpoint: str, params: dict, force_refresh: bool = False) -> tuple[dict | None, dict]:
        started = time.perf_counter()
        cache_key = _cache_key(endpoint, params)

        if config.settings.demo_mode:
            payload = self._get_demo_data(endpoint, params)
            return payload, make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=OK, message="Demo data returned", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", attempts=1, retry_count=0, fallback_used=False, stale_cache_used=False, details={"demo_mode": True, "force_refresh": force_refresh, "cache_key": cache_key})

        if not force_refresh:
            cache_entry = self._read_cache_entry(endpoint, params)
            if cache_entry:
                cache_meta = make_cache_metadata(True, cache_entry["age_seconds"], cache_entry["ttl"], cache_entry["fetched_at"], cache_entry["expires_at"])
                return cache_entry["payload"], make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=OK, message="RIPEstat response served from cache", duration_ms=int((time.perf_counter() - started) * 1000), attempts=1, retry_count=0, fallback_used=False, stale_cache_used=False, **cache_meta, details={"cache_key": cache_key, "force_refresh": False})

        url = f"{config.settings.ripestat_base_url.rstrip('/')}/{endpoint}/data.json"
        max_retries = 0 if config.settings.demo_mode else int(config.settings.ripestat_max_retries)
        timeout = float(config.settings.ripestat_timeout_seconds or config.settings.http_timeout_seconds)
        backoff = float(config.settings.ripestat_retry_backoff_seconds)
        attempts = 0
        last_status = ERROR
        last_message = "RIPEstat request failed"
        last_error_type = None
        last_http_status = None
        last_details = {"cache_key": cache_key, "force_refresh": force_refresh}

        with httpx.Client(timeout=timeout) as client:
            while attempts <= max_retries:
                attempts += 1
                try:
                    resp = client.get(url, params=params)
                    if resp.status_code == 429:
                        retry_after = resp.headers.get("Retry-After")
                        details = {**last_details}
                        if retry_after:
                            details["retry_after"] = retry_after
                        last_details = details
                        last_status = RATE_LIMITED
                        last_message = "RIPEstat rate limit reached"
                        last_http_status = 429
                        break
                    if resp.status_code in {400, 401, 403, 404}:
                        last_status = HTTP_ERROR
                        last_message = "RIPEstat responded with HTTP error"
                        last_http_status = resp.status_code
                        break
                    if resp.status_code in {502, 503, 504}:
                        last_status = HTTP_ERROR
                        last_message = "RIPEstat responded with HTTP error"
                        last_http_status = resp.status_code
                        if attempts <= max_retries:
                            time.sleep(backoff * (2 ** (attempts - 1)))
                            continue
                        break
                    resp.raise_for_status()
                    data = resp.json()
                    if not data:
                        return data, make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=EMPTY_RESPONSE, message="RIPEstat returned an empty response", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", attempts=attempts, retry_count=max(0, attempts - 1), fallback_used=False, stale_cache_used=False, details=last_details)

                    fetched_at = datetime.now(UTC).isoformat()
                    ttl = config.settings.cache_ttl_seconds
                    expires_at = (datetime.now(UTC) + timedelta(seconds=ttl)).isoformat()
                    set_cached(self.db, endpoint, params, {"payload": data, "fetched_at": fetched_at, "ttl_seconds": ttl, "cache_key": cache_key})
                    cache_meta = make_cache_metadata(False, None, ttl, fetched_at, expires_at)
                    return data, make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=OK, message="RIPEstat response received", duration_ms=int((time.perf_counter() - started) * 1000), attempts=attempts, retry_count=max(0, attempts - 1), fallback_used=False, stale_cache_used=False, **cache_meta, details={**last_details, "fetched_at": fetched_at, "expires_at": expires_at})
                except httpx.TimeoutException as exc:
                    last_status = TIMEOUT
                    last_message = f"Request timed out after {attempts} attempts"
                    last_error_type = type(exc).__name__
                    if attempts <= max_retries:
                        time.sleep(backoff * (2 ** (attempts - 1)))
                        continue
                    break
                except httpx.HTTPStatusError as exc:
                    last_status = HTTP_ERROR
                    last_message = "RIPEstat responded with HTTP error"
                    last_http_status = exc.response.status_code
                    if exc.response.status_code in {502, 503, 504} and attempts <= max_retries:
                        time.sleep(backoff * (2 ** (attempts - 1)))
                        continue
                    break
                except httpx.RequestError as exc:
                    last_status = ERROR
                    last_message = "RIPEstat network request failed"
                    last_error_type = type(exc).__name__
                    if attempts <= max_retries:
                        time.sleep(backoff * (2 ** (attempts - 1)))
                        continue
                    break
                except ValueError as exc:
                    return {"error": str(exc), "endpoint": endpoint, "params": params}, make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=PARSE_ERROR, message="RIPEstat response could not be parsed as JSON", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", attempts=attempts, retry_count=max(0, attempts - 1), fallback_used=False, stale_cache_used=False, error_type=type(exc).__name__, details=last_details)
                except Exception as exc:
                    last_status = ERROR
                    last_message = "RIPEstat request failed"
                    last_error_type = type(exc).__name__
                    break

        if config.settings.ripestat_use_stale_cache_on_error:
            cache_entry = self._read_cache_entry(endpoint, params)
            if cache_entry:
                cache_meta = make_cache_metadata(True, cache_entry["age_seconds"], cache_entry["ttl"], cache_entry["fetched_at"], cache_entry["expires_at"])
                cache_meta["freshness"] = "STALE"
                reason = "rate_limited" if last_status == RATE_LIMITED else "timeout" if last_status == TIMEOUT else "http_error" if last_status == HTTP_ERROR else "network_error"
                return cache_entry["payload"], make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=last_status, message="Live request failed; stale cached response used", duration_ms=int((time.perf_counter() - started) * 1000), attempts=attempts, retry_count=max(0, attempts - 1), fallback_used=True, fallback_reason=reason, stale_cache_used=True, http_status=last_http_status, error_type=last_error_type, **cache_meta, details=last_details)

        return None, make_source_diagnostic(name=f"RIPEstat {endpoint}", endpoint=endpoint, status=last_status, message=f"RIPEstat {endpoint} could not be queried after {attempts} attempts.", duration_ms=int((time.perf_counter() - started) * 1000), cached=False, freshness="LIVE", attempts=attempts, retry_count=max(0, attempts - 1), fallback_used=False, stale_cache_used=False, http_status=last_http_status, error_type=last_error_type, details=last_details)

    def _get_demo_data(self, endpoint: str, params: dict) -> dict:
        resource = str(params.get("resource", "")).upper()
        if endpoint == "as-overview" and resource == "AS3320":
            return {"data": {"resource": "AS3320", "holder": "DEMO: Deutsche Telekom AG", "announced": True}, "demo_mode": True}
        if endpoint == "announced-prefixes" and resource == "AS3320":
            return {"data": {"resource": "AS3320", "organisation": "Demo Networks Ltd.", "as-name": "DEMO-AS", "prefixes": [{"prefix": "192.0.2.0/24"}, {"prefix": "198.51.100.0/24"}, {"prefix": "203.0.113.0/24"}, {"prefix": "2001:db8::/32"}]}, "demo_mode": True}
        if endpoint == "as-overview" and resource == "AS4491":
            return {"data": {"resource": "AS4491", "holder": "DEMO: CNC Group CHINA169 Backbone", "announced": False}, "demo_mode": True}
        if endpoint == "announced-prefixes" and resource == "AS4491":
            return {"data": {"resource": "AS4491", "prefixes": []}, "demo_mode": True}
        if endpoint == "whois":
            return {"data": {"resource": resource, "records": [{"key": "organisation", "value": "Demo Networks Ltd."}, {"key": "netname", "value": "DEMO-NET"}], "holder": "Demo Networks Ltd."}, "demo_mode": True}
        if endpoint == "routing-status":
            demo_routing = {"192.0.2.0/24": {"data": {"routes": [{"origin": "AS3320"}]}, "demo_mode": True}, "198.51.100.0/24": {"data": {"routes": [{"origin": "AS64496"}]}, "demo_mode": True}, "203.0.113.0/24": {"data": {"visibility": [{"prefix": "203.0.113.0/24"}]}, "demo_mode": True}, "203.0.114.0/24": {"error": "demo upstream timeout", "demo_mode": True}}
            return demo_routing.get(resource.lower(), {"data": {}, "demo_mode": True})
        if endpoint == "rpki-validation":
            prefix = str(params.get("resource", "")).lower()
            origin_param = params.get('prefix') or params.get('origin_asn') or params.get('origin')
            origin = str(origin_param or '').strip().upper()
            statuses = {("192.0.2.0/24", "AS3320"): "valid", ("198.51.100.0/24", "AS3320"): "invalid_asn", ("203.0.113.0/24", "AS3320"): "invalid_length", ("2001:db8::/32", "AS3320"): "unknown"}
            status = statuses.get((prefix, origin), "unknown")
            return {"data": {"status": status}, "demo_mode": True}
        return {"error": f"No demo data for endpoint '{endpoint}'", "endpoint": endpoint, "params": params, "demo_mode": True}
