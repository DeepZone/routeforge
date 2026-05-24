from pathlib import Path


def _parse_env_keys(path: Path) -> list[str]:
    keys: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _ = line.split("=", 1)
        keys.append(key.strip())
    return keys


def test_env_example_has_no_duplicate_keys() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env.example"
    keys = _parse_env_keys(env_path)
    duplicates = sorted({key for key in keys if keys.count(key) > 1})
    assert duplicates == []


def test_markdown_report_template_uses_english_headings() -> None:
    template = (Path(__file__).resolve().parents[1] / "app" / "templates" / "report.md.j2").read_text(encoding="utf-8")
    assert "## Input" in template
    assert "## Overall Assessment" in template
    assert "## Raw Data" in template
    assert "## Technical Details" in template


def test_html_report_template_uses_english_headings() -> None:
    template = (Path(__file__).resolve().parents[1] / "app" / "templates" / "report.html.j2").read_text(encoding="utf-8")
    assert "<h2>Input</h2>" in template
    assert "<h2>Overall Assessment</h2>" in template
    assert "<h2>Raw Data</h2>" in template
    assert "<h2>Technical Details</h2>" in template
