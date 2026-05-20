from pathlib import Path
import os
import sqlite3
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, env):
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, check=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "upgrade-check.db"
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite:///{db_path}"

        run(["alembic", "upgrade", "head"], env)
        current = run(["alembic", "current"], env).stdout
        heads = run(["alembic", "heads"], env).stdout
        assert "000" in current and "000" in heads

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("UPDATE alembic_version SET version_num = ?", ("0001_initial_schema",))
        conn.commit(); conn.close()

        current2 = run(["alembic", "current"], env).stdout
        if "0001_initial_schema" not in current2:
            raise SystemExit("Failed to simulate behind revision")

        print("Upgrade checks passed")


if __name__ == "__main__":
    main()
