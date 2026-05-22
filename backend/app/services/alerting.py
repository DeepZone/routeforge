from datetime import datetime, timezone
import hashlib
import hmac
import json

import httpx

from app.config import settings


MAX_ALERT_ERROR_MESSAGE_LENGTH = 500

def _trim_error_message(exc: Exception) -> str:
    return str(exc).strip()[:MAX_ALERT_ERROR_MESSAGE_LENGTH]


def send_watch_webhook(payload: dict) -> tuple[str, str | None]:
    if not settings.alert_webhook_enabled:
        return 'skipped_disabled', None
    if not settings.alert_webhook_url:
        return 'skipped_no_url', 'Webhook enabled but URL missing'
    ts=datetime.now(timezone.utc).isoformat()
    headers={'X-RouteForge-Event':payload.get('event','watch_status_changed'),'X-RouteForge-Timestamp':ts}
    body=json.dumps(payload, separators=(',',':'))
    if settings.alert_webhook_secret:
        sig=hmac.new(settings.alert_webhook_secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
        headers['X-RouteForge-Signature']=f'sha256={sig}'
    last_error: Exception | None = None
    attempts = max(1, settings.alert_webhook_max_retries + 1)
    for _ in range(attempts):
        try:
            response = httpx.post(
                settings.alert_webhook_url,
                data=body,
                headers={**headers, 'Content-Type': 'application/json'},
                timeout=settings.alert_webhook_timeout_seconds,
            )
            response.raise_for_status()
            return 'sent', None
        except Exception as exc:
            last_error = exc
    return 'failed', _trim_error_message(last_error) if last_error else 'webhook delivery failed'
