from app.core.recommendations import evaluate_rpki_status
from app.services.providers.rpki import RpkiProviderService


class RpkiChecker:
    def __init__(self, client):
        self.provider = RpkiProviderService(client)

    def check(self, prefix: str, origin_as: str | None) -> dict:
        provider_result = self.provider.check(prefix, origin_as)
        evaluation = evaluate_rpki_status(provider_result.get("validation_status"), prefix, origin_as)
        return {
            **evaluation,
            "raw_status": provider_result.get("validation_status"),
            "source_diagnostic": (provider_result.get("source_diagnostics") or [None])[0],
            "provider": provider_result.get("provider"),
            "provider_status": provider_result.get("provider_status"),
            "matched_roas": provider_result.get("matched_roas", []),
            "checked_prefix": provider_result.get("checked_prefix"),
            "checked_origin_as": provider_result.get("checked_origin_as"),
            "fallback_used": provider_result.get("fallback_used", False),
            "fallback_reason": provider_result.get("fallback_reason"),
            "source_diagnostics": provider_result.get("source_diagnostics", []),
            "provider_disagreement": provider_result.get("provider_disagreement", False),
            "raw": provider_result.get("raw", {}),
        }
