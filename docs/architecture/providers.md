# Provider Architecture (Read-Only)

RouteForge provider integrations are read-only and only fetch/aggregate external routing and registry data.

## RPKI
- Provider abstraction: RIPEstat, Routinator, local JSON, auto fallback.
- Diagnostics: fallback usage, disagreement flags, source diagnostics.

## BGP Visibility
- Multi-source aggregation with provider-level diagnostics and confidence scoring.

## Security Model
- No write operations against routers, RIPE DB, IRR, or ROA systems.
- No secrets in frontend, reports, logs, or audit details.
