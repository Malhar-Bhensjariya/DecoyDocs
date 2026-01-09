#!/usr/bin/env python3
"""
pipeline_with_graphs.py
Enhanced pipeline that:
1. Generates documents with LLM
2. Generates professional graphs with Gemini
3. Embeds beacons in both stego and graph
4. Creates PDFs with multiple hidden triggers

Integration point for LLM-generated docs + Gemini graphs.
"""

import os
import json
from pathlib import Path
from typing import Tuple, Optional
from embedder.utils import gen_uuid, ensure_dir
from embedder.beacon import build_mixed_beacon_urls
from embedder.packer import build_pdf_with_assets
from embedder.uuid_manager import init_db, reserve_uuid, mark_deployed
from embedder.stego import lsb_embed
from embedder.gemini_graph_generator import generate_graph_with_beacon
from PIL import PngImagePlugin, Image


def create_honeydoc_from_content(
    doc_content: str,
    doc_title: str,
    doc_label: str = "",
    output_dir: str = "out",
    api_key: str = None
) -> Tuple[bool, Optional[str]]:
    """
    Create a complete honeydoc with beacons and graph.
    
    Args:
        doc_content: Generated document text
        doc_title: Document title
        doc_label: Human-readable label
        output_dir: Output directory
        api_key: Gemini API key (optional)
    
    Returns:
        Tuple of (success, pdf_path)
    """
    ensure_dir(output_dir)
    init_db()
    
    # Create unique document
    u = gen_uuid()
    doc_folder = os.path.join(output_dir, u)
    ensure_dir(doc_folder)
    
    reserve_uuid(u, label=doc_label, template=doc_title)
    
    # Generate beacon URLs
    beacon_urls = build_mixed_beacon_urls(u)
    
    # Generate professional graph with Gemini FIRST
    graph_path = None
    print(f"Generating professional graph...")
    try:
        graph_path = os.path.join(doc_folder, f"graph_{u}.png")
        success, graph_file = generate_graph_with_beacon(
            document_content=doc_content,
            output_path=graph_path,
            beacon_url=beacon_urls.get('assets', ''),
            api_key=api_key
        )
        if success:
            print(f"Graph generated: {graph_file}")
        else:
            print(f"Graph generation failed, will use base.png for stego")
            graph_path = None
    except Exception as e:
        print(f"Graph generation error: {e}")
        graph_path = None
    
    # Create stego image (with LSB embedding) - use graph as base if available
    stego_path = os.path.join(doc_folder, f"stego_{u}.png")
    data = json.dumps({"uuid": u, "beacons": beacon_urls})
    
    # Use generated graph as stego base, fallback to base.png
    base_for_stego = graph_path if graph_path else "assets/base.png"
    if os.path.exists(base_for_stego):
        try:
            lsb_embed(base_for_stego, stego_path, data)
            img = Image.open(stego_path)
            meta = PngImagePlugin.PngInfo()
            meta.add_text("HoneyUUID", u)
            img.save(stego_path, pnginfo=meta)
        except Exception as e:
            print(f"Stego embedding error: {e}")
            stego_path = base_for_stego  # Fallback
    else:
        print(f"Base image not found: {base_for_stego}")
        stego_path = None
    
    # Build PDF with all triggers
    try:
        print(f"Building PDF with beacons...")
        pdf_path, manifest_path = build_pdf_with_assets(
            title=doc_title,
            stego_path=stego_path,
            beacon_urls=beacon_urls,
            graph_path=graph_path,
            output_dir=doc_folder
        )
        
        # Mark as deployed
        mark_deployed(u, manifest_path)
        
        print("\n" + "="*60)
        print(f"HONEYDOC CREATED")
        print("="*60)
        print(f"UUID: {u}")
        print(f"Title: {doc_title}")
        print(f"PDF: {pdf_path}")
        print(f"Manifest: {manifest_path}")
        if graph_path:
            print(f"Graph: {graph_path}")
        print(f"\nBeacon URLs:")
        for endpoint, url in beacon_urls.items():
            print(f"  {endpoint}: {url}")
        print("="*60 + "\n")
        
        return True, pdf_path
        
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return False, None
