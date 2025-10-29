# uuid_manager.py
from typing import Dict
import sqlite3
from datetime import datetime
from .utils import ensure_dir

DB_PATH = "embedder_uuid.db"

def init_db(db_path: str = DB_PATH):
    ensure_dir(".")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS uuids (
        uuid TEXT PRIMARY KEY,
        label TEXT,
        template TEXT,
        created_at TEXT,
        status TEXT,
        manifest_path TEXT
    )""")
    conn.commit()
    conn.close()

def reserve_uuid(u: str, label: str = "", template: str = "", db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO uuids (uuid,label,template,created_at,status) VALUES (?,?,?,?,?)",
              (u, label, template, datetime.utcnow().isoformat(), "reserved"))
    conn.commit()
    conn.close()

def mark_deployed(u: str, manifest_path: str, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE uuids SET status=?, manifest_path=? WHERE uuid=?", ("deployed", manifest_path, u))
    conn.commit()
    conn.close()

def lookup(u: str, db_path: str = DB_PATH) -> Dict:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT uuid,label,template,created_at,status,manifest_path FROM uuids WHERE uuid=?", (u,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {}
    keys = ["uuid","label","template","created_at","status","manifest_path"]
    return dict(zip(keys, row))
