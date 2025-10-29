# stego.py
# Lightweight LSB writer/reader (educational, small payloads only)
from PIL import Image
from typing import Optional

def lsb_embed(input_path: str, output_path: str, secret_text: str) -> None:
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()
    data = ''.join(f"{ord(c):08b}" for c in secret_text) + "00000000"  # terminator
    w, h = img.size
    idx = 0
    for y in range(h):
        for x in range(w):
            if idx >= len(data):
                break
            r,g,b,a = pixels[x,y]
            r = (r & ~1) | int(data[idx]); idx+=1
            if idx < len(data):
                g = (g & ~1) | int(data[idx]); idx+=1
            if idx < len(data):
                b = (b & ~1) | int(data[idx]); idx+=1
            pixels[x,y] = (r,g,b,a)
        if idx >= len(data):
            break
    img.save(output_path, "PNG")

def lsb_extract(stego_path: str) -> Optional[str]:
    img = Image.open(stego_path).convert("RGBA")
    pixels = img.load()
    w,h = img.size
    bits = []
    for y in range(h):
        for x in range(w):
            r,g,b,a = pixels[x,y]
            bits.append(str(r&1)); bits.append(str(g&1)); bits.append(str(b&1))
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        val = int(''.join(byte),2)
        if val == 0:
            break
        chars.append(chr(val))
    return ''.join(chars) if chars else None
