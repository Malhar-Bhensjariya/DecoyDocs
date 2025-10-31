# utils.py
from typing import Tuple
import uuid
import pathlib
import hashlib

def gen_uuid() -> str:
    return str(uuid.uuid4())

def safe_filename(name: str) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
    return safe[:255]

def file_checksum(path: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_dir(path: str):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
