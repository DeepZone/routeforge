import httpx
import hmac, hashlib, json
from datetime import datetime, timezone
from app.config import settings

def send_watch_webhook(payload: dict) -> tuple[str,str|None]:
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
    try:
        httpx.post(settings.alert_webhook_url,data=body,headers={**headers,'Content-Type':'application/json'},timeout=settings.alert_webhook_timeout_seconds)
        return 'sent', None
    except Exception as exc:
        return 'failed', str(exc)
