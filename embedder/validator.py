# validator.py
# Simple validators to confirm embedded artifacts exist
from .stego import lsb_extract
from .exif_meta import read_png_text, read_exif_comment_exiftool
from .metadata import read_docx_custom_property
from typing import Dict, Optional

def validate_stego_image(img_path: str) -> Optional[str]:
    # try LSB extract first
    payload = lsb_extract(img_path)
    if payload:
        return payload
    # fallback: try PNG text
    t = read_png_text(img_path, "HoneyUUID")
    if t:
        return t
    # fallback: exiftool if present
    try:
        t2 = read_exif_comment_exiftool(img_path)
        return t2
    except Exception:
        return None

def validate_docx_custom(docx_path: str, prop_name: str = "HoneyUUID") -> Optional[str]:
    return read_docx_custom_property(docx_path, prop_name)
