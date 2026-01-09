# beacon.py
from urllib.parse import urlencode
from typing import Dict, List
import datetime
import os
import uuid as uuid_lib
import random

# Use environment variable to switch between test and production
# Set API_BASE_URL=http://localhost:5000 for test server
# Or leave unset/default for production
API_BASE_URL = os.environ.get("API_BASE_URL", "https://fyp-backend-98o5.onrender.com")
DEFAULT_BEACON = f"{API_BASE_URL}/api/beacon"
DEFAULT_FONTS = f"{API_BASE_URL}/fonts"
DEFAULT_ASSETS = f"{API_BASE_URL}/assets"

def build_beacon_url(uuid: str, domain: str = None, path: str = "", extra: Dict = None) -> str:
    """Build /api/beacon endpoint URL."""
    if domain is None:
        domain = DEFAULT_BEACON
    q = {"resource_id": uuid}
    q["nonce"] = str(uuid_lib.uuid4())[:8]
    if extra:
        q.update(extra)
    return f"{domain}{path}?{urlencode(q)}"

def build_fonts_beacon_url(uuid: str, domain: str = None, extra: Dict = None) -> str:
    """Build /fonts endpoint URL for stealthy beacon trigger."""
    if domain is None:
        domain = DEFAULT_FONTS
    fontnames = ["inter-regular.woff2", "roboto-regular.woff2", "opensans-regular.woff2", "lato-regular.woff2"]
    fontname = random.choice(fontnames)
    q = {"resource_id": uuid}
    q["nonce"] = str(uuid_lib.uuid4())[:8]
    if extra:
        q.update(extra)
    return f"{domain}/{fontname}?{urlencode(q)}"

def build_assets_beacon_url(uuid: str, domain: str = None, extra: Dict = None) -> str:
    """Build /assets/media endpoint URL for stealthy beacon trigger."""
    if domain is None:
        domain = DEFAULT_ASSETS
    filenames = ["logo.png", "icon.svg", "banner.jpg", "profile.webp", "avatar.png"]
    filename = random.choice(filenames)
    q = {"resource_id": uuid}
    q["nonce"] = str(uuid_lib.uuid4())[:8]
    if extra:
        q.update(extra)
    return f"{domain}/media/{filename}?{urlencode(q)}"

def build_mixed_beacon_urls(uuid: str) -> Dict[str, str]:
    """Build mixed beacon URLs using both fonts and assets endpoints.
    
    Returns dict with 'fonts' and 'assets' keys containing beacon URLs.
    """
    return {
        "fonts": build_fonts_beacon_url(uuid),
        "assets": build_assets_beacon_url(uuid),
        "beacon": build_beacon_url(uuid),
    }
