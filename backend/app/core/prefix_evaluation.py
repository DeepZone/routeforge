from app.core.status import CheckStatus


def evaluate_prefix_overall(
    rpki_check: dict,
    registry_check: dict,
    prefix: str,
    origin_as: str | None,
) -> dict:
    _ = prefix
    rpki_status = _normalize_status(rpki_check.get("status"))
    registry_status = _normalize_status(registry_check.get("status"))

    if not origin_as:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "Keine vollständige Prefix-Origin-Prüfung möglich",
            "explanation": "Ohne Origin-AS ist keine vollständige kombinierte Bewertung von RPKI und Registry-Origin möglich.",
            "risk": "Die Gesamtaussage bleibt eingeschränkt, weil die Origin-Autorisierung nicht vollständig geprüft werden kann.",
            "recommendations": [
                "Origin-AS ergänzen, um die kombinierte Prefix-Bewertung zu vervollständigen.",
                "RPKI- und Registry/IRR-Hinweise danach erneut gemeinsam prüfen.",
            ],
        }

    if CheckStatus.CRITICAL in {rpki_status, registry_status}:
        if registry_status == CheckStatus.CRITICAL:
            return {
                "status": CheckStatus.CRITICAL.value,
                "summary": "Registry/IRR-Origin widerspricht dem angegebenen Origin-AS.",
                "explanation": "Ein gefundenes route/route6-Origin weicht vom geprüften Origin-AS ab.",
                "risk": "Hohe Wahrscheinlichkeit für Konfigurations- oder Dokumentationsfehler mit Hijack-/Erreichbarkeitsrisiko.",
                "recommendations": [
                    "Origin-AS und route/route6-Objekte in der zuständigen Registry sofort abgleichen.",
                    "Fehlerhafte Registry-Einträge korrigieren.",
                ],
            }
        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "RPKI meldet ein kritisches Problem trotz plausibler Registry-Daten.",
            "explanation": "Registry/IRR-Daten wirken plausibel, aber RPKI würde diese Route als problematisch bewerten. Validierende Netze können die Route verwerfen.",
            "risk": "Akute Erreichbarkeitsrisiken durch mögliche Routenverwerfung in ROV-validierenden Netzen.",
            "recommendations": [
                "Origin-AS und ROA-Zuordnung priorisiert prüfen.",
                "RPKI-Inkonsistenz beheben und Prüfung erneut durchführen.",
            ],
        }

    if rpki_status == CheckStatus.UNKNOWN and registry_status == CheckStatus.UNKNOWN:
        return {
            "status": CheckStatus.UNKNOWN.value,
            "summary": "Keine belastbare Gesamtbewertung möglich.",
            "explanation": "Sowohl RPKI als auch Registry/IRR liefern keine verlässliche Aussage.",
            "risk": "Die Datenlage ist unzureichend für eine belastbare Routing-Sicherheitsbewertung.",
            "recommendations": [
                "Prüfung später wiederholen.",
                "Rohdaten und Quellfehler in beiden Checks kontrollieren.",
            ],
        }

    if rpki_status == CheckStatus.OK and registry_status == CheckStatus.OK:
        return {
            "status": CheckStatus.OK.value,
            "summary": "Prefix-Origin-Paar wirkt plausibel und RPKI-valid.",
            "explanation": "RPKI bestätigt die Origin-Autorisierung und Registry/IRR-Daten enthalten passende Hinweise.",
            "risk": "Derzeit kein akutes Risiko aus RPKI- oder Registry-Sicht erkennbar.",
            "recommendations": ["Weiterhin regelmäßig überwachen und Dokumentation aktuell halten."],
        }

    if rpki_status == CheckStatus.OK and registry_status == CheckStatus.WARNING:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "RPKI ist gültig, Registry/IRR-Dokumentation ist unvollständig.",
            "explanation": "Das Prefix-Origin-Paar ist RPKI-valid, aber in den Registry-/IRR-Daten wurde kein klares passendes route/route6-Objekt gefunden.",
            "risk": "Technisch aktuell stabil möglich, aber mit Dokumentations- und Nachvollziehbarkeitslücke.",
            "recommendations": [
                "Registry-/IRR-Daten auf vollständige route/route6-Dokumentation prüfen.",
            ],
        }

    if rpki_status == CheckStatus.WARNING and registry_status == CheckStatus.WARNING:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "Routing-Sicherheitslage ist unvollständig dokumentiert.",
            "explanation": "Weder RPKI noch Registry/IRR liefern eine vollständig belastbare Bestätigung.",
            "risk": "Erhöhtes operatives Risiko durch fehlende oder unvollständige Absicherung.",
            "recommendations": ["RPKI- und Registry-Daten gemeinsam vervollständigen und erneut prüfen."],
        }

    # Konservativ: Teilweise positive Ergebnisse mit UNKNOWN bleiben WARNING.
    if (rpki_status, registry_status) in {
        (CheckStatus.OK, CheckStatus.UNKNOWN),
        (CheckStatus.UNKNOWN, CheckStatus.OK),
    }:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "Teilweise bestätigte Datenlage mit Unsicherheit.",
            "explanation": "Eine Quelle bestätigt die Plausibilität, die andere bleibt unklar. Die Gesamtbewertung ist daher konservativ WARNING.",
            "risk": "Verbleibende Unsicherheit kann zu Fehlannahmen in der Routing-Bewertung führen.",
            "recommendations": [
                "Unklare Quelle gezielt nachprüfen und Datenlage vervollständigen.",
            ],
        }

    if CheckStatus.WARNING in {rpki_status, registry_status}:
        return {
            "status": CheckStatus.WARNING.value,
            "summary": "Kombinierte Prefix-Bewertung zeigt Warnhinweise.",
            "explanation": "Mindestens eine Einzelprüfung meldet eine unvollständige oder unsichere Datenlage.",
            "risk": "Routing-Sicherheitsbewertung ist nicht vollständig belastbar.",
            "recommendations": ["Hinweise aus RPKI und Registry/IRR gezielt nacharbeiten."],
        }

    return {
        "status": CheckStatus.UNKNOWN.value,
        "summary": "Kombinierte Prefix-Bewertung nicht eindeutig bestimmbar.",
        "explanation": "Die vorliegenden Einzelergebnisse konnten nicht konsistent kombiniert werden.",
        "risk": "Die Gesamtaussage bleibt unklar.",
        "recommendations": ["Einzelprüfungen und Rohdaten manuell verifizieren."],
    }


def _normalize_status(value: str | None) -> CheckStatus:
    mapping = {s.value: s for s in CheckStatus}
    return mapping.get((value or "UNKNOWN").upper(), CheckStatus.UNKNOWN)
