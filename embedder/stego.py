# stego.py
# Lightweight LSB writer/reader (educational, small payloads only)
from PIL import Image
from typing import Optional

def lsb_embed(input_path: str, output_path: str, secret_text: str) -> None:
    """Embed secret text in image using LSB steganography."""
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()
    data = ''.join(f"{ord(c):08b}" for c in secret_text) + "00000000"  # terminator
    w, h = img.size
    idx = 0
    for y in range(h):
        for x in range(w):
            if idx >= len(data):
                break
            r, g, b, a = pixels[x, y]
            if idx < len(data): r = (r & ~1) | int(data[idx]); idx += 1
            if idx < len(data): g = (g & ~1) | int(data[idx]); idx += 1
            if idx < len(data): b = (b & ~1) | int(data[idx]); idx += 1
            pixels[x, y] = (r, g, b, a)
        if idx >= len(data):
            break
    img.save(output_path, "PNG")

def lsb_extract(stego_path: str) -> Optional[str]:
    """Extract hidden text from steganographic image."""
    img = Image.open(stego_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size
    bits = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            bits.append(str(r & 1))
            bits.append(str(g & 1))
            bits.append(str(b & 1))
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) < 8:
            break
        val = int(''.join(byte), 2)
        if val == 0:
            break
        chars.append(chr(val))
    return ''.join(chars) if chars else None

def create_clickable_stego_html(stego_image_path: str, beacon_url: str, alt_text: str = "Document") -> str:
    """
    Create HTML for clickable steganographic image that triggers beacon.
    
    Args:
        stego_image_path: path to steganographic image
        beacon_url: beacon URL to trigger on click
        alt_text: alt text for accessibility
    
    Returns:
        HTML string with clickable image
    """
    html = f'''<img src="{stego_image_path}"
     alt="{alt_text}"
     style="cursor: pointer; max-width: 100%; display: block; margin: 15px 0;"
     onclick="fetch('{beacon_url}', {{mode: 'no-cors'}}).catch(e => {{}});"
     title="Click to view full document" />'''
    return html
