# beacon.py
from urllib.parse import urlencode
from typing import Dict
import datetime
import uuid as uuid_lib

DEFAULT_DOMAIN = "https://fyp-backend-98o5.onrender.com/api/beacon"

def build_beacon_url(uuid: str, domain: str = DEFAULT_DOMAIN, path: str = "", extra: Dict = None) -> str:
    q = {"resource_id": uuid}
    # Add a random nonce to prevent caching and allow multiple triggers if needed
    q["nonce"] = str(uuid_lib.uuid4())[:8]
    if extra:
        q.update(extra)
    return f"{domain}{path}?{urlencode(q)}"

# TODO: Implement conditional triggering for beacons to reduce detection risk.
# Future enhancement: Add logic to trigger beacons only under specific conditions,
# e.g., after multiple document opens, from non-whitelisted IPs, or based on time delays.
# This could involve checking access patterns or embedding conditional metadata.
# Example: def should_trigger_beacon(uuid: str, access_count: int, ip: str) -> bool:
#     return access_count > 1 or ip not in WHITELIST
