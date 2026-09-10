import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = Path("/tmp/trafficvision.db") if os.environ.get("VERCEL") else BASE_DIR / "database" / "trafficvision.db"


def _ensure_schema(conn):
    schema_path = BASE_DIR / "database" / "schema.sql"
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()


def get_connection():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE))

    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)

    return conn