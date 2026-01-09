#!/usr/bin/env python3
"""
test_simulation.py
Simulates real-world document access by triggering embedded beacon endpoints.
Tests visible links, steganographic images, and hidden regions.
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import List, Dict

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from embedder.metadata import read_docx_custom_property

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OUT_DIR = Path("out")
SIMULATION_LOG = "simulation_log.json"
BEACON_BASE = "https://fyp-backend-98o5.onrender.com"

def setup_headless_browser():
    """Set up Selenium with headless Chrome for simulating document opens."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {e}")
        logger.warning("Continuing without browser-based simulation (will use direct HTTP requests)")
        return None

def fire_beacon(url: str, timeout: int = 5) -> Dict:
    """Fire a beacon request and log results."""
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=False)
        return {
            "success": True,
            "status": response.status_code,
            "url": url,
            "timestamp": time.time(),
            "body": response.text[:200]
        }
    except requests.exceptions.Timeout:
        logger.warning(f"Beacon request timeout: {url}")
        return {
            "success": False,
            "error": "timeout",
            "url": url,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.warning(f"Beacon request failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "timestamp": time.time()
        }

def fire_manifest_beacons(manifest_path: Path) -> List[Dict]:
    """Read manifest and fire all beacons from it."""
    results = []
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        logger.error(f"Could not read manifest {manifest_path}: {e}")
        return results

    uuid = manifest.get("title", "unknown")
    beacon_urls = manifest.get("beacon_urls", {})
    
    if not beacon_urls:
        logger.warning(f"No beacon_urls in manifest {manifest_path}")
        return results

    logger.info(f"📡 Firing {len(beacon_urls)} beacon(s) for {uuid}")
    
    for endpoint_name, url in beacon_urls.items():
        if url:
            result = fire_beacon(url)
            result["endpoint"] = endpoint_name
            results.append(result)
            if result["success"]:
                logger.info(f"  ✅ {endpoint_name}: status={result['status']}")
            else:
                logger.warning(f"  ⚠️  {endpoint_name}: {result.get('error')}")
    
    return results

def simulate_pdf_with_browser(driver, pdf_path: Path) -> List[Dict]:
    """Simulate PDF opening in browser (loads embedded resources)."""
    if driver is None:
        logger.info(f"⏭️  Skipping browser simulation for {pdf_path.name}")
        return []
    
    results = []
    file_url = f"file://{pdf_path.resolve()}"
    logger.info(f"🌐 Opening PDF in browser: {pdf_path.name}")
    
    try:
        driver.get(file_url)
        
        # Wait for body to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Allow time for embedded resources and beacons to load
        time.sleep(3)
        
        logger.info(f"✅ PDF loaded successfully: {pdf_path.name}")
        
        # Try to trigger any visible links by executing JavaScript
        try:
            driver.execute_script("""
                const links = document.querySelectorAll('a[onclick]');
                links.forEach(link => {
                    console.log('Found clickable link');
                });
            """)
        except Exception as e:
            logger.debug(f"Could not check links: {e}")
            
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
    
    return results

def simulate_docx_metadata(docx_path: Path) -> List[Dict]:
    """Extract and fire beacon from DOCX metadata."""
    results = []
    logger.info(f"📦 Reading DOCX metadata: {docx_path.name}")
    
    try:
        uuid = read_docx_custom_property(str(docx_path), "HoneyUUID")
        beacon = read_docx_custom_property(str(docx_path), "BeaconURL")
        
        logger.info(f"  UUID: {uuid}")
        logger.info(f"  BeaconURL: {beacon}")
        
        if beacon:
            result = fire_beacon(beacon)
            result["file"] = str(docx_path)
            result["type"] = "docx_metadata"
            results.append(result)
            if result["success"]:
                logger.info(f"  ✅ DOCX beacon fired: {result['status']}")
    except Exception as e:
        logger.warning(f"Error reading DOCX: {e}")
    
    return results

def run_simulation():
    """Run simulation on all documents in out/ subfolders."""
    driver = None
    try:
        driver = setup_headless_browser()
    except Exception as e:
        logger.warning(f"Browser setup failed, will use HTTP requests only: {e}")
    
    log_entries = []
    documents_processed = 0
    beacons_fired = 0

    try:
        if not OUT_DIR.exists():
            logger.error(f"Output directory not found: {OUT_DIR}")
            return

        # Find all subfolders in out/
        subfolders = list(OUT_DIR.iterdir())
        if not subfolders:
            logger.warning(f"No subfolders found in {OUT_DIR}")
            return

        for folder in subfolders:
            if not folder.is_dir():
                continue
            
            logger.info(f"\n📁 Processing folder: {folder.name}")
            
            # Fire beacons from manifest files
            for manifest in folder.glob("*.manifest.json"):
                manifest_results = fire_manifest_beacons(manifest)
                log_entries.extend(manifest_results)
                beacons_fired += len([r for r in manifest_results if r.get("success")])

            # Process PDF files
            for pdf_file in folder.glob("*.pdf"):
                documents_processed += 1
                logger.info(f"  📄 Processing PDF: {pdf_file.name}")
                
                # Try browser-based simulation if available
                if driver:
                    try:
                        browser_results = simulate_pdf_with_browser(driver, pdf_file)
                        log_entries.extend(browser_results)
                        beacons_fired += len([r for r in browser_results if r.get("success")])
                    except Exception as e:
                        logger.error(f"Browser simulation failed: {e}")

            # Process DOCX files
            for docx_file in folder.glob("*.docx"):
                documents_processed += 1
                logger.info(f"  📦 Processing DOCX: {docx_file.name}")
                
                docx_results = simulate_docx_metadata(docx_file)
                log_entries.extend(docx_results)
                beacons_fired += len([r for r in docx_results if r.get("success")])

        # Save simulation log
        with open(SIMULATION_LOG, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=2)
        
        logger.info(f"\n📋 Simulation log saved to {SIMULATION_LOG}")
        logger.info(f"📊 Summary:")
        logger.info(f"   Documents processed: {documents_processed}")
        logger.info(f"   Beacons fired: {beacons_fired}")
        logger.info(f"   Log entries: {len(log_entries)}")

    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")

    logger.info("\n🎯 Simulation complete! Check server logs for beacon hits and alerts.")

if __name__ == "__main__":
    run_simulation()

if __name__ == "__main__":
    if not OUT_DIR.exists():
        print("No out/ directory found. Run pipeline.py first.")
        exit(1)
    run_simulation()