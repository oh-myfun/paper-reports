#!/usr/bin/env python3
"""Scan reports directory and generate manifest.json for static deployment."""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = SCRIPT_DIR / "reports"
OUTPUT_FILE = SCRIPT_DIR / "manifest.json"

TAG_MAP = {
    "minimind-o.html": ["LM", "Omni", "ASR", "0.1B"],
    "omnivoice.html": ["TTS", "DiT", "0.6B"],
    "seed-tts.html": ["TTS", "VC"],
    "supertonic-tts.html": ["TTS", "44M"],
    "supertonic-tts-appendix.html": ["TTS", "Appendix", "44M"],
    "matcha-tts.html": ["TTS", "18M"],
}


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
            description = _extract_description(entry / pages[0])
            year = _extract_year(entry / pages[0])
            figures = sorted(
                [f.name for f in (entry / "figures").iterdir() if f.is_file()]
            ) if (entry / "figures").is_dir() else []
            results.append({
                "name": entry.name,
                "title": title,
                "description": description,
                "year": year,
                "tags": TAG_MAP.get(entry.name, []),
                "type": "directory",
                "pages": pages,
                "figures": figures,
                "page_count": len(pages),
            })
        elif entry.is_file() and entry.suffix.lower() == ".html":
            title = _extract_title(entry)
            description = _extract_description(entry)
            year = _extract_year(entry)
            results.append({
                "name": entry.name,
                "title": title,
                "description": description,
                "year": year,
                "tags": TAG_MAP.get(entry.name, []),
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


def _extract_description(fpath):
    try:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<h1>(.*?)</h1>", content, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return ""


def _extract_year(fpath):
    try:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"来源[：:].*?·\s*(\d{4})", content)
        if m:
            return int(m.group(1))
        m = re.search(r"arxiv\.org/abs/(\d{2})\d{2}\.\d+", content)
        if m:
            return int(m.group(1)) + 2000
        m = re.search(r"arXiv:(\d{2})\d{2}\.\d+", content)
        if m:
            return int(m.group(1)) + 2000
    except Exception:
        pass
    return None


def main():
    data = scan_reports()
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Generated {OUTPUT_FILE} with {len(data)} reports")


if __name__ == "__main__":
    main()
