#!/usr/bin/env python3
"""
pipeline.py
Unified orchestrator: generates 5 unique docs via LLM (one per template), validates similarity, embeds UUID and 
mixed beacon metadata into them, and saves honeydocs in /out with Gemini-generated graphs.
"""

import subprocess
import os
import json
import sys
import time
from pathlib import Path
from embedder.utils import gen_uuid, ensure_dir
from embedder.uuid_manager import init_db, reserve_uuid, mark_deployed
from embedder.stego import lsb_embed
from embedder.beacon import build_mixed_beacon_urls, build_beacon_url
from embedder.packer import build_pdf_with_assets
try:
    from embedder.gemini_graph_generator import generate_graph_with_beacon
    GEMINI_AVAILABLE = True
except ImportError:
    print("Gemini not available, graphs will be skipped")
    GEMINI_AVAILABLE = False
    generate_graph_with_beacon = None
from PIL import PngImagePlugin, Image
try:
    from similarity import check_similarity_threshold, compute_similarity_matrix
    SIMILARITY_AVAILABLE = True
except ImportError:
    print("Similarity checking not available, will skip uniqueness validation")
    SIMILARITY_AVAILABLE = False
    check_similarity_threshold = lambda docs, threshold: False
    compute_similarity_matrix = lambda docs: [[0.0] * len(docs)] * len(docs)
import numpy as np
import requests
from datetime import datetime
from datetime import timezone

# ---- Configuration ----
GENERATED_DIR = Path("generated_docs")
OUT_DIR = Path("out")
# Use environment variable to switch between test and production
# Set API_BASE_URL=http://localhost:5000 for test server
# Or leave unset/default for production
API_BASE_URL = os.environ.get("API_BASE_URL", "https://fyp-backend-98o5.onrender.com")
BEACON_DOMAIN = f"{API_BASE_URL}/api/beacon"
DOCUMENTS_API_URL = f"{API_BASE_URL}/api/documents/create"
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


def generate_doc_with_retry(template: str, attempts: int = 3, base_delay: int = 8) -> bool:
    """
    Run llm-docgen for a template with basic retry/backoff to tolerate transient model outages.
    Returns True on success, False after exhausting retries.
    """
    for attempt in range(1, attempts + 1):
        print(f"Generating document for template: {template} (attempt {attempt}/{attempts})")
        try:
            subprocess.run(
                ["python3", "llm-docgen/generate_docs.py", "--count", "1", "--template", template],
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Generation failed (exit {e.returncode}) for template {template}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"Generation exception for template {template}: {e}")

        if attempt < attempts:
            delay = base_delay * attempt
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"Giving up on template: {template} after {attempts} attempts.")
    return False


def main():
    print("=== DECOYDOCS PIPELINE START ===")
    ensure_dir(GENERATED_DIR)
    ensure_dir(OUT_DIR)
    init_db()

    # Step 1: Generate 5 documents, one per template (unless we already have enough)
    templates = list(TEMPLATE_TO_FOLDER.keys())
    existing_docx = list(GENERATED_DIR.glob("*.docx"))
    if len(existing_docx) >= len(templates):
        print(f"\n[1/5] Found {len(existing_docx)} existing DOCX in {GENERATED_DIR}, skipping generation and reusing them.")
    else:
        print(f"\n[1/5] Generating {len(templates)} documents with one per template...")
        failed_templates = []
        for template in templates:
            ok = generate_doc_with_retry(template)
            if not ok:
                failed_templates.append(template)
        if failed_templates:
            raise ValueError(
                f"Document generation failed for templates: {failed_templates}. "
                "Check model/API availability and retry."
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
    if SIMILARITY_AVAILABLE:
        print("\n[2/5] Computing similarity matrix...")
        sim_matrix = compute_similarity_matrix(doc_tuples)
        print("Cosine Similarity Matrix:")
        print(sim_matrix)

        # Check global similarity
        if check_similarity_threshold(doc_tuples, SIMILARITY_THRESHOLD):
            print("Warning: Some documents have similarity >= threshold. Enforcement not fully implemented; proceeding.")
    else:
        print("\n[2/5] Skipping similarity check (sentence-transformers not available)")
        sim_matrix = [[0.0] * len(doc_tuples)] * len(doc_tuples)

    # Step 3: Create honeydocs with all triggers (visible links, graph, hidden regions)
    uuids = []
    embedded_docs = []
    pdf_docs = []
    for i, docx_path in enumerate(docs):
        template = templates[i]
        folder = TEMPLATE_TO_FOLDER[template]
        output_dir = OUT_DIR / folder
        print(f"\n[3.{i+1}/5] Creating honeydoc for {docx_path.name} (template: {template}, folder: {folder})...")

        u = gen_uuid()
        reserve_uuid(u, label=f"doc_{i+1}", template=template)
        uuids.append(u)
        print(f"Reserved UUID: {u}")

        # Extract document text for graph generation
        doc_text = read_doc_text(docx_path)
        print(f"Extracted {len(doc_text)} characters of content")

        # Create beacon URLs for steganography data
        beacon_urls = build_mixed_beacon_urls(u)
        data = json.dumps({"uuid": u, "beacons": beacon_urls})

        # Define base image for fallback
        base_image = Path("assets/base.png")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate professional graph with Gemini (optional) - FIRST
        graph_out = output_dir / f"graph_{u}.png"
        graph_success = False
        if GEMINI_AVAILABLE:
            print(f"Generating professional graph with Gemini...")
            try:
                success, graph_path = generate_graph_with_beacon(
                    document_content=doc_text,
                    output_path=str(graph_out),
                    beacon_url=beacon_urls.get('assets', '')
                )
                if success:
                    print(f"Graph generated: {graph_path}")
                    graph_success = True
                else:
                    print(f"Graph generation failed, will use base image for stego")
                    graph_out = None
            except Exception as e:
                print(f"Graph generation error: {e}, will use base image for stego")
                graph_out = None
        else:
            print(f"Skipping graph generation (Gemini not available)")
            graph_out = None

        # Generate steganographic image (LSB embedded) - SECOND, using graph as base if available
        stego_out = output_dir / f"stego_{u}.png"
        base_for_stego = str(graph_out) if graph_success else str(base_image)
        
        if os.path.exists(base_for_stego):
            if lsb_embed(base_for_stego, str(stego_out), data):
                print(f"Stego image created from {'graph' if graph_success else 'base image'}: {stego_out}")
            else:
                print(f"LSB embedding failed, using base image")
                stego_out = Path(base_for_stego)
        else:
            print("No base image found for stego, stego will be None")
            stego_out = None

        # Build PDF with ALL triggers using new packer
        print(f"Building PDF with all triggers...")
        try:
            out_pdf, manifest_path = build_pdf_with_assets(
                title=f"{template.replace('_', ' ').title()} Report",
                stego_path=str(stego_out) if stego_out else None,
                beacon_urls=beacon_urls,
                graph_path=str(graph_out) if graph_out else None,
                out_name=f"{template}_{u}",
                output_dir=str(output_dir)
            )
            pdf_docs.append(Path(out_pdf))
            embedded_docs.append(docx_path)  # Keep original DOCX reference
            print(f"Honeydoc created: {out_pdf}")
            print(f"   Manifest: {manifest_path}")
        except Exception as e:
            print(f"Failed to create honeydoc: {e}")
            raise

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
            "beacon_urls": build_mixed_beacon_urls(u),  # All 3 endpoint types
            "beacon_url": build_beacon_url(u),  # Legacy, for backward compatibility
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
    try:
        response = requests.post(DOCUMENTS_API_URL, json=documents_metadata)
        if response.status_code == 200:
            print("Metadata sent to honeypot server successfully.")
        else:
            print(f"Failed to send metadata: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending metadata to server: {e}")

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
