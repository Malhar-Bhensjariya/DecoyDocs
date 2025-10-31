#!/usr/bin/env python3
"""
test.py — refined clean output mode
Scans for *_embedded.docx in /out, reads HoneyUUID & BeaconURL, tests beacon reachability,
and prints concise inferences (no raw error noise).
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_logs';")
    if not c.fetchone():
        c.execute(
            "CREATE TABLE test_logs (uuid TEXT, beacon_url TEXT, status TEXT, time TEXT, filename TEXT)"
        )
        conn.commit()
        conn.close()
        return
    c.execute("PRAGMA table_info(test_logs);")
    cols = [row[1] for row in c.fetchall()]
    if cols != EXPECTED_COLUMNS:
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


def derive_inference_from_error(raw_status: str) -> str:
    s = (raw_status or "").lower()
    if "failed to resolve" in s or "name or service not known" in s:
        return "Domain unresolved — beacon host is placeholder or DNS blocked."
    if "connection refused" in s:
        return "Connection refused — listener not active or firewall blocked."
    if "timed out" in s or "timeout" in s:
        return "Timeout — network unreachable or host not responding."
    if "ssl" in s or "certificate" in s:
        return "TLS/SSL issue — certificate mismatch or proxy interception."
    if s.startswith("200") or "200 ok" in s:
        return "Success — external beacon successfully fetched."
    if s.startswith("204") or "204 " in s:
        return "Success (no content) — silent beacon acknowledgment."
    if s.startswith("3"):
        return "Redirect — request rerouted via CDN or proxy."
    if s.startswith("4"):
        return "Client error — endpoint reachable but denied or malformed."
    if s.startswith("5"):
        return "Server error — remote beacon server failed."
    return "Unknown network outcome — check detailed logs."


def trigger_beacon(url, timeout=6):
    try:
        r = requests.get(url, timeout=timeout)
        return f"{r.status_code} {r.reason}"
    except Exception as e:
        # Return short tag instead of raw traceback
        return f"Error: {type(e).__name__}"


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

        if not beacon:
            inference = "No beacon URL present in document."
            status = "NO_BEACON"
        elif no_http:
            inference = "HTTP test skipped (flag)."
            status = "SKIPPED_HTTP"
        else:
            status = trigger_beacon(beacon)
            inference = derive_inference_from_error(status)

        print(f"    Inference: {inference}")
        log_result(uuid, beacon, status, doc.name)
        print("    Logged.\n")

    print("BATCH TEST COMPLETE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch test embedded honeydocs")
    parser.add_argument("--no-http", action="store_true", help="Skip actual HTTP requests")
    args = parser.parse_args()
    main(no_http=args.no_http)
