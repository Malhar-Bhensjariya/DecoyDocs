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

# ---- Configuration ----
GENERATED_DIR = Path("generated_docs")
OUT_DIR = Path("out")
BEACON_DOMAIN = "cdn-docs-local.test"
SIMILARITY_THRESHOLD = 0.80


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


def embed_metadata_into_docx(docx_path: Path, uuid: str, beacon_url: str) -> Path:
    """Embed UUID and beacon URL into DOCX metadata."""
    ensure_dir(OUT_DIR)
    out_path = OUT_DIR / f"{docx_path.stem}_embedded.docx"
    print(f"Embedding metadata into DOCX: {docx_path} -> {out_path}")
    write_docx_custom_property(str(docx_path), str(out_path), "HoneyUUID", uuid)
    write_docx_custom_property(str(out_path), str(out_path), "BeaconURL", beacon_url)
    print("Metadata embedded successfully.")
    return out_path


def main():
    print("=== DECOYDOCS PIPELINE START ===")
    ensure_dir(GENERATED_DIR)
    ensure_dir(OUT_DIR)
    init_db()

    # Step 1: Generate 3 unique docs with internal similarity checks
    print("\n[1/5] Generating 3 documents with similarity enforcement...")
    subprocess.run(
        ["python3", "llm-docgen/generate_docs.py", "--count", "3", "--template", "generic_report"],
        check=True,
    )
    print("Document generation complete.")

    # Step 2: Find the 3 generated docs
    docx_files = list(GENERATED_DIR.glob("*.docx"))
    docx_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)  # Most recent first
    if len(docx_files) < 3:
        raise ValueError("Not enough DOCX files generated.")
    docs = docx_files[:3]

    # Read texts for similarity matrix
    texts = [read_doc_text(doc) for doc in docs]
    doc_labels = [f"doc_{i+1}" for i in range(3)]
    doc_tuples = list(zip(doc_labels, texts))

    # Compute similarity matrix
    print("\n[2/5] Computing similarity matrix...")
    sim_matrix = compute_similarity_matrix(doc_tuples)
    print("Cosine Similarity Matrix:")
    print(sim_matrix)

    # Step 3: Embed metadata into each doc
    uuids = []
    embedded_docs = []
    for i, docx_path in enumerate(docs):
        print(f"\n[3.{i+1}/5] Embedding metadata for {docx_path.name}...")

        u = gen_uuid()
        reserve_uuid(u, label=f"doc_{i+1}", template="llm_doc")
        uuids.append(u)
        print(f"Reserved UUID: {u}")

        beacon_url = build_beacon_url(u, domain=BEACON_DOMAIN)
        print(f"Beacon URL: {beacon_url}")

        embedded_docx = embed_metadata_into_docx(docx_path, u, beacon_url)
        embedded_docs.append(embedded_docx)

    # Step 4: Optional PNG
    print("\n[4/5] Checking for base image...")
    placeholder_image = Path("assets/base.png")
    if placeholder_image.exists():
        for u in uuids:
            stego_out = OUT_DIR / f"uuid_{u}.png"
            write_png_text(str(placeholder_image), str(stego_out), "HoneyUUID", u)
            print(f"UUID embedded into PNG: {stego_out}")
    else:
        print("No base image found. Skipping PNG embedding.")

    # Step 5: Mark deployments
    print("\n[5/5] Marking deployments...")
    for i, u in enumerate(uuids):
        manifest = OUT_DIR / f"manifest_{u}.json"
        mark_deployed(u, str(manifest))

        summary = {
            "uuid": u,
            "docx": str(embedded_docs[i]),
            "beacon_url": build_beacon_url(u, domain=BEACON_DOMAIN),
            "manifest": str(manifest),
        }
        summary_path = OUT_DIR / f"summary_{u}.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    # Output
    print("\n=== PIPELINE COMPLETE ===")
    print("Generated UUIDs:", uuids)
    print("Embedded Docs:", [str(d) for d in embedded_docs])
    print("Similarity Matrix:")
    print(sim_matrix)
    print("UUID ↔ Document Mapping:")
    for i, u in enumerate(uuids):
        print(f"{u} -> {embedded_docs[i].name}")


if __name__ == "__main__":
    main()
