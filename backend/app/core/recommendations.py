from app.core.status import CheckStatus


def default_recommendations(status: CheckStatus) -> list[str]:
    if status == CheckStatus.OK:
        return ["No immediate action required. Continue monitoring."]
    if status == CheckStatus.WARNING:
        return ["Review RPKI/registry data and improve coverage."]
    if status == CheckStatus.CRITICAL:
        return ["Origin-AS und ROA sofort verifizieren, da Route verworfen werden kann."]
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
            "explanation": "Das Prefix wird mit einem Origin-AS geprüft, das nicht durch einen passenden ROA gedeckt ist.",
            "risk": "Validierende Netze können diese Route verwerfen. Dadurch kann Erreichbarkeit verloren gehen.",
            "recommendations": [
                "Check whether the origin AS is correct.",
                "Review existing ROAs for the prefix.",
                "Erstelle oder korrigiere den ROA nur, wenn du zur Verwaltung dieser Ressourcen berechtigt bist.",
            ],
        }
    if normalized == "invalid_asn":
        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "RPKI invalid: unauthorized origin AS",
            "explanation": "Für das Prefix existiert ein ROA, aber nicht für dieses Origin-AS.",
            "risk": "Validierende Netze können diese Route verwerfen, weil das Origin-AS nicht autorisiert ist.",
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
            "explanation": "Für das Prefix existiert ein ROA, aber die angekündigte Prefix-Länge ist länger als die erlaubte maxLength.",
            "risk": "Validierende Netze können diese Route verwerfen, obwohl das AS grundsätzlich passen kann.",
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
            "explanation": "Für dieses Prefix-Origin-Paar wurde kein passender ROA gefunden.",
            "risk": "Das ist nicht automatisch ein Ausfall, schwächt aber die Routing-Sicherheit.",
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
            "Vergleiche bei Bedarf mit einer zweiten Quelle oder einem lokalen RPKI-Validator.",
        ],
    }
