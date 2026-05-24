# BGP Visibility Providers

- `BGP_VISIBILITY_PROVIDERS` supports comma-separated providers (currently `ripestat,generic-http`).
- `generic-http` uses `BGP_GENERIC_URL_TEMPLATE` with `{prefix}` interpolation.
- Multi-source output includes:
  - provider/source list
  - visible origins by source
  - all visible origins
  - source agreement
  - confidence score
  - failed provider count
  - source diagnostics
- Conflicting origins and missing expected origin are exposed in reports/UI.
