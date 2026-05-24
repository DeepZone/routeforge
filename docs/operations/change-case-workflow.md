# Change Case Workflow

1. Create change case.
2. Populate `affected_prefixes` and `planned_origin_asns`.
3. Run `POST /api/change-cases/{id}/run-preflight`.
4. Review `decision`, `risk_summary`, and `required_actions`.
5. Execute routing change outside RouteForge (RouteForge is read-only).
6. Run `POST /api/change-cases/{id}/run-post-change-verification`.
7. Review `post_change_status` (`VERIFIED`, `PARTIAL`, `FAILED`, `UNKNOWN`) and detected issues.

Decision values: `GO`, `CAUTION`, `NO-GO`, `UNKNOWN`.
