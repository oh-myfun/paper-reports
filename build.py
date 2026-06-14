#!/usr/bin/env python3
"""Scan reports directory and generate manifest.json for static deployment."""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = SCRIPT_DIR / "reports"
OUTPUT_FILE = SCRIPT_DIR / "manifest.json"


def scan_reports():
    results = []
    if not REPORTS_DIR.is_dir():
        return results
    for entry in sorted(REPORTS_DIR.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            pages = sorted(
                [f.name for f in entry.iterdir()
                 if f.is_file() and re.match(r"p\d+\.html$", f.name)]
            )
            if not pages:
                continue
            title = _extract_title(entry / pages[0])
            figures = sorted(
                [f.name for f in (entry / "figures").iterdir() if f.is_file()]
            ) if (entry / "figures").is_dir() else []
            results.append({
                "name": entry.name,
                "title": title,
                "type": "directory",
                "pages": pages,
                "figures": figures,
                "page_count": len(pages),
            })
        elif entry.is_file() and entry.suffix.lower() == ".html":
            title = _extract_title(entry)
            results.append({
                "name": entry.name,
                "title": title,
                "type": "single",
                "pages": [entry.name],
                "figures": [],
                "page_count": 1,
            })
    return results


def _extract_title(fpath):
    try:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return ""


def main():
    data = scan_reports()
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Generated {OUTPUT_FILE} with {len(data)} reports")


if __name__ == "__main__":
    main()
