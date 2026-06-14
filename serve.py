#!/usr/bin/env python3
"""Local static server for browsing HTML reports. Run: python serve.py"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = SCRIPT_DIR / "build.py"
PORT = 8080

subprocess.run([sys.executable, str(BUILD_SCRIPT)], check=True)

print(f"\nServing at http://localhost:{PORT}")
print("Press Ctrl+C to stop")
subprocess.run([sys.executable, "-m", "http.server", str(PORT), "--directory", str(SCRIPT_DIR)])
