#!/usr/bin/env python3
"""Local web server for browsing HTML reports with indexing."""

import argparse
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REPORTS_DIR = SCRIPT_DIR / "reports"
DEFAULT_PORT = 8080

cfg = type("Config", (), {"reports_dir": DEFAULT_REPORTS_DIR, "port": DEFAULT_PORT})()


def scan_reports():
    results = []
    for entry in sorted(cfg.reports_dir.iterdir()):
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


THEME_CSS = """
:root{
--bg:#0d1117;--card:#161b22;--p:#4f8af7;--pm:rgba(79,138,247,.12);--bd:rgba(79,138,247,.22);
--t:#e6edf3;--mt:#8b949e;--content-bg:#1a1a2e;
--font:'Source Sans 3','Noto Sans SC',system-ui,sans-serif}
"""


INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>HTML 报告浏览器</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
""" + THEME_CSS + """
html,body{height:100%;background:var(--bg);font-family:var(--font);color:var(--t)}
.wrap{max-width:900px;margin:0 auto;padding:40px 24px}
header{text-align:center;margin-bottom:40px}
header h1{font-size:28px;font-weight:700;color:var(--t);margin-bottom:8px}
header p{color:var(--mt);font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:20px;
cursor:pointer;transition:border-color .2s,transform .2s,background .2s}
.card:hover{border-color:var(--p);transform:translateY(-2px)}
.card .name{font-size:16px;font-weight:600;color:var(--p);margin-bottom:6px;word-break:break-all}
.card .title{font-size:13px;color:var(--mt);margin-bottom:12px;min-height:18px}
.card .meta{font-size:12px;color:var(--mt);display:flex;gap:12px}
.card .meta span{display:flex;align-items:center;gap:4px}
.badge{background:var(--pm);border:1px solid var(--bd);border-radius:6px;padding:2px 8px;
font-size:11px;color:var(--p)}
.empty{text-align:center;color:var(--mt);padding:80px 0;font-size:16px}
</style>
</head>
<body>
<div class="wrap">
<header>
<h1>HTML 报告浏览器</h1>
<p>自动索引报告</p>
</header>
<div class="grid" id="grid"></div>
<div class="empty" id="empty" style="display:none">未找到报告</div>
</div>
<script>
function renderReports(data){
  if(!data.length){document.getElementById('grid').style.display='none';
    document.getElementById('empty').style.display='block';return}
  document.getElementById('grid').style.display='grid';
  document.getElementById('empty').style.display='none';
  const g=document.getElementById('grid');g.innerHTML='';
  data.forEach(r=>{
    const c=document.createElement('div');c.className='card';
    c.onclick=()=>location.href='/view/'+r.name;
    c.innerHTML=`<div class="name">${r.name}</div>
<div class="title">${r.title||'无标题'}</div>
<div class="meta">
<span><span class="badge">${r.type==='single'?'单页':'目录'}</span></span>
<span><span class="badge">${r.page_count} 页</span></span>
${r.figures.length?`<span><span class="badge">${r.figures.length} 图</span></span>`:''}
</div>`;
    g.appendChild(c);
  });
}
fetch('/api/reports').then(r=>r.json()).then(renderReports);
</script>
</body>
</html>"""

VIEWER_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>报告查看器</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
""" + THEME_CSS + """
html,body{height:100%;background:var(--bg);font-family:var(--font);color:var(--t);overflow:hidden}
.app{display:flex;height:100vh}
.sidebar{width:220px;background:var(--card);border-right:1px solid var(--bd);display:flex;
flex-direction:column;overflow:hidden;flex-shrink:0}
.sidebar.hidden{display:none}
.sidebar-header{padding:16px;border-bottom:1px solid var(--bd)}
.sidebar-header h2{font-size:14px;color:var(--p);margin-bottom:4px;word-break:break-all}
.sidebar-header a{font-size:12px;color:var(--mt);text-decoration:none}
.sidebar-header a:hover{color:var(--p)}
.page-list{flex:1;overflow-y:auto;padding:8px}
.page-item{display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:8px;
cursor:pointer;font-size:13px;color:var(--mt);transition:background .15s,color .15s}
.page-item:hover{background:var(--pm);color:var(--t)}
.page-item.active{background:var(--pm);color:var(--p);border:1px solid var(--bd)}
.page-num{font-weight:600;font-size:11px;color:var(--p);min-width:24px}
.main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.toolbar{display:flex;align-items:center;gap:12px;padding:8px 16px;background:var(--card);
border-bottom:1px solid var(--bd);flex-shrink:0}
.toolbar .page-title{font-size:13px;color:var(--t);flex:1}
.toolbar button{background:var(--pm);border:1px solid var(--bd);color:var(--p);
padding:4px 10px;border-radius:6px;cursor:pointer;font-size:12px}
.toolbar button:hover{background:var(--bd)}
.toolbar .nav-group{display:flex;gap:4px}
.toolbar .nav-group.hidden{display:none}
.content{flex:1;display:flex;align-items:center;justify-content:center;overflow:auto;
background:var(--content-bg)}
iframe{border:none;flex-shrink:0}
iframe.fit{width:1017px;height:720px;transform-origin:center}
iframe.full{width:100%;height:100%}
.toolbar a{font-size:12px;color:var(--mt);text-decoration:none;flex-shrink:0}
.toolbar a:hover{color:var(--p)}
</style>
</head>
<body>
<div class="app">
<div class="sidebar" id="sidebar">
<div class="sidebar-header">
<h2 id="reportName"></h2>
<a href="/">返回索引</a>
</div>
<div class="page-list" id="pageList"></div>
</div>
<div class="main">
<div class="toolbar">
<a href="/" style="font-size:12px;color:var(--mt);text-decoration:none">索引</a>
<div class="nav-group" id="navGroup">
<button onclick="prevPage()">上一页</button>
<button onclick="nextPage()">下一页</button>
</div>
<div class="page-title" id="pageTitle"></div>
<button onclick="zoomFit()">适配</button>
<button onclick="zoom100()">100%</button>
</div>
<div class="content" id="content">
<iframe id="frame"></iframe>
</div>
</div>
</div>
<script>
const path=location.pathname.replace('/view/','');
let pages=[];let idx=0;let zoomMode='fit';let reportType='directory';
async function loadReport(){
  try{const r=await fetch('/api/reports');const data=await r.json();
    const report=data.find(d=>d.name===path);
    if(!report){document.getElementById('reportName').textContent='未找到';return}
    document.getElementById('reportName').textContent=report.name;
    pages=report.pages;reportType=report.type;
    if(reportType==='single'){
      document.getElementById('sidebar').classList.add('hidden');
      document.getElementById('navGroup').classList.add('hidden');
      document.getElementById('frame').classList.add('full');
      document.getElementById('frame').classList.remove('fit');
      document.getElementById('pageTitle').textContent=report.name;
      document.getElementById('frame').src='/file/'+path;
      return}
    if(idx>=pages.length)idx=0;
    document.getElementById('frame').classList.add('fit');
    document.getElementById('frame').classList.remove('full');
    renderPages();showPage(idx)}catch(e){console.error(e)}
}
function renderPages(){
  const list=document.getElementById('pageList');list.innerHTML='';
  pages.forEach((p,i)=>{
    const item=document.createElement('div');item.className='page-item'+(i===idx?' active':'');
    item.innerHTML=`<span class="page-num">P${i}</span><span>${p}</span>`;
    item.onclick=()=>{idx=i;renderPages();showPage(i)};
    list.appendChild(item);
  });
}
function showPage(i){
  const f=document.getElementById('frame');
  f.src=`/file/${path}/${pages[i]}`;
  document.getElementById('pageTitle').textContent=`P${i} (${i+1}/${pages.length})`;
  applyZoom();
}
function prevPage(){if(idx>0){idx--;renderPages();showPage(idx)}}
function nextPage(){if(idx<pages.length-1){idx++;renderPages();showPage(idx)}}
function applyZoom(){
  if(reportType==='single')return;
  const f=document.getElementById('frame');const c=document.getElementById('content');
  if(zoomMode==='fit'){
    const sx=c.clientWidth/1017;const sy=c.clientHeight/720;
    const s=Math.min(sx,sy,1.5);f.style.transform=`scale(${s})`}
  else{f.style.transform='scale(1)'}
}
function zoomFit(){zoomMode='fit';applyZoom()}
function zoom100(){zoomMode='100';applyZoom()}
document.addEventListener('keydown',e=>{
  if(reportType==='single')return;
  if(e.key==='ArrowLeft'||e.key==='ArrowUp')prevPage();
  if(e.key==='ArrowRight'||e.key==='ArrowDown')nextPage();
});
window.addEventListener('resize',()=>applyZoom());
loadReport();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        url = unquote(self.path)
        parsed = urlparse(url)
        path = parsed.path

        if path == "/" or path == "":
            self._send_html(INDEX_HTML)
        elif path.startswith("/view/"):
            self._send_html(VIEWER_HTML)
        elif path == "/api/reports":
            data = scan_reports()
            self._send_json(data)
        elif path.startswith("/file/"):
            rel = path[len("/file/"):]
            fpath = cfg.reports_dir / rel
            if fpath.is_file() and _is_safe(fpath):
                self._send_file(fpath)
            else:
                self._send_404()
        else:
            fpath = cfg.reports_dir / path.lstrip("/")
            if fpath.is_file() and _is_safe(fpath):
                self._send_file(fpath)
            else:
                self._send_404()

    def _send_html(self, content):
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, fpath):
        ext = fpath.suffix.lower()
        mime = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".webp": "image/webp",
        }.get(ext, "application/octet-stream")
        try:
            data = fpath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self._send_404()

    def _send_404(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"404 Not Found")


def _is_safe(fpath):
    try:
        fpath.resolve().relative_to(cfg.reports_dir.resolve())
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description="HTML Report Viewer Server")
    parser.add_argument("-d", "--dir", default=str(cfg.reports_dir),
                        help="Reports directory path (default: ./reports)")
    parser.add_argument("-p", "--port", type=int, default=cfg.port,
                        help=f"Server port (default: {cfg.port})")
    args = parser.parse_args()

    cfg.reports_dir = Path(args.dir).resolve()
    cfg.port = args.port

    if not cfg.reports_dir.is_dir():
        print(f"Error: Reports directory not found: {cfg.reports_dir}")
        return

    host = "localhost"
    server = HTTPServer((host, cfg.port), Handler)
    url = f"http://{host}:{cfg.port}"
    print(f"Report Viewer started at {url}")
    print(f"Serving reports from: {cfg.reports_dir}")
    print(f"Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()