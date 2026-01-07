#!/usr/bin/env python3
"""
test_simulation.py
Simulates real-world document access by attackers to test honeytoken triggers.
Uses headless browser to "open" PDFs/DOCX files, allowing embedded beacons to fire naturally.
This mimics sabotage/exfiltration without manual opening.
"""

import os
import time
import json
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from embedder.metadata import read_docx_custom_property

# Configuration
OUT_DIR = Path("out")
SIMULATION_LOG = "simulation_log.json"
BEACON_BASE = "https://fyp-backend-98o5.onrender.com/api/beacon"

def setup_headless_browser():
    """Set up Selenium with headless Chrome for simulating document opens."""
    options = Options()
    options.add_argument("--headless")  # Run without UI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Add user-agent to mimic real access
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=options)

def simulate_open_pdf(driver, pdf_path: Path):
    """Simulate opening a PDF by loading it in browser, allowing image/beacon fetches.

    NOTE: Our current PDFs (built via wkhtmltopdf) embed the beacon as an <img src="BEACON_URL" ...>,
    so simply loading the PDF file may or may not execute that HTML depending on the viewer.
    To remove ambiguity, we also parse and fire the beacon explicitly via HTTP (see below).
    """
    file_url = f"file://{pdf_path.resolve()}"
    print(f"Simulating PDF open: {pdf_path.name}")
    driver.get(file_url)

    # Wait for page to load and images to fetch (beacons fire here)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)  # Allow time for beacon requests
        print(f"✅ Simulated open complete for {pdf_path.name}")
    except Exception as e:
        print(f"⚠️  Simulation issue for {pdf_path.name}: {e}")

def simulate_open_docx(driver, docx_path: Path):
    """Simulate 'opening' DOCX by verifying embedded metadata and explicitly firing beacon.

    DOCX core properties are not active content, so they won't auto-call the beacon on open.
    For end-to-end testing we read the UUID/BeaconURL and hit the beacon API directly.
    """
    print(f"Simulating DOCX access: {docx_path.name}")
    uuid = read_docx_custom_property(str(docx_path), "HoneyUUID")
    beacon = read_docx_custom_property(str(docx_path), "BeaconURL")

    print(f"  Extracted UUID: {uuid}")
    print(f"  Extracted Beacon URL: {beacon}")

    if beacon:
        try:
            r = requests.get(beacon, timeout=5)
            print(f"  ▶ Beacon GET status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            print(f"  ⚠️ Error firing DOCX beacon: {e}")
    else:
        print("  ⚠️ No BeaconURL metadata found on DOCX.")


def fire_explicit_beacon_from_summary(summary_path: Path):
    """Read summary_*.json and explicitly call the beacon for that UUID.

    This isolates 'does the backend log /api/beacon hits?' from any viewer behavior.
    """
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ⚠️ Could not read summary {summary_path}: {e}")
        return

    uuid = data.get("uuid")
    if not uuid:
        print(f"  ⚠️ No uuid in summary {summary_path}")
        return

    beacon_url = f"{BEACON_BASE}?resource_id={uuid}&nonce=testsim"
    print(f"  Firing explicit beacon for UUID={uuid} -> {beacon_url}")
    try:
        r = requests.get(beacon_url, timeout=5)
        print(f"  ▶ Explicit beacon status={r.status_code}, body={r.text[:200]}")
    except Exception as e:
        print(f"  ⚠️ Error firing explicit beacon: {e}")

def run_simulation():
    """Run simulation on all honeytokens in out/ subfolders."""
    driver = setup_headless_browser()
    log_entries = []

    try:
        # Find all subfolders in out/
        for folder in OUT_DIR.iterdir():
            if folder.is_dir():
                print(f"\n📁 Simulating access in folder: {folder.name}")
                # Fire one explicit beacon based on summary JSON (if present)
                for summary in folder.glob("summary_*.json"):
                    fire_explicit_beacon_from_summary(summary)

                for file_path in folder.glob("*"):
                    if file_path.suffix == ".pdf":
                        simulate_open_pdf(driver, file_path)
                        log_entries.append({
                            "file": str(file_path),
                            "type": "pdf",
                            "simulated_at": time.time(),
                            "status": "pdf_opened"
                        })
                    elif file_path.suffix == ".docx":
                        simulate_open_docx(driver, file_path)
                        log_entries.append({
                            "file": str(file_path),
                            "type": "docx",
                            "simulated_at": time.time(),
                            "status": "metadata_checked"
                        })

        # Save log
        with open(SIMULATION_LOG, "w") as f:
            json.dump(log_entries, f, indent=2)
        print(f"\n📋 Simulation log saved to {SIMULATION_LOG}")

    finally:
        driver.quit()

    print("\n🎯 Simulation complete. Check server logs for beacon hits and alerts!")

if __name__ == "__main__":
    if not OUT_DIR.exists():
        print("❌ No out/ directory found. Run pipeline.py first.")
        exit(1)
    run_simulation()