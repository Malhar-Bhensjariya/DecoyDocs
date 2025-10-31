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
    print("\n[1/7] Generating new documents using llm-docgen/generate_docs.py ...")
    subprocess.run(
        ["python3", "llm-docgen/generate_docs.py", "--count", "1", "--template", "generic_report"],
        check=True,
    )
    print("   -> Document generation complete.\n")


def get_latest_docx() -> Path:
    """Fetch the most recently created docx from generated_docs."""
    docs = list(GENERATED_DIR.glob("*.docx"))
    if not docs:
        raise FileNotFoundError("No DOCX found in generated_docs/.")
    latest = max(docs, key=lambda p: p.stat().st_mtime)
    print(f"[2/7] Latest generated DOCX found: {latest.name}")
    return latest


def embed_metadata_into_docx(docx_path: Path, uuid: str, beacon_url: str) -> Path:
    """Embed UUID and beacon URL into DOCX metadata."""
    ensure_dir(OUT_DIR)
    out_path = OUT_DIR / f"{docx_path.stem}_embedded.docx"
    print(f"[5/7] Embedding metadata into DOCX:\n    Source: {docx_path}\n    Destination: {out_path}")
    write_docx_custom_property(str(docx_path), str(out_path), "HoneyUUID", uuid)
    write_docx_custom_property(str(out_path), str(out_path), "BeaconURL", beacon_url)
    print("   -> Metadata embedded successfully.")
    return out_path


def main():
    print("=== DECOYDOCS PIPELINE START ===")
    ensure_dir(GENERATED_DIR)
    ensure_dir(OUT_DIR)
    init_db()

    # Step 1: Generate new doc(s)
    generate_docs()

    # Step 2: Get latest generated doc
    latest_doc = get_latest_docx()

    # Step 3: Generate UUID + reserve entry
    print("\n[3/7] Generating and reserving UUID ...")
    u = gen_uuid()
    reserve_uuid(u, label="auto_generated", template="llm_doc")
    print(f"   -> Reserved UUID: {u}")

    # Step 4: Build beacon URL
    print("\n[4/7] Building beacon URL ...")
    beacon_url = build_beacon_url(u, domain=BEACON_DOMAIN)
    print(f"   -> Beacon URL: {beacon_url}")

    # Step 5: Embed metadata into the DOCX
    embedded_docx = embed_metadata_into_docx(latest_doc, u, beacon_url)

    # Step 6: Optionally embed EXIF-style PNG metadata
    print("\n[6/7] Checking for base image to embed UUID ...")
    placeholder_image = Path("assets/base.png")
    if placeholder_image.exists():
        stego_out = OUT_DIR / f"uuid_{u}.png"
        write_png_text(str(placeholder_image), str(stego_out), "HoneyUUID", u)
        print(f"   -> UUID embedded into PNG: {stego_out}")
    else:
        print("   -> No base image found. Skipping PNG embedding.")

    # Step 7: Mark deployment
    print("\n[7/7] Marking deployment in manifest ...")
    manifest = OUT_DIR / f"manifest_{u}.json"
    mark_deployed(u, str(manifest))

    # Write summary file
    summary = {
        "uuid": u,
        "docx": str(embedded_docx),
        "beacon_url": beacon_url,
        "manifest": str(manifest),
    }
    summary_path = OUT_DIR / f"summary_{u}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== PIPELINE COMPLETE ===")
    print(f"Generated UUID: {u}")
    print(f"Final Honeydoc: {embedded_docx}")
    print(f"Beacon URL: {beacon_url}")
    print(f"Manifest saved to: {manifest}")
    print(f"Summary file saved to: {summary_path}\n")


if __name__ == "__main__":
    main()
