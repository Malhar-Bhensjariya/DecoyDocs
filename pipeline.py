#!/usr/bin/env python3
"""
pipeline.py
Unified orchestrator: generates 3 unique docs via LLM, validates similarity, embeds UUID and beacon metadata into them,
and saves honeydocs in /out.
"""

import subprocess
import os
import json
import sys
from pathlib import Path
from embedder.utils import gen_uuid, ensure_dir
from embedder.uuid_manager import init_db, reserve_uuid, mark_deployed
from embedder.metadata import write_docx_custom_property
from embedder.exif_meta import write_png_text
from embedder.beacon import build_beacon_url
from similarity import check_similarity_threshold, compute_similarity_matrix
import numpy as np
import requests
from datetime import datetime
from datetime import timezone

# ---- Configuration ----
GENERATED_DIR = Path("generated_docs")
OUT_DIR = Path("out")
BEACON_DOMAIN = "https://fyp-backend-98o5.onrender.com/api/beacon"
SIMILARITY_THRESHOLD = 0.80

# Mapping from template key to output folder
TEMPLATE_TO_FOLDER = {
    "generic_report": "Strategy",
    "employee_bonus": "HR",
    "q3_financial": "Finance",
    "hr_review": "Engineering",
    "sales_pipeline": "Sales"
}


def generate_single_doc(avoid_topics=None, avoid_terms=None):
    """Generate a single document with optional avoid lists."""
    print("Generating single document...")
    cmd = ["python3", "llm-docgen/generate_docs.py", "--count", "1", "--template", "generic_report"]
    if avoid_topics:
        cmd.extend(["--avoid-topics", json.dumps(avoid_topics)])
    if avoid_terms:
        cmd.extend(["--avoid-terms", json.dumps(avoid_terms)])
    subprocess.run(cmd, check=True)
    print("Document generation complete.")


def get_latest_docx() -> Path:
    """Fetch the most recently created docx from generated_docs."""
    docs = list(GENERATED_DIR.glob("*.docx"))
    if not docs:
        raise FileNotFoundError("No DOCX found in generated_docs/.")
    latest = max(docs, key=lambda p: p.stat().st_mtime)
    print(f"Latest generated DOCX: {latest.name}")
    return latest


def read_doc_text(docx_path: Path) -> str:
    """Extract text from DOCX for similarity check."""
    from docx import Document
    doc = Document(str(docx_path))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def generate_three_docs():
    """Generate 3 documents with similarity enforcement."""
    docs = []
    avoid_topics_agg = []
    avoid_terms_agg = []

    for i in range(3):
        print(f"\n[1.{i+1}/3] Generating Document {i+1}...")
        if i == 0:
            generate_single_doc()
        else:
            # For doc 2 and 3, use aggregated avoid lists
            generate_single_doc(avoid_topics_agg, avoid_terms_agg)

        latest_doc = get_latest_docx()
        text = read_doc_text(latest_doc)

        # Check similarity with previous docs
        current_docs = docs + [(f"doc_{i}", text)]
        if len(current_docs) > 1 and check_similarity_threshold(current_docs, SIMILARITY_THRESHOLD):
            print(f"Document {i+1} too similar to previous. Regenerating...")
            # Extract avoid from previous
            prev_topics, prev_terms = extract_avoid_from_text(text)  # Need to implement
            avoid_topics_agg.extend(prev_topics)
            avoid_terms_agg.extend(prev_terms)
            # Retry
            generate_single_doc(avoid_topics_agg, avoid_terms_agg)
            latest_doc = get_latest_docx()
            text = read_doc_text(latest_doc)

        docs.append((f"doc_{i}", text))
        print(f"Document {i+1} accepted.")

    return docs


def extract_avoid_from_text(text: str):
    """Extract topics and terms from text."""
    # Simple implementation
    lines = text.split('\n')
    topics = [line.strip() for line in lines if line.isupper() or line.startswith('**')]
    terms = []
    for line in lines:
        words = [w for w in line.split() if len(w) > 4]
        terms.extend(words)
    return topics, terms


def embed_metadata_into_docx(docx_path: Path, uuid: str, beacon_url: str, output_path: Path) -> Path:
    """Embed UUID and beacon URL into DOCX metadata."""
    ensure_dir(output_path.parent)
    print(f"Embedding metadata into DOCX: {docx_path} -> {output_path}")
    write_docx_custom_property(str(docx_path), str(output_path), "HoneyUUID", uuid)
    write_docx_custom_property(str(output_path), str(output_path), "BeaconURL", beacon_url)
    print("Metadata embedded successfully.")
    return output_path


def convert_docx_to_pdf(docx_path: Path, output_dir: Path) -> Path:
    """Convert a DOCX to PDF via headless LibreOffice for cross-platform compatibility."""
    ensure_dir(output_dir)
    libreoffice_bin = os.environ.get("LIBREOFFICE_BIN") or "libreoffice"
    out_pdf = output_dir / f"{docx_path.stem}.pdf"
    cmd = [
        libreoffice_bin,
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to",
        "pdf:writer_pdf_Export",
        "--outdir",
        str(output_dir),
        str(docx_path),
    ]
    print(f"Converting DOCX to PDF: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    if not out_pdf.exists():
        raise FileNotFoundError(f"Expected PDF not found after conversion: {out_pdf}")
    print(f"PDF ready at: {out_pdf}")
    return out_pdf


def main():
    print("=== DECOYDOCS PIPELINE START ===")
    ensure_dir(GENERATED_DIR)
    ensure_dir(OUT_DIR)
    init_db()

    # Step 1: Generate 5 documents, one per template
    templates = list(TEMPLATE_TO_FOLDER.keys())
    print(f"\n[1/5] Generating {len(templates)} documents with one per template...")
    for template in templates:
        print(f"Generating document for template: {template}")
        subprocess.run(
            ["python3", "llm-docgen/generate_docs.py", "--count", "1", "--template", template],
            check=True,
        )
    print("Document generation complete.")

    # Step 2: Find the 5 generated docs
    docx_files = list(GENERATED_DIR.glob("*.docx"))
    docx_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)  # Most recent first
    if len(docx_files) < len(templates):
        raise ValueError(f"Not enough DOCX files generated. Expected {len(templates)}, got {len(docx_files)}.")
    docs = docx_files[:len(templates)]

    # Read texts for similarity matrix
    texts = [read_doc_text(doc) for doc in docs]
    doc_labels = [f"doc_{i+1}" for i in range(len(templates))]
    doc_tuples = list(zip(doc_labels, texts))

    # Compute similarity matrix
    print("\n[2/5] Computing similarity matrix...")
    sim_matrix = compute_similarity_matrix(doc_tuples)
    print("Cosine Similarity Matrix:")
    print(sim_matrix)

    # Check global similarity
    if check_similarity_threshold(doc_tuples, SIMILARITY_THRESHOLD):
        print("Warning: Some documents have similarity >= threshold. Enforcement not fully implemented; proceeding.")

    # Step 3: Embed metadata into each doc
    uuids = []
    embedded_docs = []
    pdf_docs = []
    for i, docx_path in enumerate(docs):
        template = templates[i]
        folder = TEMPLATE_TO_FOLDER[template]
        output_dir = OUT_DIR / folder
        print(f"\n[3.{i+1}/5] Embedding metadata for {docx_path.name} (template: {template}, folder: {folder})...")

        u = gen_uuid()
        reserve_uuid(u, label=f"doc_{i+1}", template=template)
        uuids.append(u)
        print(f"Reserved UUID: {u}")

        beacon_url = build_beacon_url(u, domain=BEACON_DOMAIN)
        print(f"Beacon URL: {beacon_url}")

        embedded_docx = embed_metadata_into_docx(docx_path, u, beacon_url, output_dir / f"{docx_path.stem}_embedded.docx")
        embedded_docs.append(embedded_docx)

        # Convert to PDF for Linux compatibility/consumers
        embedded_pdf = convert_docx_to_pdf(embedded_docx, output_dir)
        pdf_docs.append(embedded_pdf)

    # TODO: Implement conditional beacon triggering in pipeline.
    # Future enhancement: Add checks before embedding beacons, e.g., based on document template,
    # deployment context, or access history. For example, only embed active beacons for high-risk docs.
    # This requires integration with a monitoring system to track opens.

    # Step 4: Optional PNG
    print("\n[4/5] Checking for base image...")
    placeholder_image = Path("assets/base.png")
    if placeholder_image.exists():
        for i, u in enumerate(uuids):
            template = templates[i]
            folder = TEMPLATE_TO_FOLDER[template]
            stego_out = OUT_DIR / folder / f"uuid_{u}.png"
            write_png_text(str(placeholder_image), str(stego_out), "HoneyUUID", u)
            print(f"UUID embedded into PNG: {stego_out}")
    else:
        print("No base image found. Skipping PNG embedding.")

    # Step 5: Mark deployments
    print("\n[5/5] Marking deployments...")
    documents_metadata = []
    for i, u in enumerate(uuids):
        template = templates[i]
        folder = TEMPLATE_TO_FOLDER[template]
        output_dir = OUT_DIR / folder
        manifest = output_dir / f"manifest_{u}.json"
        mark_deployed(u, str(manifest))

        embedded_doc = embedded_docs[i]
        summary = {
            "uuid": u,
            "docx": str(embedded_doc),
            "pdf": str(pdf_docs[i]),
            "beacon_url": build_beacon_url(u, domain=BEACON_DOMAIN),
            "manifest": str(manifest),
            "template": template,
            "folder": folder
        }
        summary_path = output_dir / f"summary_{u}.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Collect metadata for API
        documents_metadata.append({
            "uuid": u,
            "file_path": str(embedded_doc),
            "pdf_path": str(pdf_docs[i]),
            "document_name": f"{template}_{i+1}",
            "created_at": datetime.now(timezone.utc).isoformat()
        })

    # Send metadata to honeypot server
    api_url = "https://fyp-backend-98o5.onrender.com/api/documents/create"
    try:
        response = requests.post(api_url, json=documents_metadata)
        if response.status_code == 200:
            print("✅ Metadata sent to honeypot server successfully.")
        else:
            print(f"⚠️ Failed to send metadata: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error sending metadata to server: {e}")

    # Output
    print("\n=== PIPELINE COMPLETE ===")
    print("Generated UUIDs:", uuids)
    print("Embedded Docs:", [str(d) for d in embedded_docs])
    print("PDF Docs:", [str(p) for p in pdf_docs])
    print("Similarity Matrix:")
    print(sim_matrix)
    print("UUID ↔ Document Mapping:")
    for i, u in enumerate(uuids):
        template = templates[i]
        folder = TEMPLATE_TO_FOLDER[template]
        print(f"{u} -> {embedded_docs[i].name} / {pdf_docs[i].name} (template: {template}, folder: {folder})")


if __name__ == "__main__":
    main()
