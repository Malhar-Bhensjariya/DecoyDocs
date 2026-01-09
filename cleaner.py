#!/usr/bin/env python3
"""
cleaner.py
Cleanup script to remove all generated files and databases created by pipeline.py.
This allows rerunning the pipeline from scratch after code changes.

Removes:
- generated_docs/ directory and contents
- out/ directory and contents
- honeypot.db database file
"""

import os
import shutil
from pathlib import Path

def cleanup():
    """Remove generated files and databases."""
    base_dir = Path(__file__).parent

    # Directories to remove
    dirs_to_remove = [
        base_dir / "generated_docs",
        base_dir / "out"
    ]

    # Files to remove
    files_to_remove = [
        base_dir / "honeypot.db"
    ]

    print("🧹 Starting cleanup...")

    # Remove directories
    for dir_path in dirs_to_remove:
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            print(f"Removed directory: {dir_path}")
        else:
            print(f"Directory not found: {dir_path}")

    # Remove files
    for file_path in files_to_remove:
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            print(f"Removed file: {file_path}")
        else:
            print(f"File not found: {file_path}")

    print("Cleanup complete! You can now rerun pipeline.py from scratch.")

if __name__ == "__main__":
    # Simple confirmation
    response = input("This will delete generated_docs/, out/, and honeypot.db. Continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        cleanup()
    else:
        print("Cleanup cancelled.")