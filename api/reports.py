from http.server import BaseHTTPRequestHandler
import json
import re
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def scan_reports():
    results = []
    if not REPORTS_DIR.is_dir():
        return results
    for entry in sorted(REPORTS_DIR.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            pages = sorted(
                [f.name for f in entry.iterdir() if f.is_file() and re.match(r"p\d+\.html$", f.name)]
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


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = scan_reports()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
