# packer.py
# Build final PDF via HTML -> wkhtmltopdf
import os
import subprocess
from typing import Tuple
from .utils import ensure_dir, safe_filename, file_checksum
import json

OUTPUT_DIR = "out"

def build_pdf_with_assets(title: str, stego_path: str, beacon_url: str, out_name: str = None, output_dir: str = "out") -> Tuple[str, str]:
    ensure_dir(output_dir)
    out_name = safe_filename(out_name or f"{title}.pdf")
    out_path = os.path.join(output_dir, out_name)

    html = f"""
    <html>
      <body>
        <h1>{title}</h1>
        <p>Document UUID embedded in image.</p>
        <img src="{beacon_url}" alt="remote-beacon" style="display:none;" />
        <p>Embedded image:</p>
        <img src="file://{os.path.abspath(stego_path)}" alt="stego" />
      </body>
    </html>
    """
    tmp_html = os.path.join(output_dir, "tmp_embed.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html)

    subprocess.run(["wkhtmltopdf", tmp_html, out_path], check=True)
    os.remove(tmp_html)

    checksum = file_checksum(out_path)
    manifest = {
        "path": out_path,
        "checksum": checksum,
        "title": title,
        "stego": stego_path,
        "beacon": beacon_url
    }
    manifest_path = out_path + ".manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)
    return out_path, manifest_path

# TODO: Implement conditional beacon embedding in PDFs.
# Future enhancement: Embed beacons conditionally based on document access patterns,
# e.g., only include beacon URL if the document has been opened multiple times or from suspicious IPs.
# This requires tracking access state, possibly via a shared database or metadata checks.
