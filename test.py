#!/usr/bin/env python3
"""
test.py (batch)
Scan out/ for all *_embedded.docx, read HoneyUUID + BeaconURL, optionally perform HTTP GET,
log results into honeypot.db, and print a short inference instead of raw error text for demos.

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
import socket
import urllib3

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


def derive_inference_from_error(raw_status: str) -> str:
    # Accepts raw status strings (e.g., "Error: <...>", "200 OK") and returns a short inference.
    s = (raw_status or "").lower()
    if "name or service not known" in s or "failed to resolve" in s or "nodename nor servname" in s:
        return "Domain unresolved — beacon host is placeholder or DNS blocked."
    if "connection refused" in s or "connectionreseterror" in s:
        return "Connection refused — listener not running or port blocked by firewall."
    if "timed out" in s or "timeout" in s or "max retries exceeded" in s:
        return "Timeout — network blocked, no route, or listener too slow to respond."
    if "ssl" in s or "certificate" in s or "tls" in s:
        return "TLS/SSL problem — certificate issue or interception by proxy."
    # HTTP status codes
    if s.startswith("200") or "200 ok" in s:
        return "Success — external resource fetched (beacon reached)."
    if s.startswith("204") or "204 " in s:
        return "Success (no content) — beacon endpoint acknowledged the request."
    if s.startswith("3"):
        return "Redirect — request was redirected (CDN or proxy)."
    if s.startswith("4"):
        return "Client error — resource reachable but access denied or invalid request."
    if s.startswith("5"):
        return "Server error — beacon reachable but server failed to handle request."
    return "Unknown network outcome — check raw status or logs."


def trigger_beacon(url, timeout=6):
    try:
        # run a real request and return HTTP status text
        r = requests.get(url, timeout=timeout)
        raw = f"{r.status_code} {r.reason}"
        return raw
    except requests.exceptions.SSLError as e:
        return f"Error: SSL error: {e}"
    except requests.exceptions.ConnectTimeout as e:
        return f"Error: Timeout: {e}"
    except requests.exceptions.ReadTimeout as e:
        return f"Error: Read timeout: {e}"
    except requests.exceptions.ConnectionError as e:
        # ConnectionError wraps several lower-level socket errors; include message
        return f"Error: Connection error: {e}"
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
            inference = "No beacon URL present in document."
            print(f"    {inference}")
        elif no_http:
            status = "SKIPPED_HTTP"
            inference = "HTTP test skipped by flag."
            print(f"    {inference}")
        else:
            print("    Triggering beacon (HTTP GET)...")
            raw_status = trigger_beacon(beacon)
            inference = derive_inference_from_error(raw_status)
            print(f"    Result: {raw_status}")
            print(f"    Inference: {inference}")
            status = raw_status

        log_result(uuid, beacon, status, doc.name)
        print("    Logged.\n")

    print("BATCH TEST COMPLETE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch test embedded honeydocs")
    parser.add_argument("--no-http", action="store_true", help="Do not perform HTTP GET on beacon URLs")
    args = parser.parse_args()
    main(no_http=args.no_http)
