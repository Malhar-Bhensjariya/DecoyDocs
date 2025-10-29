# main.py
# Minimal CLI-style orchestrator (safe: no auto macro insertion, no network calls at generation time)
import argparse
import json
from .utils import gen_uuid, ensure_dir
from .stego import lsb_embed
from .exif_meta import write_png_text
from .beacon import build_beacon_url
from .packer import build_pdf_with_assets
from .uuid_manager import init_db, reserve_uuid, mark_deployed
from .audit import write_audit
import os

CONFIG_PATH = "config/sample_config.json"

def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Embedder orchestrator (lab-only)")
    parser.add_argument("--base-image", required=True, help="PNG/JPG base image to embed into")
    parser.add_argument("--title", default="HoneyDoc", help="Document title")
    parser.add_argument("--out-name", default=None, help="Output PDF name")
    parser.add_argument("--label", default="", help="Human label for this honeydoc")
    args = parser.parse_args()

    cfg = load_config()
    ensure_dir(cfg.get("output_dir","out"))
    init_db()
    u = gen_uuid()
    reserve_uuid(u, label=args.label, template=args.title)
    # stego
    stego_out = os.path.join(cfg.get("output_dir","out"), f"stego_{u}.png")
    if cfg["embed"].get("use_lsb", True):
        lsb_embed(args.base_image, stego_out, u)
    if cfg["embed"].get("use_exif", True):
        write_png_text(stego_out, stego_out, "HoneyUUID", u)
    # beacon url
    beacon = build_beacon_url(u, domain=cfg.get("beacon_domain"))
    # pack to PDF
    out_pdf, manifest_path = build_pdf_with_assets(args.title, stego_out, beacon, out_name=args.out_name)
    mark_deployed(u, manifest_path)
    write_audit({"uuid": u, "label": args.label, "out_pdf": out_pdf, "manifest": manifest_path})
    print("Done:", u)
    print("PDF:", out_pdf)
    print("Manifest:", manifest_path)

if __name__ == "__main__":
    main()
