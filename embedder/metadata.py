# metadata.py
# DOCX custom property writer (safe, simple) and PDF XMP placeholder writer
import os
import shutil
from typing import Optional

from docx import Document

from .utils import ensure_dir


def write_docx_custom_property(src_docx: str, dest_docx: str, prop_name: str, prop_value: str) -> None:
    """
    Copy src -> dest (if different) and stash the value in standard core properties
    using python-docx only (no manual ZIP/XML surgery).

    - HoneyUUID  -> core_properties.identifier
    - BeaconURL  -> core_properties.comments
    - anything else -> appended to comments
    """
    ensure_dir(os.path.dirname(dest_docx) or ".")

    src_abs = os.path.abspath(src_docx)
    dest_abs = os.path.abspath(dest_docx)
    if src_abs != dest_abs:
        shutil.copy2(src_abs, dest_abs)

    doc = Document(dest_abs)
    cp = doc.core_properties

    if prop_name == "HoneyUUID":
        cp.identifier = prop_value
    elif prop_name == "BeaconURL":
        cp.comments = prop_value
    else:
        existing = cp.comments or ""
        sep = "\n" if existing else ""
        cp.comments = f"{existing}{sep}{prop_name}={prop_value}"

    doc.save(dest_abs)


def read_docx_custom_property(docx_path: str, prop_name: str) -> Optional[str]:
    """Mirror write_docx_custom_property: read from core properties."""
    doc = Document(docx_path)
    cp = doc.core_properties

    if prop_name == "HoneyUUID":
        return cp.identifier
    if prop_name == "BeaconURL":
        return cp.comments

    # Fallback: parse "name=value" lines from comments
    if not cp.comments:
        return None
    for line in cp.comments.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            if k.strip() == prop_name:
                return v.strip()
    return None

