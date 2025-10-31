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
