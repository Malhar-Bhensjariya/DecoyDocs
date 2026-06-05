#!/usr/bin/env python3
"""
simple_generate.py
Lightweight Gemini-based document generator for DecoyDocs backend.
Generates a single DOCX without similarity checks (no sentence-transformers dependency).
"""

import os
import sys
import json
import uuid
import re
import io
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from google import genai
import docx
from docx.shared import Inches
import markdown2
from bs4 import BeautifulSoup

# Load API key
dotenv_path = Path(__file__).resolve().parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in environment or .env file")

client = genai.Client(api_key=api_key)
from templates import TEMPLATES

TEMPLATE_PROMPTS = {k: v["prompt"] for k, v in TEMPLATES.items()}

def generate_docx_from_gemini(title: str, template: str, output_path: str):
    """Generate DOCX using Gemini content."""
    base_prompt = (
        "You are a professional business writer creating a clean internal document. "
        "Write using headings, paragraphs, and list items only. "
        "Do not use markdown horizontal rules or raw divider lines such as '---', '***', or '___'. "
        "Do not include page dividers or raw markdown separators in the response. "
        "Use realistic Indian locale details when requested by the template. "
    )
    prompt_body = TEMPLATE_PROMPTS.get(template, f"Write professional content about {title}.")
    prompt = f"{base_prompt}\n\n{prompt_body.format(title=title)}"
    
    # Call Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    content = response.text
    print(f"DEBUG: Raw Gemini response length: {len(content)}", file=sys.stderr)
    print(f"DEBUG: Raw Gemini response end: {repr(content[-200:])}", file=sys.stderr)
    
    # Post-process to prefer Indian locale/currency as a safety-net in case the model
    # used non-Indian examples. Replace common USD markers with INR/rupee symbol.
    content_text = content
    try:
        # Don't overwrite if rupee symbol already present
        if '₹' not in content_text:
            # Replace $ amounts with ₹, and common currency words
            content_text = content_text.replace('USD', 'INR').replace('usd', 'INR')
            content_text = content_text.replace('$', '₹')
            # Replace plural 'dollars' with 'rupees' (case-insensitive)
            content_text = re.sub(r"\bdollars\b", 'rupees', content_text, flags=re.IGNORECASE)
            content_text = re.sub(r"\bDollar\b", 'Rupee', content_text)
    except Exception as e:
        print(f"Locale post-processing skipped due to error: {e}", file=sys.stderr)

    # Strip lines that consist solely of repeated hyphens/underscores/stars
    # which markdown sometimes emits as page dividers ("---"). Replace them with a single blank line.
    try:
        content_text = re.sub(r'(?m)^[ \t]*[-_*]{3,}[ \t]*$', '\\n', content_text)
    except Exception as e:
        print(f"Divider stripping skipped due to error: {e}", file=sys.stderr)
    
    # Convert markdown to HTML then to DOCX
    print("Converting markdown to HTML...", file=sys.stderr)
    try:
        html = markdown2.markdown(content_text, extras=['fenced-code-blocks', 'tables'])
    except Exception as e:
        print(f"Markdown conversion failed: {e}", file=sys.stderr)
        html = f"<pre>{content_text}</pre>"
        print("Falling back to plain text formatting", file=sys.stderr)
    
    # Remove any HTML paragraphs that are just separators after markdown conversion.
    html = re.sub(r'(?i)<p>\s*[-_*]{3,}\s*</p>', '', html)

    # Create DOCX
    doc = docx.Document()
    doc.add_heading(title, level=1)

    def is_separator_text(text: str) -> bool:
        if not text:
            return True
        return bool(re.fullmatch(r'[\s\-\*_]{3,}', text))

    # Parse HTML and add to doc
    soup = BeautifulSoup(html, "html.parser")
    for elem in soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'blockquote', 'hr']):
        if elem.name in ('h1', 'h2', 'h3'):
            text = elem.get_text(strip=True)
            if not text or is_separator_text(text):
                continue
            level = int(elem.name[1])
            doc.add_heading(text, level=level)
        elif elem.name == 'p':
            text = elem.get_text(strip=True)
            if not text or is_separator_text(text):
                continue
            doc.add_paragraph(text)
        elif elem.name == 'ul':
            for li in elem.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if not text or is_separator_text(text):
                    continue
                doc.add_paragraph(text, style='List Bullet')
        elif elem.name == 'ol':
            for li in elem.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                if not text or is_separator_text(text):
                    continue
                doc.add_paragraph(text, style='List Number')
        elif elem.name == 'blockquote':
            text = elem.get_text(strip=True)
            if not text or is_separator_text(text):
                continue
            p = doc.add_paragraph(text)
            p.style = 'Intense Quote'
        elif elem.name == 'hr':
            # ignore horizontal rules — they can render as long lines/pages in some viewers
            continue
    
    doc.save(output_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: simple_generate.py <title> <template> [output_dir]")
        sys.exit(1)
    
    title = sys.argv[1]
    template = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "generated_docs"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create clean filename
    clean_title = "".join(c for c in title if c.isalnum() or c in ' -_')[:40]
    docx_name = f"{clean_title}_{str(uuid.uuid4())[:8]}.docx"
    output_path = os.path.join(output_dir, docx_name)
    
    try:
        generate_docx_from_gemini(title, template, output_path)
        print(json.dumps({"success": True, "path": output_path, "filename": docx_name}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
