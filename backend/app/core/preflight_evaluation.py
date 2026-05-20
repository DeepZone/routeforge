from app.core.status import CheckStatus


def evaluate_preflight(
    rpki_check: dict,
    registry_check: dict,
    routing_visibility_check: dict,
    prefix: str,
    planned_origin_as: str,
) -> dict:
    _ = prefix
    _ = planned_origin_as
    statuses = {
        "rpki": _normalize_status(rpki_check.get("status")),
        "registry": _normalize_status(registry_check.get("status")),
        "routing": _normalize_status(routing_visibility_check.get("status")),
    }

    visible_origins = set((routing_visibility_check.get("raw", {}) or {}).get("visible_origins", []))
    visible_conflicts = len(visible_origins) > 1

    if statuses["rpki"] == statuses["registry"] == statuses["routing"] == CheckStatus.UNKNOWN:
        return _result(
            CheckStatus.UNKNOWN,
            "Preflight result could not be determined.",
            "The available data was insufficient to produce a reliable preflight assessment.",
            "No reliable go/no-go signal could be established from external sources.",
            ["Retry the preflight check later.", "Verify source availability before deployment."],
        )

    if CheckStatus.CRITICAL in statuses.values() or visible_conflicts:
        return _result(
            CheckStatus.CRITICAL,
            "Preflight check found a critical conflict.",
            "The planned Origin-AS conflicts with RPKI, Registry/IRR or visible routing data. Deploying this change may cause reachability issues.",
            "High risk of invalid announcement or traffic impact.",
            ["Do not deploy before resolving conflicts.", "Validate RPKI/IRR and visible origin data with operators."],
        )

    if statuses["rpki"] == CheckStatus.OK and statuses["registry"] == CheckStatus.OK and statuses["routing"] == CheckStatus.OK and not visible_conflicts:
        return _result(
            CheckStatus.OK,
            "Preflight check passed for planned Prefix-Origin announcement.",
            "RPKI, Registry/IRR and Routing Visibility show no obvious conflict for the planned Origin-AS.",
            "No obvious pre-deployment conflict detected.",
            ["Proceed with normal change process and post-deployment monitoring."],
        )

    return _result(
        CheckStatus.WARNING,
        "Preflight check completed with warnings.",
        "Some checks are incomplete or indicate missing documentation. The planned announcement may work, but should be reviewed before deployment.",
        "Moderate preflight uncertainty remains.",
        ["Review warnings and raw data before deployment.", "Confirm visibility and IRR/RPKI consistency manually if needed."],
    )


def _normalize_status(value: str | None) -> CheckStatus:
    mapping = {s.value: s for s in CheckStatus}
    return mapping.get((value or "UNKNOWN").upper(), CheckStatus.UNKNOWN)


def _result(status: CheckStatus, summary: str, explanation: str, risk: str, recommendations: list[str]) -> dict:
    return {
        "status": status.value,
        "summary": summary,
        "explanation": explanation,
        "risk": risk,
        "recommendations": recommendations,
    }
