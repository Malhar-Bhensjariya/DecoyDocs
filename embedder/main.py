# main.py
# Minimal CLI orchestrator
import argparse
import json
import os
from .utils import gen_uuid, ensure_dir
from .stego import lsb_embed
from .beacon import build_beacon_url
from .packer import build_pdf_with_assets
from .uuid_manager import init_db, reserve_uuid, mark_deployed
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
    parser = argparse.ArgumentParser(description="Embedder Orchestrator")
    parser.add_argument("--base-image", required=True, help="PNG/JPG base image to embed into")
    parser.add_argument("--title", default="HoneyDoc", help="Document title")
    parser.add_argument("--out-name", default=None, help="Output PDF name")
    parser.add_argument("--label", default="", help="Human label for this honeydoc")
    args = parser.parse_args()

    cfg = load_config()
    ensure_dir(cfg.get("output_dir", "out"))
    init_db()

    u = gen_uuid()
    reserve_uuid(u, label=args.label, template=args.title)

    stego_out = os.path.join(cfg.get("output_dir", "out"), f"stego_{u}.png")
    if cfg["embed"].get("use_lsb", True):
        lsb_embed(args.base_image, stego_out, u)
    if cfg["embed"].get("use_png_text", True):
        write_png_text(stego_out, stego_out, "HoneyUUID", u)

    beacon = build_beacon_url(u, domain=cfg.get("beacon_domain"))
    out_pdf, manifest_path = build_pdf_with_assets(args.title, stego_out, beacon, out_name=args.out_name)
    mark_deployed(u, manifest_path)

    print("✅ Done:", u)
    print("📄 PDF:", out_pdf)
    print("📜 Manifest:", manifest_path)

if __name__ == "__main__":
    main()
