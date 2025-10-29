# exif_meta.py
# Thin wrapper around exiftool if present; fallback to Pillow for basic PNG tEXt
import subprocess
from typing import Optional
from PIL import Image, PngImagePlugin

def write_exif_comment_exiftool(image_path: str, comment: str) -> None:
    subprocess.run(["exiftool", f"-Comment={comment}", "-overwrite_original", image_path], check=True)

def read_exif_comment_exiftool(image_path: str) -> Optional[str]:
    res = subprocess.run(["exiftool", "-Comment", image_path], capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return res.stdout.strip().split(":",1)[-1].strip()

def write_png_text(image_path: str, output_path: str, key: str, value: str) -> None:
    img = Image.open(image_path)
    meta = PngImagePlugin.PngInfo()
    meta.add_text(key, value)
    img.save(output_path, pnginfo=meta)

def read_png_text(image_path: str, key: str) -> Optional[str]:
    img = Image.open(image_path)
    info = img.info
    return info.get(key)
