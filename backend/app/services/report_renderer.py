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
