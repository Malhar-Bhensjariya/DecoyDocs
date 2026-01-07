# beacon.py
from urllib.parse import urlencode
from typing import Dict
import datetime
import os
import uuid as uuid_lib

# Use environment variable to switch between test and production
# Set API_BASE_URL=http://localhost:5000 for test server
# Or leave unset/default for production
API_BASE_URL = os.environ.get("API_BASE_URL", "https://fyp-backend-98o5.onrender.com")
DEFAULT_DOMAIN = f"{API_BASE_URL}/api/beacon"

def build_beacon_url(uuid: str, domain: str = None, path: str = "", extra: Dict = None) -> str:
    if domain is None:
        domain = DEFAULT_DOMAIN
    q = {"resource_id": uuid}
    # Add a random nonce to prevent caching and allow multiple triggers if needed
    q["nonce"] = str(uuid_lib.uuid4())[:8]
    if extra:
        q.update(extra)
    return f"{domain}{path}?{urlencode(q)}"
