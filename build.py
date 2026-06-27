#!/usr/bin/env python3
"""Verify manifest.json exists for static deployment."""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_FILE = SCRIPT_DIR / "manifest.json"

def main():
    if not MANIFEST_FILE.exists():
        print(f"ERROR: {MANIFEST_FILE} not found")
        return
    data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    print(f"manifest.json verified: {len(data)} reports")

if __name__ == "__main__":
    main()
