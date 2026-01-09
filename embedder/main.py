# main.py
# Minimal CLI orchestrator
import argparse
import json
import os
import sys
from .utils import gen_uuid, ensure_dir
from .stego import lsb_embed
from .beacon import build_mixed_beacon_urls
from .packer import build_pdf_with_assets
from .uuid_manager import init_db, reserve_uuid, mark_deployed
from .gemini_graph_generator import generate_graph_with_beacon
from PIL import PngImagePlugin, Image

CONFIG_PATH = "config/sample_config.json"

def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_png_text(image_path: str, output_path: str, key: str, value: str) -> None:
    img = Image.open(image_path)
    meta = PngImagePlugin.PngInfo()
    meta.add_text(key, value)
    img.save(output_path, pnginfo=meta)

def main():
    parser = argparse.ArgumentParser(description="Embedder Orchestrator with Gemini Graph Generation")
    parser.add_argument("--doc-content", required=True, help="Document content text to visualize")
    parser.add_argument("--title", default="HoneyDoc", help="Document title")
    parser.add_argument("--out-name", default=None, help="Output PDF name")
    parser.add_argument("--label", default="", help="Human label for this honeydoc")
    parser.add_argument("--skip-graph", action="store_true", help="Skip graph generation (use stego only)")
    args = parser.parse_args()

    cfg = load_config()
    out_dir = cfg.get("output_dir", "out")
    ensure_dir(out_dir)
    init_db()

    u = gen_uuid()
    doc_folder = os.path.join(out_dir, u)
    ensure_dir(doc_folder)
    
    reserve_uuid(u, label=args.label, template=args.title)

    # Create beacon URLs for steganography data
    beacon_urls = build_mixed_beacon_urls(u)
    data = json.dumps({"uuid": u, "beacons": beacon_urls})

    # Generate professional graph with Gemini (optional) - FIRST
    graph_out = None
    graph_success = False
    if not args.skip_graph:
        graph_out = os.path.join(doc_folder, f"graph_{u}.png")
        print(f"Generating professional graph with Gemini...")
        try:
            success, graph_path = generate_graph_with_beacon(
                document_content=args.doc_content,
                output_path=graph_out,
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

    # Generate steganographic image (LSB embedded) - SECOND, using graph as base if available
    stego_out = os.path.join(doc_folder, f"stego_{u}.png")
    base_for_stego = graph_out if graph_success else cfg.get("default_stego_image", "assets/base.png")
    
    if os.path.exists(base_for_stego):
        if cfg["embed"].get("use_lsb", True):
            lsb_embed(base_for_stego, stego_out, data)
        if cfg["embed"].get("use_png_text", True):
            write_png_text(stego_out, stego_out, "HoneyUUID", u)
        print(f"Stego image created from {'graph' if graph_success else 'base image'}: {stego_out}")
    else:
        print(f"Base stego image not found: {base_for_stego}")

    # Build PDF with all triggers
    print(f"Building PDF with beacons...")
    out_pdf, manifest_path = build_pdf_with_assets(
        args.title, 
        stego_out, 
        beacon_urls, 
        graph_path=graph_out,
        out_name=args.out_name,
        output_dir=doc_folder
    )
    mark_deployed(u, manifest_path)

    print("\n" + "="*60)
    print("HONEYDOC GENERATION COMPLETE")
    print("="*60)
    print(f"UUID: {u}")
    print(f"PDF: {out_pdf}")
    print(f"Manifest: {manifest_path}")
    print(f"Stego: {stego_out}")
    if graph_out:
        print(f"Graph: {graph_out}")
    print(f"\nBeacon URLs:")
    for endpoint, url in beacon_urls.items():
        print(f"  {endpoint}: {url}")
    print("="*60)

if __name__ == "__main__":
    main()
