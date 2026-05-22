from app.core.status import CheckStatus


def evaluate_prefix_overall(
    rpki_check: dict,
    registry_check: dict,
    routing_visibility_check: dict | None,
    prefix: str,
    origin_as: str | None,
) -> dict:
    _ = prefix
    statuses = {
        "rpki": _normalize_status(rpki_check.get("status")),
        "registry": _normalize_status(registry_check.get("status")),
        "routing": _normalize_status((routing_visibility_check or {}).get("status")),
    }

    if not origin_as:
        return _warning("No complete prefix-origin check possible", "Without an origin AS, a complete combined assessment of RPKI, registry/IRR, and routing visibility is not possible.")

    if CheckStatus.CRITICAL in statuses.values():
        if statuses["routing"] == CheckStatus.CRITICAL:
            return _critical("RPKI and registry look plausible, but visible routing origin differs.", "The prefix is visible, but not with the expected origin AS.")
        if statuses["rpki"] == CheckStatus.CRITICAL:
            return _critical("Das Prefix ist zwar sichtbar, aber RPKI meldet ein kritisches Problem.", "RPKI bewertet das Prefix-Origin-Paar kritisch, obwohl andere Checks ggf. positive Hinweise liefern.")
        return _critical("Registry/IRR origin conflicts with the provided origin AS.", "A discovered route/route6 origin differs from the checked origin AS.")

    if statuses["rpki"] == statuses["registry"] == statuses["routing"] == CheckStatus.UNKNOWN:
        return _unknown("No reliable overall assessment possible.", "RPKI, Registry/IRR, and routing visibility do not provide a reliable assessment.")

    if statuses["rpki"] == CheckStatus.OK and statuses["registry"] == CheckStatus.OK and statuses["routing"] == CheckStatus.OK:
        return {
            "status": CheckStatus.OK.value,
            "summary": "Prefix-origin pair appears authorized, documented, and visible.",
            "explanation": "RPKI, Registry/IRR, and routing visibility show a consistent result.",
            "risk": "No obvious inconsistency is currently visible.",
            "recommendations": ["Continue monitoring routing visibility and RPKI/registry data."],
        }

    if statuses["rpki"] == CheckStatus.OK and statuses["registry"] == CheckStatus.OK and statuses["routing"] == CheckStatus.UNKNOWN:
        return _warning("Routing visibility could not be determined reliably.", "RPKI and Registry/IRR are plausible, but routing visibility remains unclear.")

    if CheckStatus.WARNING in statuses.values():
        return _warning("Combined prefix evaluation shows warnings.", "At least one individual check reports incomplete or uncertain data.")

    if CheckStatus.UNKNOWN in statuses.values():
        return _warning("Partially confirmed data with uncertainty.", "At least one source is unclear; the overall assessment remains conservatively WARNING.")

    return _unknown("Combined prefix evaluation is not clearly determinable.", "The available individual results could not be combined consistently.")


def _warning(summary: str, explanation: str) -> dict:
    return {
        "status": CheckStatus.WARNING.value,
        "summary": summary,
        "explanation": explanation,
        "risk": "The overall conclusion remains limited.",
        "recommendations": ["Review individual checks and raw data in detail."],
    }


def _critical(summary: str, explanation: str) -> dict:
    return {
        "status": CheckStatus.CRITICAL.value,
        "summary": summary,
        "explanation": explanation,
        "risk": "Increased risk of misrouting, reachability issues, or security incidents.",
        "recommendations": ["Prioritize checking and resolving the discrepancy."],
    }


def _unknown(summary: str, explanation: str) -> dict:
    return {
        "status": CheckStatus.UNKNOWN.value,
        "summary": summary,
        "explanation": explanation,
        "risk": "The data is insufficient for a reliable routing security assessment.",
        "recommendations": ["Repeat the check later and verify raw data."],
    }


def _normalize_status(value: str | None) -> CheckStatus:
    mapping = {s.value: s for s in CheckStatus}
    return mapping.get((value or "UNKNOWN").upper(), CheckStatus.UNKNOWN)
