# metadata.py
# DOCX custom property writer (safe, simple) and PDF XMP placeholder writer
import os
import shutil
from typing import Optional

from docx import Document

from .utils import ensure_dir


def write_docx_custom_property(src_docx: str, dest_docx: str, prop_name: str, prop_value: str) -> None:
    """
    Copy src -> dest (if different) and set/replace a custom property using python-docx.
    This keeps the OPC package valid for LibreOffice/Word (content types + relationships).
    """
    ensure_dir(os.path.dirname(dest_docx) or ".")

    src_abs = os.path.abspath(src_docx)
    dest_abs = os.path.abspath(dest_docx)
    if src_abs != dest_abs:
        shutil.copy2(src_abs, dest_abs)

    doc = Document(dest_abs)
    # Replace if present, otherwise add; python-docx handles content types/part wiring.
    doc.custom_properties[prop_name] = prop_value
    doc.save(dest_abs)

def read_docx_custom_property(docx_path: str, prop_name: str) -> Optional[str]:
    # simplistic reader: extract and search for name
    import zipfile, xml.etree.ElementTree as ET
    try:
        with zipfile.ZipFile(docx_path) as z:
            content = z.read('docProps/custom.xml').decode('utf-8')
    except Exception:
        return None
    root = ET.fromstring(content)
    for prop in root:
        if prop.get('name') == prop_name:
            vt = prop.find('{http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes}lpwstr')
            return vt.text if vt is not None else None
    return None

