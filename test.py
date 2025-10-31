#!/usr/bin/env python3
"""
test.py (batch)
Scan out/ for all *_embedded.docx, read HoneyUUID + BeaconURL, optionally perform HTTP GET,
and log results into honeypot.db. If the existing test_logs table has a mismatched schema,
it will be recreated to the expected schema (5 columns).

Usage:
    python test.py            # runs HTTP checks
    python test.py --no-http  # only read metadata and log SKIPPED_HTTP
"""

import sqlite3
from datetime import datetime, timezone
from embedder.metadata import read_docx_custom_property
import requests
from pathlib import Path
import sys
import argparse

DB_PATH = "honeypot.db"
OUT_DIR = Path("out")
PATTERN = "*_embedded.docx"
EXPECTED_COLUMNS = ["uuid", "beacon_url", "status", "time", "filename"]


def ensure_table_schema():
    """Ensure test_logs table exists with the expected 5-column schema.
    If an older/invalid schema exists, drop & recreate the table.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # If table doesn't exist, create it
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_logs';")
    if not c.fetchone():
        c.execute(
            "CREATE TABLE test_logs (uuid TEXT, beacon_url TEXT, status TEXT, time TEXT, filename TEXT)"
        )
        conn.commit()
        conn.close()
        return

    # If table exists, verify columns
    c.execute("PRAGMA table_info(test_logs);")
    cols = [row[1] for row in c.fetchall()]  # second field is name
    if cols != EXPECTED_COLUMNS:
        # Recreate table with expected schema
        print("Existing test_logs schema mismatch. Recreating table with the expected schema.")
        c.execute("DROP TABLE IF EXISTS test_logs;")
        c.execute(
            "CREATE TABLE test_logs (uuid TEXT, beacon_url TEXT, status TEXT, time TEXT, filename TEXT)"
        )
        conn.commit()

    conn.close()


def find_embedded_docs():
    if not OUT_DIR.exists():
        return []
    return sorted(OUT_DIR.glob(PATTERN), key=lambda p: p.stat().st_mtime)


def extract_docx_metadata(doc_path: Path):
    uuid = read_docx_custom_property(str(doc_path), "HoneyUUID")
    beacon = read_docx_custom_property(str(doc_path), "BeaconURL")
    return uuid, beacon


def trigger_beacon(url, timeout=6):
    try:
        r = requests.get(url, timeout=timeout)
        return f"{r.status_code} {r.reason}"
    except Exception as e:
        return f"Error: {e}"


def log_result(uuid, beacon_url, status, filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute(
        "INSERT INTO test_logs VALUES (?, ?, ?, ?, ?)",
        (uuid or "UNKNOWN", beacon_url or "NONE", status, now, filename),
    )
    conn.commit()
    conn.close()


def main(no_http: bool):
    print("HONEYDOC BATCH TEST START")
    ensure_table_schema()

    docs = find_embedded_docs()
    if not docs:
        print(f"No embedded docs found in {OUT_DIR.resolve()} matching '{PATTERN}'.")
        sys.exit(0)

    print(f"Found {len(docs)} embedded doc(s). Processing in chronological order.\n")

    for i, doc in enumerate(docs, start=1):
        print(f"[{i}/{len(docs)}] File: {doc.name}")
        uuid, beacon = extract_docx_metadata(doc)
        print(f"    HoneyUUID: {uuid or 'MISSING'}")
        print(f"    BeaconURL: {beacon or 'MISSING'}")

        if not beacon:
            status = "NO_BEACON"
            print("    No beacon URL — skipping HTTP test.")
        elif no_http:
            status = "SKIPPED_HTTP"
            print("    HTTP test skipped by flag.")
        else:
            print("    Triggering beacon (HTTP GET)...")
            status = trigger_beacon(beacon)
            print(f"    Result: {status}")

        log_result(uuid, beacon, status, doc.name)
        print("    Logged.\n")

    print("BATCH TEST COMPLETE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch test embedded honeydocs")
    parser.add_argument("--no-http", action="store_true", help="Do not perform HTTP GET on beacon URLs")
    args = parser.parse_args()
    main(no_http=args.no_http)
