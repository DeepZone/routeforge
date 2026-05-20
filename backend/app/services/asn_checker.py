from collections.abc import Iterable

from app.core.normalize import format_asn, normalize_asn
from app.core.status import CheckStatus
from app.config import settings
from app.core.holder_extraction import extract_holder
from app.services.rpki_checker import RpkiChecker
from app.services.ripe_stat_client import RipeStatClient


class AsnChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def _extract_prefixes(self, announced_data: dict) -> list[str]:
        candidates = []
        if isinstance(announced_data, dict):
            for key in ("prefixes", "announced_prefixes", "prefix", "routes"):
                value = announced_data.get(key)
                if isinstance(value, list):
                    candidates.extend(value)

        extracted: list[str] = []
        seen = set()
        for item in candidates:
            prefix = None
            if isinstance(item, str):
                prefix = item
            elif isinstance(item, dict):
                for k in ("prefix", "route", "resource", "cidr"):
                    if isinstance(item.get(k), str):
                        prefix = item[k]
                        break
            if prefix and "/" in prefix and prefix not in seen:
                seen.add(prefix)
                extracted.append(prefix)
        return extracted

    def check(self, asn_input: str) -> dict:
        asn = normalize_asn(asn_input)
        resource = format_asn(asn)
        overview, overview_diag = self.client.get_with_diagnostics("as-overview", {"resource": resource})
        prefixes, prefixes_diag = self.client.get_with_diagnostics("announced-prefixes", {"resource": resource})
        overview = overview or {}
        prefixes = prefixes or {}
        announced_data = prefixes.get("data", {}) if isinstance(prefixes, dict) else {}
        extracted_prefixes = self._extract_prefixes(announced_data if isinstance(announced_data, dict) else {})
        rpki_batch = self._build_rpki_batch_metadata(prefixes, announced_data, extracted_prefixes)

        errors = []
        if "error" in overview:
            errors.append("as-overview nicht erreichbar")
        if "error" in prefixes:
            errors.append("announced-prefixes nicht erreichbar")
        status = CheckStatus.UNKNOWN.value if errors else CheckStatus.OK.value
        summary = f"ASN {resource} geprüft."
        return {
            "status": status,
            "summary": summary,
            "explanation": "RPKI kann nicht für eine ASN allein bewertet werden. Für RPKI braucht RouteForge konkrete Prefix-Origin-Paare.",
            "risk": "Ohne Prefix-Origin-Paar ist keine direkte RPKI-Gültigkeitsaussage möglich.",
            "recommendations": ["Fehlende Datenquellen erneut abrufen."] if errors else ["Keine unmittelbare Aktion erforderlich."],
            "details": {
                "normalized_asn": asn,
                "resource": resource,
                "as_overview": overview.get("data", {}),
                "announced_prefixes": announced_data if isinstance(announced_data, dict) else {},
                "resource_holder": extract_holder(
                    {"_source": "as-overview", **(overview.get("data", {}) if isinstance(overview, dict) else {})},
                    {"_source": "prefix-overview", **(announced_data if isinstance(announced_data, dict) else {})},
                ),
                "extracted_prefixes": extracted_prefixes,
                "rpki_batch": rpki_batch,
                "rpki_applicable": False,
                "rpki_explanation": "RPKI validation requires a concrete prefix-origin pair. An ASN alone cannot be classified as RPKI-valid or invalid.",
                "rpki_next_step": "Validate announced prefixes for this ASN against the ASN as origin.",
                "warnings": errors,
                "source_errors": {
                    "as_overview": overview.get("error") if isinstance(overview, dict) else None,
                    "announced_prefixes": prefixes.get("error") if isinstance(prefixes, dict) else None,
                },
                "source_diagnostics": [overview_diag, prefixes_diag],
                "demo_mode": settings.demo_mode,
            },
            "sources": ["RIPEstat as-overview", "RIPEstat announced-prefixes"],
        }

    def check_rpki_batch(self, asn_input: str, limit: int) -> dict:
        asn = normalize_asn(asn_input)
        resource = format_asn(asn)
        prefixes_payload, prefixes_diag = self.client.get_with_diagnostics("announced-prefixes", {"resource": resource})
        prefixes_payload = prefixes_payload or {}
        announced_data = prefixes_payload.get("data", {}) if isinstance(prefixes_payload, dict) else {}
        extracted = self._extract_prefixes(announced_data if isinstance(announced_data, dict) else {})
        rpki_batch = self._build_rpki_batch_metadata(prefixes_payload, announced_data, extracted)
        selected = extracted[:limit]

        rpki_checker = RpkiChecker(self.client)
        results = []
        summary = {"valid": 0, "invalid": 0, "invalid_asn": 0, "invalid_length": 0, "unknown": 0, "errors": 0}
        has_critical = False
        has_warning = False

        diag_agg = {"total_requests": 0, "ok": 0, "errors": 0, "timeouts": 0, "rate_limited": 0, "unknown_structure": 0}
        for prefix in selected:
            try:
                rpki = rpki_checker.check(prefix, resource)
                diag = rpki.get("source_diagnostic") or {}
                diag_agg["total_requests"] += 1
                st = diag.get("status")
                if st == "OK": diag_agg["ok"] += 1
                elif st == "TIMEOUT": diag_agg["timeouts"] += 1
                elif st == "RATE_LIMITED": diag_agg["rate_limited"] += 1
                elif st == "UNKNOWN_STRUCTURE": diag_agg["unknown_structure"] += 1
                else: diag_agg["errors"] += 1 if st and st != "OK" else 0
                raw_status = (rpki.get("raw_status") or "").strip().lower().replace("-", "_")
                if raw_status in summary:
                    summary[raw_status] += 1
                elif raw_status:
                    summary["unknown"] += 1
                if rpki.get("status") == CheckStatus.CRITICAL.value:
                    has_critical = True
                elif rpki.get("status") == CheckStatus.WARNING.value:
                    has_warning = True
                results.append({
                    "prefix": prefix,
                    "origin_as": resource,
                    "rpki_raw_status": rpki.get("raw_status"),
                    "status": rpki.get("status"),
                    "summary": rpki.get("summary"),
                    "raw": rpki.get("raw", {}),
                })
            except Exception:
                summary["errors"] += 1
                has_warning = True
                results.append({"prefix": prefix, "origin_as": resource, "rpki_raw_status": None, "status": CheckStatus.WARNING.value, "summary": "Prefix check failed", "raw": {}})

        if not selected:
            status = CheckStatus.UNKNOWN.value
        elif has_critical:
            status = CheckStatus.CRITICAL.value
        elif has_warning:
            status = CheckStatus.WARNING.value
        else:
            status = CheckStatus.OK.value

        summary_text = f"RPKI-Batchprüfung für {resource}: {len(selected)} Prefixe geprüft."
        explanation = "RPKI wurde für sichtbare Prefix-Origin-Paare der ASN geprüft."
        recommendations = ["Kritische Ergebnisse priorisiert prüfen.", "Warnungen auf fehlende ROA-Abdeckung untersuchen."]
        if not selected:
            summary_text = f"RPKI-Batchprüfung für {resource} nicht möglich."
            explanation = "Für diese ASN konnten keine auswertbaren Prefixe gefunden werden."
            recommendations = [
                "Prüfe, ob die ASN aktuell Prefixe announced.",
                "Wiederhole die Abfrage später.",
                "Prüfe die Rohdaten der announced-prefixes Antwort.",
            ]

        return {
            "status": status,
            "summary": summary_text,
            "explanation": explanation,
            "risk": "Kritische oder warnende Einzelresultate können auf Routing-Risiken hinweisen.",
            "recommendations": recommendations,
            "input": {"asn": resource, "limit": limit},
            "checks": None,
            "details": {
                "asn": resource,
                "checked_prefixes": len(selected),
                "total_prefixes_seen": len(extracted),
                "limited": len(extracted) > limit,
                "rpki_summary": summary,
                "results": results,
                "rpki_batch": rpki_batch,
                "announced_prefixes": announced_data if isinstance(announced_data, dict) else {},
                "source_diagnostics": [prefixes_diag, {"name": "RIPEstat rpki-validation (batch)", "endpoint": "rpki-validation", "status": "OK" if diag_agg["errors"] == 0 and diag_agg["timeouts"] == 0 and diag_agg["rate_limited"] == 0 else "ERROR", "message": "Aggregated RPKI batch diagnostics", "details": diag_agg}],
                "demo_mode": settings.demo_mode,
            },
        }

    def _build_rpki_batch_metadata(self, prefixes_payload: dict, announced_data: dict, extracted_prefixes: list[str]) -> dict:
        if extracted_prefixes:
            return {
                "available": True,
                "reason_code": "prefixes_available",
                "message": f"RPKI-Batchprüfung ist möglich. Es wurden {len(extracted_prefixes)} sichtbare Prefixe gefunden.",
                "prefix_count": len(extracted_prefixes),
                "can_retry": False,
            }
        if isinstance(prefixes_payload, dict) and prefixes_payload.get("error"):
            return {
                "available": False,
                "reason_code": "announced_prefixes_error",
                "message": "Die angekündigten Prefixe konnten über RIPEstat nicht geladen werden. Eine RPKI-Batchprüfung ist deshalb aktuell nicht möglich.",
                "prefix_count": 0,
                "can_retry": True,
            }
        if isinstance(announced_data, dict) and announced_data:
            return {
                "available": False,
                "reason_code": "no_prefixes_extracted",
                "message": "Für diese ASN wurden in der RIPEstat-Antwort keine auswertbaren Prefixe gefunden. Entweder announced die ASN aktuell keine Prefixe in dieser Quelle oder die Datenstruktur konnte nicht interpretiert werden.",
                "prefix_count": 0,
                "can_retry": True,
            }
        return {
            "available": False,
            "reason_code": "no_announced_prefixes",
            "message": "Für diese ASN wurden keine sichtbaren Prefixe gefunden. Ohne Prefixe kann RouteForge keine RPKI-Batchprüfung durchführen.",
            "prefix_count": 0,
            "can_retry": True,
        }
