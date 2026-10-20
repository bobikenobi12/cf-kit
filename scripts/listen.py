#!/usr/bin/env python3
"""Receive problems from the Competitive Companion browser extension.

Start it once with `python3 scripts/listen.py` and leave it running. Then click the
Competitive Companion button on any Codeforces problem page. Each problem is saved to
contests/<contest>/<index>/ (gym problems go to contests/gym-<id>/<index>/):

    tests/N.in, tests/N.ans   the sample tests from the statement
    problem.json              name, url, limits (overwritten on every click)
    sol.cpp, brute.cpp, gen.py  copied from templates/ the first time only
"""
import json
import re
import shutil
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from common import ROOT

TEMPLATES = ROOT / "templates"
CONTESTS = ROOT / "contests"
PORT = 27121  # Competitive Companion's default port
TEMPLATE_FILES = ["sol.cpp", "brute.cpp", "gen.py"]

# Matches /contest/1234/problem/A, /problemset/problem/1234/A and /gym/100123/problem/B
URL_RE = re.compile(r"/(contest|gym|problemset/problem)/(\d+)(?:/problem)?/([A-Za-z0-9]+)")


def problem_dir(data):
    match = URL_RE.search(data.get("url", ""))
    if match:
        kind, number, index = match.groups()
        contest = f"gym-{number}" if kind == "gym" else number
        return CONTESTS / contest / index.upper()
    slug = re.sub(r"[^a-z0-9]+", "-", data.get("name", "").lower()).strip("-")
    return CONTESTS / "other" / (slug or "problem")


def with_newline(text):
    return text if text.endswith("\n") else text + "\n"


def save_problem(data):
    d = problem_dir(data)
    tests_dir = d / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    # Remove old numbered tests so a re-click doesn't leave stale ones behind.
    for old in tests_dir.iterdir():
        if re.fullmatch(r"\d+\.(in|ans)", old.name):
            old.unlink()
    tests = data.get("tests", [])
    for i, test in enumerate(tests, 1):
        (tests_dir / f"{i}.in").write_text(with_newline(test["input"]))
        (tests_dir / f"{i}.ans").write_text(with_newline(test["output"]))

    meta = {k: v for k, v in data.items() if k != "tests"}
    (d / "problem.json").write_text(json.dumps(meta, indent=2))

    for name in TEMPLATE_FILES:
        if not (d / name).exists():
            shutil.copy(TEMPLATES / name, d / name)
    return d, len(tests)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            data = json.loads(body)
            d, count = save_problem(data)
            note = "  (interactive: cannot be judged locally)" if data.get("interactive") else ""
            print(f"saved {data.get('name', '?')} -> {d.relative_to(ROOT)} ({count} tests){note}", flush=True)
            self.send_response(200)
        except Exception as exc:  # keep serving even if one problem fails
            print(f"error: {exc}", file=sys.stderr, flush=True)
            self.send_response(400)
        self.end_headers()

    def do_GET(self):  # lets you check in a browser that the listener is up
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"competitive companion listener is running\n")

    def log_message(self, *args):  # keep the console quiet
        pass


def main():
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        sys.exit(f"cannot listen on port {PORT}: {exc}. Is another listener already running?")
    print(f"listening on http://127.0.0.1:{PORT}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
