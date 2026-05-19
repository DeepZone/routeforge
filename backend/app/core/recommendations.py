from app.core.status import CheckStatus


def default_recommendations(status: CheckStatus) -> list[str]:
    if status == CheckStatus.OK:
        return ["Keine unmittelbare Aktion erforderlich. Monitoring fortsetzen."]
    if status == CheckStatus.WARNING:
        return ["RPKI/Registry-Daten prüfen und Abdeckung verbessern."]
    if status == CheckStatus.CRITICAL:
        return ["Origin-AS und ROA sofort verifizieren, da Route verworfen werden kann."]
    return ["Erneut prüfen; externe Datenquelle war unzuverlässig oder nicht erreichbar."]


def evaluate_rpki_status(rpki_status: str | None, prefix: str, origin_as: str | None) -> dict:
    _ = prefix
    if not origin_as:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "Origin-AS missing",
            "explanation": "Für eine vollständige RPKI-Prüfung wird ein Origin-AS benötigt.",
            "risk": "Ohne Origin-AS kann nicht geprüft werden, ob eine konkrete Route RPKI-valid wäre.",
            "recommendations": [
                "Ergänze das Origin-AS, zum Beispiel AS3333.",
                "Nutze den ASN-Check, um mögliche Origin-AS-Informationen zu finden.",
            ],
        }

    normalized = (rpki_status or "").strip().lower().replace("-", "_")
    if normalized == "valid":
        return {
            "status": CheckStatus.OK.value,
            "summary": "RPKI validation successful",
            "explanation": "Das Prefix-Origin-Paar ist durch einen passenden ROA abgedeckt.",
            "risk": "Kein akutes RPKI-Risiko erkennbar.",
            "recommendations": ["Keine akute Maßnahme erforderlich."],
        }
    if normalized == "invalid":
        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "RPKI validation failed",
            "explanation": "Das Prefix wird mit einem Origin-AS geprüft, das nicht durch einen passenden ROA gedeckt ist.",
            "risk": "Validierende Netze können diese Route verwerfen. Dadurch kann Erreichbarkeit verloren gehen.",
            "recommendations": [
                "Prüfe, ob das Origin-AS korrekt ist.",
                "Prüfe bestehende ROAs für das Prefix.",
                "Erstelle oder korrigiere den ROA nur, wenn du zur Verwaltung dieser Ressourcen berechtigt bist.",
            ],
        }
    if normalized in {"not_found", "unknown_roa", "notfound"}:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "No matching ROA found",
            "explanation": "Für dieses Prefix-Origin-Paar wurde kein passender ROA gefunden.",
            "risk": "Das ist nicht automatisch ein Ausfall, schwächt aber die Routing-Sicherheit.",
            "recommendations": [
                "Prüfe, ob für dieses Prefix ein ROA angelegt werden sollte.",
                "Lege einen ROA nur an, wenn du zur Verwaltung der Ressource berechtigt bist.",
                "Achte auf eine passende maxLength, damit keine unbeabsichtigten Subprefixe autorisiert werden.",
            ],
        }

    return {
        "status": CheckStatus.UNKNOWN.value,
        "summary": "RPKI status could not be determined",
        "explanation": "Der RPKI-Status konnte nicht zuverlässig ermittelt werden.",
        "risk": "Die Bewertung ist unvollständig.",
        "recommendations": [
            "Prüfe die API-Rohdaten.",
            "Wiederhole die Prüfung später.",
            "Vergleiche bei Bedarf mit einer zweiten Quelle oder einem lokalen RPKI-Validator.",
        ],
    }
