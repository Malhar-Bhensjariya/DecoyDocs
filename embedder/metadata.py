# metadata.py
# DOCX custom property writer (safe, simple) and PDF XMP placeholder writer
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional
import shutil
import os
from .utils import ensure_dir

def write_docx_custom_property(src_docx: str, dest_docx: str, prop_name: str, prop_value: str) -> None:
    """
    Non-destructive: copy src -> dest and add/replace custom property in docProps/custom.xml
    """
    ensure_dir(os.path.dirname(dest_docx) or ".")

    # ✅ Skip copy if same path
    if os.path.abspath(src_docx) != os.path.abspath(dest_docx):
        shutil.copy2(src_docx, dest_docx)
    else:
        print(f"Skipping copy: {src_docx} and {dest_docx} are the same file")

    with zipfile.ZipFile(dest_docx, 'a') as z:
        try:
            content = z.read('docProps/custom.xml').decode('utf-8')
            root = ET.fromstring(content)
        except KeyError:
            # create basic structure
            ns = {
                'cp': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
                'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
            }
            root = ET.Element('{http://schemas.openxmlformats.org/officeDocument/2006/custom-properties}Properties')

        # Append property (simple mode)
        prop = ET.Element('{http://schemas.openxmlformats.org/officeDocument/2006/custom-properties}property')
        prop.set('fmtid', '{D5CDD505-2E9C-101B-9397-08002B2CF9AE}')
        prop.set('pid', '2')
        prop.set('name', prop_name)
        vt_lpwstr = ET.Element('{http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes}lpwstr')
        vt_lpwstr.text = prop_value
        prop.append(vt_lpwstr)
        root.append(prop)

        new_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        z.writestr('docProps/custom.xml', new_xml)

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

# TODO: Implement conditional metadata embedding in DOCX.
# Future enhancement: Embed UUID/beacon conditionally, e.g., only if access count exceeds threshold
# or if the document is opened outside expected parameters (e.g., non-corporate IP).
# This could involve querying a central access log or using embedded counters.
