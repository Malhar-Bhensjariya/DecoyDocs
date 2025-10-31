# audit.py
# append-only audit writer (JSON lines) with minimal retained info
import json
from datetime import datetime
from .utils import ensure_dir
AUDIT_LOG = "audit.log"

def write_audit(entry: dict):
    ensure_dir(".")
    base = {
        "ts": datetime.utcnow().isoformat(),
    }
    base.update(entry)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(base) + "\n")
