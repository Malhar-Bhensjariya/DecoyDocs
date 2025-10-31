#!/usr/bin/env python3
"""
pipeline.py
Unified orchestrator: generates docs via LLM, embeds UUID and beacon metadata into them,
and saves honeydocs in /out.
"""

import subprocess
import os
import json
from pathlib import Path
from embedder.utils import gen_uuid, ensure_dir
from embedder.uuid_manager import init_db, reserve_uuid, mark_deployed
from embedder.metadata import write_docx_custom_property
from embedder.exif_meta import write_png_text
from embedder.beacon import build_beacon_url

# ---- Configuration ----
GENERATED_DIR = Path("generated_docs")
OUT_DIR = Path("out")
BEACON_DOMAIN = "cdn-docs-local.test"


def generate_docs():
    """Step 1: Call the LLM document generator."""
    print("🧠 Generating new documents using generate_docs.py ...")
    subprocess.run(
        ["python3", "llm-docgen/generate_docs.py", "--count", "1", "--template", "generic_report"],
        check=True,
    )
    print("✅ Document generation complete.\n")


def get_latest_docx() -> Path:
    """Fetch the most recently created docx from generated_docs."""
    docs = list(GENERATED_DIR.glob("*.docx"))
    if not docs:
        raise FileNotFoundError("No DOCX found in generated_docs/")
    return max(docs, key=lambda p: p.stat().st_mtime)


def embed_metadata_into_docx(docx_path: Path, uuid: str, beacon_url: str) -> Path:
    """Embed UUID and beacon URL into DOCX metadata."""
    ensure_dir(OUT_DIR)
    out_path = OUT_DIR / f"{docx_path.stem}_embedded.docx"
    write_docx_custom_property(str(docx_path), str(out_path), "HoneyUUID", uuid)
    write_docx_custom_property(str(out_path), str(out_path), "BeaconURL", beacon_url)
    print(f"📄 Embedded metadata into: {out_path}")
    return out_path


def main():
    ensure_dir(GENERATED_DIR)
    ensure_dir(OUT_DIR)
    init_db()

    # 1️⃣ Generate new doc(s)
    generate_docs()

    # 2️⃣ Get latest generated doc
    latest_doc = get_latest_docx()
    print(f"🗂️ Latest generated doc: {latest_doc.name}")

    # 3️⃣ Generate UUID + reserve entry
    u = gen_uuid()
    reserve_uuid(u, label="auto_generated", template="llm_doc")

    # 4️⃣ Build beacon URL
    beacon_url = build_beacon_url(u, domain=BEACON_DOMAIN)
    print(f"🌐 Beacon URL: {beacon_url}")

    # 5️⃣ Embed metadata into the docx
    embedded_docx = embed_metadata_into_docx(latest_doc, u, beacon_url)

    # 6️⃣ Write EXIF-like PNG metadata (optional — image watermarking)
    placeholder_image = Path("assets/base.png")
    if placeholder_image.exists():
        stego_out = OUT_DIR / f"uuid_{u}.png"
        write_png_text(str(placeholder_image), str(stego_out), "HoneyUUID", u)
        print(f"🖼️ Embedded HoneyUUID into PNG: {stego_out}")
    else:
        print("⚠️ No base image found, skipping PNG embedding.")

    # 7️⃣ Mark deployment
    manifest = OUT_DIR / f"manifest_{u}.json"
    mark_deployed(u, str(manifest))

    summary = {
        "uuid": u,
        "docx": str(embedded_docx),
        "beacon_url": beacon_url,
        "manifest": str(manifest),
    }
    with open(OUT_DIR / f"summary_{u}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n🎯 Pipeline complete.")
    print(f"UUID: {u}")
    print(f"Final DOCX: {embedded_docx}")
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
