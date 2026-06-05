#!/usr/bin/env python3
"""
test_signal.py
Test sending a signal to the dashboard API
"""

import requests
import json
from datetime import datetime

DASHBOARD_API = "https://fyp-backend-98o5.onrender.com/api/signals/"

def test_signal():
    payload = {
        "bot_type": "scanner",
        "attack_vector": "document_download",
        "source_ip": "192.168.1.155",
        "target_resource": "1234-test-uuid",
        "target_endpoint": "/api/beacon",
        "success": False,
        "timestamp": "2026-04-17T21:00:00Z",
        "details": {
            "user_agent": "Mozilla/5.0 (compatible; BotScanner/1.0)",
            "behavior_indicators": ["automation_flags", "rapid_requests"],
            "request_headers": {"X-Scanner": "true"},
            "custom_metadata": {"tool": "ZAP"}
        }
    }

    print(f"Sending test signal to {DASHBOARD_API}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(DASHBOARD_API, json=payload, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signal()