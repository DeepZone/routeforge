#!/usr/bin/env python3
"""RouteForge deployment smoke/health check for release validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def fetch_json(url: str, timeout: float) -> dict:
    try:
        with urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Connection error for {url}: {exc.reason}") from exc


def check(condition: bool, message: str, failures: list[str]) -> None:
    prefix = "[OK]" if condition else "[FAIL]"
    print(f"{prefix} {message}")
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--frontend-dist", default="frontend/dist", help="Frontend build artifact directory")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--check-setup", action="store_true", help="Also validate /api/setup/required endpoint")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    failures: list[str] = []

    try:
        health = fetch_json(f"{base}/health", timeout=args.timeout)
    except RuntimeError as exc:
        check(False, str(exc), failures)
        print(f"\nDeployment check failed with {len(failures)} issue(s).")
        return 1
    check(health.get("status") == "ok", "Backend /health is reachable and status=ok", failures)

    try:
        status = fetch_json(f"{base}/api/system/status", timeout=args.timeout)
    except RuntimeError as exc:
        check(False, str(exc), failures)
        print(f"\nDeployment check failed with {len(failures)} issue(s).")
        return 1
    check(status.get("status") == "ok", "System status endpoint reachable", failures)
    check(bool(status.get("version")), "System status contains version", failures)
    check(status.get("read_only") is True, "System status read_only=true", failures)

    database = status.get("database") if isinstance(status, dict) else None
    check(isinstance(database, dict), "System status contains database payload", failures)
    if isinstance(database, dict):
        check(bool(database.get("status")), "Database status is present", failures)
        check(bool(database.get("schema_version")), "Database schema_version is present", failures)
        check(bool(database.get("migration_head")), "Database migration_head is present", failures)
        check(database.get("migration_status") != "behind", "Migration status is not behind", failures)

    dist = Path(args.frontend_dist)
    check(dist.exists(), f"Frontend artifacts directory exists ({dist})", failures)
    check((dist / "index.html").exists(), f"Frontend build artifact exists ({dist / 'index.html'})", failures)

    if args.check_setup:
        try:
            setup = fetch_json(f"{base}/api/setup/required", timeout=args.timeout)
            check("required" in setup, "Setup endpoint reachable and contains required field", failures)
        except RuntimeError as exc:
            check(False, str(exc), failures)

    if failures:
        print(f"\nDeployment check failed with {len(failures)} issue(s).")
        return 1
    print("\nDeployment check completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
