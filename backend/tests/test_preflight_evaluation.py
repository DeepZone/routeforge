from app.core.preflight_evaluation import evaluate_preflight


def _c(status: str, raw: dict | None = None) -> dict:
    return {"status": status, "raw": raw or {}}


def test_all_ok() -> None:
    result = evaluate_preflight(_c("OK"), _c("OK"), _c("OK", {"visible_origins": ["AS64500"]}), "203.0.113.0/24", "AS64500")
    assert result["status"] == "OK"


def test_rpki_critical() -> None:
    assert evaluate_preflight(_c("CRITICAL"), _c("OK"), _c("OK"), "p", "AS1")["status"] == "CRITICAL"


def test_registry_critical() -> None:
    assert evaluate_preflight(_c("OK"), _c("CRITICAL"), _c("OK"), "p", "AS1")["status"] == "CRITICAL"


def test_routing_critical() -> None:
    assert evaluate_preflight(_c("OK"), _c("OK"), _c("CRITICAL"), "p", "AS1")["status"] == "CRITICAL"


def test_routing_unknown_others_ok_warn() -> None:
    assert evaluate_preflight(_c("OK"), _c("OK"), _c("UNKNOWN"), "p", "AS1")["status"] == "WARNING"


def test_all_unknown() -> None:
    assert evaluate_preflight(_c("UNKNOWN"), _c("UNKNOWN"), _c("UNKNOWN"), "p", "AS1")["status"] == "UNKNOWN"


def test_warning_from_one_check() -> None:
    assert evaluate_preflight(_c("WARNING"), _c("OK"), _c("OK"), "p", "AS1")["status"] == "WARNING"
