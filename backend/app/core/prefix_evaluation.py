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
            return _critical("RPKI und Registry wirken plausibel, aber die sichtbare Routing-Origin weicht ab.", "Das Prefix ist sichtbar, aber nicht mit dem erwarteten Origin-AS.")
        if statuses["rpki"] == CheckStatus.CRITICAL:
            return _critical("Das Prefix ist zwar sichtbar, aber RPKI meldet ein kritisches Problem.", "RPKI bewertet das Prefix-Origin-Paar kritisch, obwohl andere Checks ggf. positive Hinweise liefern.")
        return _critical("Registry/IRR-Origin widerspricht dem angegebenen Origin-AS.", "Ein gefundenes route/route6-Origin weicht vom geprüften Origin-AS ab.")

    if statuses["rpki"] == statuses["registry"] == statuses["routing"] == CheckStatus.UNKNOWN:
        return _unknown("No reliable overall assessment possible.", "RPKI, Registry/IRR und Routing Visibility liefern keine verlässliche Aussage.")

    if statuses["rpki"] == CheckStatus.OK and statuses["registry"] == CheckStatus.OK and statuses["routing"] == CheckStatus.OK:
        return {
            "status": CheckStatus.OK.value,
            "summary": "Prefix-Origin-Paar wirkt autorisiert, dokumentiert und sichtbar.",
            "explanation": "RPKI, Registry/IRR und Routing Visibility zeigen ein konsistentes Ergebnis.",
            "risk": "Derzeit keine offensichtliche Inkonsistenz erkennbar.",
            "recommendations": ["Routing-Sichtbarkeit und RPKI/Registry-Daten weiter überwachen."],
        }

    if statuses["rpki"] == CheckStatus.OK and statuses["registry"] == CheckStatus.OK and statuses["routing"] == CheckStatus.UNKNOWN:
        return _warning("Routing visibility could not be determined reliably.", "RPKI und Registry/IRR sind plausibel, aber die Routing-Sichtbarkeit bleibt unklar.")

    if CheckStatus.WARNING in statuses.values():
        return _warning("Kombinierte Prefix-Bewertung zeigt Warnhinweise.", "Mindestens eine Einzelprüfung meldet unvollständige oder unsichere Daten.")

    if CheckStatus.UNKNOWN in statuses.values():
        return _warning("Teilweise bestätigte Datenlage mit Unsicherheit.", "Mindestens eine Quelle ist unklar; die Gesamtbewertung bleibt daher konservativ WARNING.")

    return _unknown("Kombinierte Prefix-Bewertung nicht eindeutig bestimmbar.", "Die vorliegenden Einzelergebnisse konnten nicht konsistent kombiniert werden.")


def _warning(summary: str, explanation: str) -> dict:
    return {
        "status": CheckStatus.WARNING.value,
        "summary": summary,
        "explanation": explanation,
        "risk": "Die Gesamtaussage bleibt eingeschränkt.",
        "recommendations": ["Individual checks und Rohdaten gezielt nacharbeiten."],
    }


def _critical(summary: str, explanation: str) -> dict:
    return {
        "status": CheckStatus.CRITICAL.value,
        "summary": summary,
        "explanation": explanation,
        "risk": "Erhöhtes Risk für Fehlrouting, Erreichbarkeitsprobleme oder Sicherheitsvorfälle.",
        "recommendations": ["Abweichung priorisiert prüfen und beheben."],
    }


def _unknown(summary: str, explanation: str) -> dict:
    return {
        "status": CheckStatus.UNKNOWN.value,
        "summary": summary,
        "explanation": explanation,
        "risk": "Die Datenlage ist unzureichend für eine belastbare Routing-Sicherheitsbewertung.",
        "recommendations": ["Prüfung später wiederholen und Rohdaten kontrollieren."],
    }


def _normalize_status(value: str | None) -> CheckStatus:
    mapping = {s.value: s for s in CheckStatus}
    return mapping.get((value or "UNKNOWN").upper(), CheckStatus.UNKNOWN)
