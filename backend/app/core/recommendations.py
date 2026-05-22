from app.core.status import CheckStatus


def default_recommendations(status: CheckStatus) -> list[str]:
    if status == CheckStatus.OK:
        return ["No immediate action required. Continue monitoring."]
    if status == CheckStatus.WARNING:
        return ["Review RPKI/registry data and improve coverage."]
    if status == CheckStatus.CRITICAL:
        return ["Verify origin AS and ROA immediately, because the route may be rejected."]
    return ["Check again; external data source was unreliable or unavailable."]


def evaluate_rpki_status(rpki_status: str | None, prefix: str, origin_as: str | None) -> dict:
    _ = prefix
    if not origin_as:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "Origin-AS missing",
            "explanation": "A complete RPKI check requires an origin AS.",
            "risk": "Without an origin AS, it cannot be verified whether a route would be RPKI valid.",
            "recommendations": [
                "Provide the origin AS, for example AS3333.",
                "Use the ASN check to find potential origin AS information.",
            ],
        }

    normalized = (rpki_status or "").strip().lower().replace("-", "_")
    if normalized == "valid":
        return {
            "status": CheckStatus.OK.value,
            "summary": "RPKI validation successful",
            "explanation": "Das Prefix-Origin-Paar ist durch einen passenden ROA abgedeckt.",
            "risk": "No immediate RPKI risk detected.",
            "recommendations": ["No urgent action required."],
        }
    if normalized == "invalid":
        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "RPKI validation failed",
            "explanation": "The prefix is checked with an origin AS that is not covered by a matching ROA.",
            "risk": "Validierende Netze können diese Route verwerfen. Dadurch kann Erreichbarkeit verloren gehen.",
            "recommendations": [
                "Check whether the origin AS is correct.",
                "Review existing ROAs for the prefix.",
                "Create or correct the ROA only if you are authorized to manage these resources.",
            ],
        }
    if normalized == "invalid_asn":
        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "RPKI invalid: unauthorized origin AS",
            "explanation": "A ROA exists for the prefix, but not for this origin AS.",
            "risk": "Validating networks may reject this route because the origin AS is not authorized.",
            "recommendations": [
                "Check the origin AS.",
                "Review the ROA.",
                "Nur korrigieren, wenn man zur Verwaltung der Ressource berechtigt ist.",
            ],
        }
    if normalized == "invalid_length":
        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "RPKI invalid: announced prefix too specific",
            "explanation": "A ROA exists for the prefix, but the announced prefix length is longer than the allowed maxLength.",
            "risk": "Validating networks may reject this route, even though the AS may otherwise match.",
            "recommendations": [
                "Check announced prefix length.",
                "Check ROA maxLength.",
                "Do not use an overly broad maxLength unless necessary.",
            ],
        }
    if normalized in {"unknown", "not_found", "unknown_roa", "notfound"}:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "No matching ROA found",
            "explanation": "No matching ROA was found for this prefix-origin pair.",
            "risk": "This is not automatically an outage, but it weakens routing security.",
            "recommendations": [
                "Check whether a ROA should be created.",
                "Nur anlegen, wenn man zur Verwaltung berechtigt ist.",
            ],
        }

    return {
        "status": CheckStatus.UNKNOWN.value,
        "summary": "RPKI status could not be determined",
        "explanation": "The RPKI status could not be determined reliably.",
        "risk": "The assessment is incomplete.",
        "recommendations": [
            "Review the API raw data.",
            "Repeat the check later.",
            "Compare with a secondary source or a local RPKI validator if needed.",
        ],
    }
