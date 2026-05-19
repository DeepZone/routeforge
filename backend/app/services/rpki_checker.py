from app.core.recommendations import evaluate_rpki_status
from app.core.status import CheckStatus
from app.core.normalize import format_asn
from app.services.ripe_stat_client import RipeStatClient


class RpkiChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def check(self, prefix: str, origin_as: str | None) -> dict:
        if not origin_as:
            evaluation = evaluate_rpki_status(None, prefix, None)
            return {**evaluation, "raw_status": None, "raw": {}}

        payload = self.client.get("rpki-validation", {"resource": prefix, "prefix": prefix, "origin": origin_as})
        status_raw = payload.get("data", {}).get("status") if isinstance(payload, dict) else None
        evaluation = evaluate_rpki_status(status_raw, prefix, origin_as)

        if isinstance(payload, dict) and payload.get("error"):
            evaluation = {
                "status": CheckStatus.UNKNOWN.value,
                "summary": "RPKI status could not be determined",
                "explanation": "Die RIPEstat-Quelle war nicht erreichbar oder lieferte unerwartete Daten.",
                "risk": "Die Bewertung ist unvollständig.",
                "recommendations": [
                    "Prüfe die API-Rohdaten.",
                    "Wiederhole die Prüfung später.",
                    "Vergleiche bei Bedarf mit einer zweiten Quelle oder einem lokalen RPKI-Validator.",
                ],
            }

        return {**evaluation, "raw_status": status_raw, "raw": payload}
