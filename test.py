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
                 (uuid TEXT, beacon_url TEXT, status TEXT, country TEXT, city TEXT, time TEXT)''')
    conn.commit()
    conn.close()

# --- Read metadata from DOCX ---
def extract_docx_metadata(doc_path):
    honey_uuid = read_docx_custom_property(doc_path, "HoneyUUID")
    beacon_url = read_docx_custom_property(doc_path, "BeaconURL")
    print(f"Extracted Metadata:")
    print(f"  HoneyUUID  → {honey_uuid}")
    print(f"  BeaconURL  → {beacon_url}")
    return honey_uuid, beacon_url

# --- Optional: Simulate beacon hit ---
def trigger_beacon(url):
    try:
        print(f"\nPinging beacon URL: {url}")
        r = requests.get(url, timeout=5)
        status = f"{r.status_code} {r.reason}"
        ip = r.raw._connection.sock.getpeername()[0] if hasattr(r.raw, "_connection") else None
    except Exception as e:
        status = f"Error: {e}"
        ip = None
    return status, ip

# --- Geo-IP lookup helper ---
def geo_lookup(ip):
    if not ip:
        return "", ""
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return r.get("country", ""), r.get("city", "")
    except Exception:
        return "", ""

# --- Save result to DB ---
def log_result(uuid, beacon_url, status, country, city):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO test_logs VALUES (?, ?, ?, ?, ?, ?)",
              (uuid, beacon_url, status, country, city, now))
    conn.commit()
    conn.close()

# --- Main test flow ---
if __name__ == "__main__":
    print("=== HoneyDoc Test Utility ===\n")
    init_db()
    uuid, beacon = extract_docx_metadata(DOC_PATH)
    
    if not beacon:
        print("No BeaconURL found in DOCX. Exiting.")
    else:
        print("\nTriggering beacon (simulated document open)...")
        status, ip = trigger_beacon(beacon)
        country, city = geo_lookup(ip)
        print(f"Response: {status}")
        print(f"Resolved IP: {ip or 'Unknown'}")
        print(f"Location: {country or 'N/A'}, {city or 'N/A'}")

        log_result(uuid, beacon, status, country, city)
        print("\n--- Logged beacon test successfully. ---")
