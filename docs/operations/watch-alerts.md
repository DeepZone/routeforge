# Watch Webhook Alerts

- Alerts are controlled by:
  - `ALERT_WEBHOOK_ENABLED`
  - `ALERT_WEBHOOK_URL`
  - `ALERT_ON_STATUS_CHANGE_ONLY`
  - `ALERT_WEBHOOK_MAX_RETRIES`
  - `ALERT_WEBHOOK_TIMEOUT_SECONDS`
- HMAC header (optional): `X-RouteForge-Signature: sha256=<hex>` over `timestamp.body`.
- Additional headers:
  - `X-RouteForge-Event`
  - `X-RouteForge-Timestamp`
- Payload includes watch identifiers, previous/current status, summary, report ID and timestamp.
- Watch run records expose `alert_delivery_status`, `alert_delivered_at`, and truncated `alert_error_message`.
- Secrets are never returned in status payloads, reports, or UI.
