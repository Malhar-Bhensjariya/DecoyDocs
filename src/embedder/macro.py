# macro.py
# Produce *text-only* macro templates for lab use. DO NOT auto-insert or execute.
from typing import Tuple
from .utils import gen_uuid

def generate_macro_template(uuid_str: str = None, beacon_url: str = "") -> Tuple[str,str]:
    """
    Returns (uuid, macro_text). Macro text is safe: commented, illustrative, and must be pasted manually in lab.
    """
    u = uuid_str or gen_uuid()
    safe_beacon = beacon_url or f"https://{u}.beacon.local/ping?id={u}"
    macro = f"""' LAB-ONLY VBA TEMPLATE - DO NOT DEPLOY OUTSIDE ISOLATED LAB
' HoneyUUID: {u}
' The following is a *commented* educational example. It is intentionally non-executing.
'
' Sub Document_Open()
'   ' Example (commented): perform a GET to beacon URL (lab-only)
'   ' Dim http As Object
'   ' Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
'   ' http.Open "GET", "{safe_beacon}", False
'   ' http.Send
' End Sub
'
' Paste and uncomment only inside an isolated snapshot VM when explicitly approved.
"""
    return u, macro
