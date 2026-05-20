from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_report(payload: dict) -> tuple[dict, str, str]:
    report_json = {"generated_at": datetime.utcnow().isoformat(), **payload}
    md = env.get_template("report.md.j2").render(report=report_json)
    html = env.get_template("report.html.j2").render(report=report_json)
    return report_json, md, html


def render_plain_summary(report_json: dict) -> str:
    data = report_json or {}
    details = data.get("details") or {}
    input_data = data.get("input") or {}
    holder = ((details.get("resource_holder") or {}).get("holder")) or "Unknown"
    status = data.get("status") or "Unknown"
    summary = data.get("summary") or "Unknown"
    risk = data.get("risk") or "Unknown"
    recommendations = data.get("recommendations") or []
    if not isinstance(recommendations, list):
        recommendations = [str(recommendations)]
    recommendations = [str(item) for item in recommendations if str(item).strip()]
    if not recommendations:
        recommendations = ["Unknown"]

    is_preflight = bool(input_data.get("planned_origin_as")) or str(data.get("check_type", "")).lower() == "preflight"
    check_type = data.get("check_type")
    if not check_type:
        if input_data.get("planned_origin_as"):
            check_type = "Preflight"
        elif input_data.get("asn"):
            check_type = "ASN"
        elif input_data.get("prefix"):
            check_type = "Prefix"
        else:
            check_type = "Unknown"
    check_type_label = str(check_type).replace("-", " ").title()

    lines = ["RouteForge Preflight Summary" if is_preflight else "RouteForge Result Summary"]
    if is_preflight:
        planned_prefix = input_data.get("prefix") or "Unknown"
        planned_origin = input_data.get("planned_origin_as") or "Unknown"
        lines.append(f"Planned Change: {planned_prefix} -> {planned_origin}")
    else:
        lines.append(f"Check Type: {check_type_label}")
        lines.append(f"Resource: {input_data.get('prefix') or input_data.get('asn') or data.get('input_resource') or 'Unknown'}")
        lines.append(f"Origin-AS: {input_data.get('origin_as') or 'Unknown'}")
    lines.append(f"Holder: {holder}")
    preflight_decision = details.get("preflight_decision")
    if preflight_decision:
        lines.append(f"Decision: {preflight_decision}")
    lines.append(f"Status: {status}")
    lines.extend(
        [
            "",
            "Summary:",
            str(summary),
            "",
            "Risk:",
            str(risk),
            "",
            "Recommendations:",
        ]
    )
    lines.extend([f"- {item}" for item in recommendations])
    return "\n".join(lines).strip() + "\n"
