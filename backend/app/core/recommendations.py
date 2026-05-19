from app.core.status import CheckStatus


def default_recommendations(status: CheckStatus) -> list[str]:
    if status == CheckStatus.OK:
        return ["Keine unmittelbare Aktion erforderlich. Monitoring fortsetzen."]
    if status == CheckStatus.WARNING:
        return ["RPKI/Registry-Daten prüfen und Abdeckung verbessern."]
    if status == CheckStatus.CRITICAL:
        return ["Origin-AS und ROA sofort verifizieren, da Route verworfen werden kann."]
    return ["Erneut prüfen; externe Datenquelle war unzuverlässig oder nicht erreichbar."]
