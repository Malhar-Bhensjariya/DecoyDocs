# beacon.py
from urllib.parse import urlencode
from typing import Dict
import datetime

DEFAULT_DOMAIN = "cdn-docs-local.test"

def build_beacon_url(uuid: str, domain: str = DEFAULT_DOMAIN, path: str = "/assets/img.png", extra: Dict = None) -> str:
    q = {"id": uuid, "ts": datetime.datetime.utcnow().isoformat()}
    if extra:
        q.update(extra)
    return f"https://{domain}{path}?{urlencode(q)}"

# TODO: Implement conditional triggering for beacons to reduce detection risk.
# Future enhancement: Add logic to trigger beacons only under specific conditions,
# e.g., after multiple document opens, from non-whitelisted IPs, or based on time delays.
# This could involve checking access patterns or embedding conditional metadata.
# Example: def should_trigger_beacon(uuid: str, access_count: int, ip: str) -> bool:
#     return access_count > 1 or ip not in WHITELIST
