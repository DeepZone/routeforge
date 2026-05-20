from __future__ import annotations

from collections.abc import Iterable

UNKNOWN = {"holder": "Unknown", "holder_source": "unknown", "holder_confidence": "unknown"}

_SKIP_KEYS = {"abuse-c", "admin-c", "tech-c", "abuse_c", "admin_c", "tech_c"}
_HIGH_KEYS = {"organisation", "org-name", "organization"}
_MEDIUM_KEYS = {"holder", "resource_holder", "holder_name"}
_LOW_KEYS = {"as-name", "name", "netname", "descr", "org"}


def _source_from_label(label: str | None) -> str:
    text = (label or "").lower()
    if "as-overview" in text:
        return "as-overview"
    if "prefix" in text:
        return "prefix-overview"
    if "whois" in text:
        return "whois"
    if "registry" in text:
        return "registry"
    return "unknown"


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("_", "-")


def _walk(payload: object, out: list[tuple[str, str]]) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            nkey = _normalize_key(str(key))
            if nkey in _SKIP_KEYS:
                continue
            if isinstance(value, str) and value.strip():
                out.append((nkey, value.strip()))
            _walk(value, out)
    elif isinstance(payload, list):
        for item in payload:
            _walk(item, out)


def extract_holder(*payloads: dict) -> dict:
    best: tuple[int, str, str] | None = None
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        source = _source_from_label(str(payload.get("_source")))
        candidates: list[tuple[str, str]] = []
        _walk(payload, candidates)
        for key, value in candidates:
            if key in _HIGH_KEYS:
                score, conf = 0, "high"
            elif key in _MEDIUM_KEYS:
                score, conf = 1, "medium"
            elif key in _LOW_KEYS:
                score, conf = 2, "low"
            else:
                continue
            if best is None or score < best[0]:
                best = (score, value, source)

    if best is None:
        return dict(UNKNOWN)

    confidence = {0: "high", 1: "medium", 2: "low"}.get(best[0], "unknown")
    return {"holder": best[1], "holder_source": best[2], "holder_confidence": confidence}
