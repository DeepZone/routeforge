import json

import typer
from fastapi.testclient import TestClient

from app.main import app as fastapi_app

app = typer.Typer()


@app.command("check-asn")
def check_asn(asn: str):
    with TestClient(fastapi_app) as client:
        r = client.post("/api/check/asn", json={"asn": asn})
        typer.echo(json.dumps(r.json(), indent=2, ensure_ascii=False))


@app.command("check-prefix")
def check_prefix(prefix: str, origin_as: str | None = typer.Option(None, "--origin-as")):
    with TestClient(fastapi_app) as client:
        r = client.post("/api/check/prefix", json={"prefix": prefix, "origin_as": origin_as})
        typer.echo(json.dumps(r.json(), indent=2, ensure_ascii=False))


@app.command("report")
def report(report_id: int, format: str = typer.Option("markdown", "--format")):
    path = f"/api/reports/{report_id}/{'html' if format == 'html' else 'markdown'}"
    with TestClient(fastapi_app) as client:
        r = client.get(path)
        typer.echo(r.text)
