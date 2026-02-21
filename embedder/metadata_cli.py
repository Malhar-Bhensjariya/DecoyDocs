#!/usr/bin/env python3
"""
Simple CLI wrapper around embedder.metadata.write_docx_custom_property
Usage: python embedder/metadata_cli.py <src_docx> <dest_docx> <prop_name> <prop_value>

This is used by the Node decoydocs endpoint to write HoneyUUID / BeaconURL into DOCX core properties.
"""
import sys
import argparse
from pathlib import Path

# Ensure repository root is on sys.path so "from embedder.metadata import ..." works
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from embedder.metadata import write_docx_custom_property
except Exception as e:
    # Provide a clearer error message if import still fails
    raise ImportError(f"Failed to import embedder.metadata (ROOT={ROOT}): {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='source docx path')
    parser.add_argument('dest', help='destination docx path (can be same)')
    parser.add_argument('prop', help='property name (HoneyUUID|BeaconURL|other)')
    parser.add_argument('value', help='property value')
    args = parser.parse_args()

    write_docx_custom_property(args.src, args.dest, args.prop, args.value)
    print('OK')


if __name__ == '__main__':
    main()