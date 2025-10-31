import sqlite3
from datetime import datetime, timezone
from embedder.metadata import read_docx_custom_property
import requests
from pathlib import Path

DB_PATH = "honeypot.db"
DOC_PATH = "out/Corporate_Strategy_and_Growth_Report_-_Q1_2026_e19b1de3_embedded.docx"

def init_db():
    """Ensure test_logs table exists for recording beacon test results."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS test_logs
                 (uuid TEXT, beacon_url TEXT, status TEXT, time TEXT)''')
    conn.commit()
    conn.close()
    print("[1/4] Database initialized or verified.")

def extract_docx_metadata(doc_path):
    """Read embedded properties from a DOCX file."""
    print(f"[2/4] Reading metadata from DOCX: {doc_path}")
    honey_uuid = read_docx_custom_property(doc_path, "HoneyUUID")
    beacon_url = read_docx_custom_property(doc_path, "BeaconURL")

    if not honey_uuid:
        print("   -> No HoneyUUID property found.")
    else:
        print(f"   -> HoneyUUID detected: {honey_uuid}")

    if not beacon_url:
        print("   -> No BeaconURL property found.")
    else:
        print(f"   -> BeaconURL detected: {beacon_url}")

    return honey_uuid, beacon_url

def trigger_beacon(url):
    """Attempt to simulate beacon trigger by requesting the embedded URL."""
    print(f"[3/4] Simulating beacon trigger...\n    Target: {url}")
    try:
        r = requests.get(url, timeout=5)
        status = f"{r.status_code} {r.reason}"
        print(f"   -> Beacon responded with: {status}")
    except Exception as e:
        status = f"Error: {e}"
        print(f"   -> Beacon trigger failed: {e}")
    return status

def log_result(uuid, beacon_url, status):
    """Record test results in local honeypot DB."""
    print(f"[4/4] Logging result to database...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute("INSERT INTO test_logs VALUES (?, ?, ?, ?)", (uuid, beacon_url, status, now))
    conn.commit()
    conn.close()
    print(f"   -> Log entry created for UUID {uuid} at {now}")

if __name__ == "__main__":
    print("=== HONEYDOC TEST START ===")
    init_db()

    if not Path(DOC_PATH).exists():
        print(f"ERROR: DOCX not found at {DOC_PATH}")
        exit(1)

    uuid, beacon = extract_docx_metadata(DOC_PATH)
    if not beacon:
        print("No beacon URL available — cannot test trigger.")
        exit(0)

    status = trigger_beacon(beacon)
    log_result(uuid, beacon, status)

    print("\n=== TEST COMPLETE ===")
    print(f"Tested UUID: {uuid}")
    print(f"Beacon URL: {beacon}")
    print(f"Result: {status}\n")
