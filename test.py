#!/usr/bin/env python3
"""
test.py (batch mode)
Scan out/ for all *_embedded.docx, extract HoneyUUID + BeaconURL,
optionally hit the beacon URL, and log results into honeypot.db.
Usage:
    python test.py            # runs HTTP checks
    python test.py --no-http  # only read metadata and log UNKNOWN status
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

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS test_logs
                 (uuid TEXT, beacon_url TEXT, status TEXT, time TEXT, filename TEXT)''')
    conn.commit()
    conn.close()

def find_embedded_docs():
    if not OUT_DIR.exists():
        return []
    return sorted(OUT_DIR.glob(PATTERN), key=lambda p: p.stat().st_mtime)

def extract_docx_metadata(doc_path):
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
    c.execute("INSERT INTO test_logs VALUES (?, ?, ?, ?, ?)", (uuid, beacon_url, status, now, filename))
    conn.commit()
    conn.close()

def main(no_http: bool):
    print("HONEYDOC BATCH TEST START")
    init_db()
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

        log_result(uuid or "UNKNOWN", beacon or "NONE", status, doc.name)
        print("    Logged.\n")

    print("BATCH TEST COMPLETE.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch test embedded honeydocs")
    parser.add_argument("--no-http", action="store_true", help="Do not perform HTTP GET on beacon URLs")
    args = parser.parse_args()
    main(no_http=args.no_http)