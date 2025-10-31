import sqlite3
from datetime import datetime
from embedder.metadata import read_docx_custom_property
import requests

DB_PATH = "honeypot.db"
DOC_PATH = "out/Corporate_Strategy_and_Growth_Report_-_Q1_2026_e19b1de3_embedded.docx"

# --- Initialize DB if not exists ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS test_logs
                 (uuid TEXT, beacon_url TEXT, status TEXT, time TEXT)''')
    conn.commit()
    conn.close()

# --- Read metadata from DOCX ---
def extract_docx_metadata(doc_path):
    honey_uuid = read_docx_custom_property(doc_path, "HoneyUUID")
    beacon_url = read_docx_custom_property(doc_path, "BeaconURL")
    print(f"HoneyUUID: {honey_uuid}")
    print(f"BeaconURL: {beacon_url}")
    return honey_uuid, beacon_url

# --- Optional: Simulate beacon hit ---
def trigger_beacon(url):
    try:
        r = requests.get(url, timeout=5)
        status = f"{r.status_code} {r.reason}"
    except Exception as e:
        status = f"Error: {e}"
    return status

# --- Save result to DB ---
def log_result(uuid, beacon_url, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO test_logs VALUES (?, ?, ?, ?)", (uuid, beacon_url, status, now))
    conn.commit()
    conn.close()

# --- Main test flow ---
if __name__ == "__main__":
    init_db()
    uuid, beacon = extract_docx_metadata(DOC_PATH)
    
    if not beacon:
        print("⚠️ No BeaconURL found in DOCX.")
    else:
        print("→ Triggering beacon (simulated open)...")
        status = trigger_beacon(beacon)
        log_result(uuid, beacon, status)
        print(f"✅ Logged beacon test: {status}")
