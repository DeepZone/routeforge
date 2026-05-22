from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.core.status import CheckStatus
from app.services.ripe_stat_client import RipeStatClient


class BgpVisibilityService:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def check(self, prefix: str, expected_origin_as: str | None) -> dict:
        normalized_prefix = validate_prefix(prefix)
        normalized_expected = format_asn(normalize_asn(expected_origin_as)) if expected_origin_as else None

        routing_payload, routing_diag = self.client.get_with_diagnostics("routing-status", {"resource": normalized_prefix})
        bgp_state_payload, bgp_state_diag = self.client.get_with_diagnostics("bgp-state", {"resource": normalized_prefix})
        routing_payload = routing_payload or {}
        bgp_state_payload = bgp_state_payload or {}

        routing_data = routing_payload.get("data", {}) if isinstance(routing_payload, dict) else {}
        bgp_data = bgp_state_payload.get("data", {}) if isinstance(bgp_state_payload, dict) else {}

        origins = sorted({str(item.get("origin", "")).upper() for item in (routing_data.get("routes") or []) if isinstance(item, dict) and item.get("origin")})
        visible = bool(origins or routing_data.get("visibility") or bgp_data.get("bgp_state"))
        expected_seen = normalized_expected in origins if normalized_expected else None
        multiple_origins = len(origins) > 1
        peer_count = routing_data.get("num_peers_seeing") or bgp_data.get("num_peers_seeing")
        more_specifics = routing_data.get("more_specifics") or bgp_data.get("more_specifics") or []
        less_specifics = routing_data.get("less_specifics") or bgp_data.get("less_specifics") or []

        data_unreliable = (not routing_data and not bgp_data) or (routing_payload.get("error") and bgp_state_payload.get("error"))

        if data_unreliable:
            status = CheckStatus.UNKNOWN.value
            summary = "No reliable BGP visibility data is available for the prefix."
            recommendations = ["Check again later and use external monitoring for cross-validation."]
        elif not visible:
            status = CheckStatus.CRITICAL.value if normalized_expected else CheckStatus.WARNING.value
            summary = "The prefix is currently not visible."
            recommendations = ["Check announcement path and upstream policy.", "Validate route propagation across multiple looking glasses."]
        elif normalized_expected and not expected_seen:
            status = CheckStatus.CRITICAL.value
            summary = f"The expected origin {normalized_expected} is not visible for {normalized_prefix} ."
            recommendations = ["Check origin-AS configuration.", "Investigate potential route leaks/hijacks."]
        elif multiple_origins:
            status = CheckStatus.WARNING.value
            summary = "Prefix is visible but has multiple origin ASNs (MOAS)."
            recommendations = ["Confirm multi-origin behavior or fix unintended announcements."]
        else:
            status = CheckStatus.OK.value
            summary = "Prefix is visible and the expected origin AS (if provided) is observed."
            recommendations = ["Continue monitoring; this result is a point-in-time snapshot of external visibility data."]

        return {
            "status": status,
            "summary": summary,
            "explanation": "BGP Visibility basiert auf RIPEstat-Daten und ist read-only.",
            "risk": "External visibility data may be delayed or incomplete.",
            "recommendations": recommendations,
            "input": {"prefix": normalized_prefix, "expected_origin_as": normalized_expected},
            "checks": None,
            "details": {
                "prefix": normalized_prefix,
                "visible": visible,
                "origins": origins,
                "expected_origin_as": normalized_expected,
                "expected_origin_seen": expected_seen,
                "multiple_origins": multiple_origins,
                "peer_count": peer_count,
                "more_specifics": more_specifics,
                "less_specifics": less_specifics,
                "source_diagnostics": [d for d in [routing_diag, bgp_state_diag] if isinstance(d, dict)],
                "source_errors": {
                    "routing_status": routing_payload.get("error") if isinstance(routing_payload, dict) else None,
                    "bgp_state": bgp_state_payload.get("error") if isinstance(bgp_state_payload, dict) else None,
                },
            },
            "sources": ["RIPEstat routing-status", "RIPEstat bgp-state"],
        }
