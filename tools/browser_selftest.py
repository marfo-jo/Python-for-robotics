"""Run tools/selftest.html in headless Chrome (or Edge) and print the results.

    python tools/browser_selftest.py              # all Module 0 lessons
    python tools/browser_selftest.py m00.l01      # one lesson
    python tools/browser_selftest.py --cv         # also check OpenCV loads

Serves the repo root on localhost (including the local, gitignored
verification/ folder, so reference solutions are checked in Pyodide too),
waits for the page to POST its report, then exits non-zero on failure.
No dependencies beyond the standard library and an installed browser.
"""
import functools
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser",
]
result = {}
done = threading.Event()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        if self.path != "/__selftest_result":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        result["text"] = self.rfile.read(length).decode("utf-8")
        self.send_response(204)
        self.end_headers()
        done.set()

    def log_message(self, *args):
        pass


def find_browser():
    for b in BROWSERS:
        if os.path.exists(b) or shutil.which(b):
            return b
    raise SystemExit("No Chrome/Edge/Chromium found.")


def main(argv):
    lesson = next((a for a in argv[1:] if not a.startswith("--")), None)
    query = "report=1" + (f"&lesson={lesson}" if lesson else "") + ("&cv=1" if "--cv" in argv else "")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/tools/selftest.html?{query}"
    profile = tempfile.mkdtemp(prefix="pfr-selftest-")
    proc = subprocess.Popen([find_browser(), "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--user-data-dir={profile}", url],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        finished = done.wait(timeout=float(os.environ.get("PFR_SELFTEST_TIMEOUT", "600")))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)
    if not finished:
        print("TIMEOUT: the self-test page never reported back.")
        return 3
    print(result["text"])
    return 0 if "SELFTEST PASS" in result["text"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
