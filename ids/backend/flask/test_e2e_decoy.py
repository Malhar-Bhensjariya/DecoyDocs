#!/usr/bin/env python3
"""
E2E acceptance test (authenticated):
- Logs into the frontend as admin (Selenium)
- Creates a DecoyDoc via the UI
- Starts the Node attack-bot to simulate robotic mouse events as a regular user
- Asserts an IDS alert is created for the attacking user in MongoDB (via API)

Run this with the dev servers running (frontend on :5175, Node API on :3001).
"""
import time
import json
import subprocess
import requests
import sys
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FRONTEND = os.environ.get('FRONTEND_URL', 'http://localhost:5175')
API_BASE = os.environ.get('API_BASE', 'http://localhost:3001')
ADMIN_USER = os.environ.get('E2E_ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('E2E_ADMIN_PASS', 'admin123')
ATTACK_BOT_PATH = Path('ids/backend/node/bot/attack-bot.js')


def setup_headless_chrome():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1600,900')
    # Use a common user-agent to ensure frontend behaves normally
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Could not start Chrome WebDriver: {e}")
        return None


def login_via_ui(driver, username, password):
    login_url = f"{FRONTEND}/login"
    driver.get(login_url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
    driver.find_element(By.ID, 'username').clear()
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').clear()
    driver.find_element(By.ID, 'password').send_keys(password)

    # Submit the form
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Wait for redirect to dashboard
    WebDriverWait(driver, 15).until(EC.url_contains('/dashboard'))

    # Extract token from localStorage for API requests
    token = driver.execute_script("return localStorage.getItem('token');")
    return token


def create_decoy_via_ui(driver, title):
    driver.get(f"{FRONTEND}/decoydocs")

    # Open create form
    create_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Document')]"))
    )
    create_btn.click()

    # Wait for title input and submit
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'title')))
    driver.find_element(By.ID, 'title').send_keys(title)

    # Submit the create form (button[type=submit] inside page)
    submit_btn = driver.find_element(By.CSS_SELECTOR, "form button[type='submit']")
    submit_btn.click()

    # Wait for the new document to appear in the list
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, f"//p[text()='{title}']"))
    )


def run_attack_bot_and_wait(timeout=45):
    if not ATTACK_BOT_PATH.exists():
        raise FileNotFoundError(f"Attack bot not found at {ATTACK_BOT_PATH}")

    proc = subprocess.Popen([
        'node',
        str(ATTACK_BOT_PATH)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        print('--- attack-bot stdout ---')
        print(stdout)
        print('--- attack-bot stderr ---')
        print(stderr)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print('Attack bot timed out; killed process')
        print(stdout)
        print(stderr)
        raise


def poll_alerts(admin_token, username='user', timeout=30):
    headers = {'Authorization': f'Bearer {admin_token}'}
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{API_BASE}/api/ids/alerts", headers=headers, timeout=5)
            if r.status_code == 200:
                alerts = r.json()
                for a in alerts:
                    if a.get('username') == username:
                        return a
        except Exception:
            pass
        time.sleep(1)
    return None


def main():
    title = f"E2E Test Doc {int(time.time())}"

    driver = setup_headless_chrome()
    if driver is None:
        print('Selenium Chrome driver not available — aborting E2E test')
        sys.exit(1)

    try:
        print('Logging in as admin via UI...')
        admin_token = login_via_ui(driver, ADMIN_USER, ADMIN_PASS)
        if not admin_token:
            print('Failed to obtain admin token from frontend localStorage')
            sys.exit(1)
        print('Admin token obtained')

        print('Creating DecoyDoc via UI...')
        create_decoy_via_ui(driver, title)
        print('DecoyDoc created (UI reported success)')

        # Ensure decoy exists via API
        headers = {'Authorization': f'Bearer {admin_token}'}
        r = requests.get(f"{API_BASE}/api/decoydocs", headers=headers, timeout=10)
        assert r.status_code == 200, f"Decoy list API returned {r.status_code}"
        docs = r.json()
        matching = [d for d in docs if d.get('title') == title]
        if not matching:
            print('Created decoy not visible via API — continuing but test may be flaky')
        else:
            decoy_id = matching[0]['id']
            print(f'Found decoy id: {decoy_id}')

        print('Starting attack-bot to trigger IDS heuristic...')
        run_attack_bot_and_wait(timeout=50)

        print('Polling IDS alerts for attacker "user"...')
        alert = poll_alerts(admin_token, username='user', timeout=30)
        if alert:
            print('✅ IDS alert detected for attacker user:')
            print(json.dumps(alert, indent=2))
            print('\nE2E acceptance test: PASS')
            sys.exit(0)
        else:
            print('❌ No IDS alert detected for attacker user within timeout')
            sys.exit(2)

    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == '__main__':
    main()
