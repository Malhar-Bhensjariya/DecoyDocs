#!/usr/bin/env python3
"""Quick test of simple_generate.py"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Setup
test_output_dir = Path("test_gen_output")
test_output_dir.mkdir(exist_ok=True)

# Test 1: Check imports work
print("Test 1: Checking imports...")
try:
    from dotenv import load_dotenv
    from google import genai
    import docx
    import markdown2
    from bs4 import BeautifulSoup
    print("✓ All imports successful\n")
except ImportError as e:
    print(f"✗ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Check Gemini API key
print("Test 2: Checking Gemini API key...")
dotenv_path = Path("llm-docgen/.env")
if dotenv_path.exists():
    load_dotenv(dotenv_path)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✓ API key configured: {api_key[:20]}...\n")
    else:
        print("✗ No API key found in .env file\n")
else:
    print("✗ .env file not found\n")

# Test 3: Test simple_generate.py
print("Test 3: Testing simple_generate.py...")
result = subprocess.run([
    sys.executable,
    "llm-docgen/simple_generate.py",
    "Test Document",
    "generic_report",
    str(test_output_dir)
], capture_output=True, text=True)

print(f"Exit code: {result.returncode}")
print(f"Stdout: {result.stdout}")
if result.stderr:
    print(f"Stderr: {result.stderr}")

if result.returncode == 0:
    try:
        output = json.loads(result.stdout)
        if output.get("success"):
            doc_path = Path(output["path"])
            if doc_path.exists():
                size = doc_path.stat().st_size
                print(f"✓ Generated DOCX: {output['filename']} ({size} bytes)\n")
            else:
                print(f"✗ DOCX file not found at {doc_path}\n")
        else:
            print(f"✗ Generation failed: {output.get('error')}\n")
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse output as JSON: {e}\n")
else:
    print("✗ simple_generate.py failed\n")

print("Test complete!")
