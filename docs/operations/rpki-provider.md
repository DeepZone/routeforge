# RPKI Provider Operations

- `RPKI_PROVIDER`: `ripestat`, `routinator`, `local-json`, or `auto`.
- `auto` tries local provider first (`routinator`) and can fallback to RIPEstat if `RPKI_FALLBACK_TO_RIPESTAT=true`.
- `RPKI_ROUTINATOR_URL` points to a read-only Routinator API endpoint.
- `RPKI_LOCAL_JSON_PATH` is used by `local-json` mode and must contain ROA-like JSON entries.
- Runtime output includes provider, fallback flags, disagreement indicators, and matched ROAs.
- RouteForge remains read-only: no ROA creation/writes.
