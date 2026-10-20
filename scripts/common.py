"""Shared helpers for the CP scripts: compile, run, compare."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDE_DIR = ROOT / "include"
PCH = INCLUDE_DIR / "bits" / "stdc++.h.gch"

# Codeforces uses GNU C++ 17/20/23. gnu++20 is close enough to test with locally.
COMMON_FLAGS = ["-std=gnu++20", "-Wall", "-Wextra", "-Wshadow", "-DLOCAL"]
RELEASE_FLAGS = ["-O2"]
DEBUG_FLAGS = [
    "-O0", "-g",
    "-fsanitize=address,undefined", "-fno-sanitize-recover=all",  # abort on the first bug
    "-D_GLIBCXX_DEBUG",  # bounds-checked STL containers
]


def find_compiler(required=True):
    """Pick a GCC. Apple's /usr/bin/g++ is clang, which has no bits/stdc++.h, so skip it.

    With required=False, returns None instead of exiting when no GCC is found.
    """
    if os.environ.get("CP_CXX"):
        return os.environ["CP_CXX"]
    for name in ["g++-16", "g++-15", "g++-14", "g++-13", "g++"]:
        path = shutil.which(name)
        if not path:
            continue
        version = subprocess.run([path, "--version"], capture_output=True, text=True).stdout
        if "clang" not in version.lower():
            return path
    if not required:
        return None
    sys.exit("No GCC found. Install one (brew install gcc) or set CP_CXX to its path.")


def compile_cpp(src, debug=False):
    """Compile src into <src dir>/build/. Exits with the compiler output on error."""
    src = Path(src).resolve()
    if not src.exists():
        sys.exit(f"{src} does not exist")
    out_dir = src.parent / "build"
    out_dir.mkdir(exist_ok=True)
    exe = out_dir / (src.stem + ("-debug" if debug else ""))
    flags = COMMON_FLAGS + (DEBUG_FLAGS if debug else RELEASE_FLAGS)
    cmd = [find_compiler(), *flags, f"-I{INCLUDE_DIR}", str(src), "-o", str(exe)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stderr.strip():
        print(result.stderr, end="")  # errors or warnings
    if result.returncode != 0:
        sys.exit(f"compilation failed: {src.name}")
    return exe


def run_binary(exe, stdin_text, time_limit):
    """Run exe with stdin_text. Returns (status, stdout, stderr, seconds).

    status is "OK", "RE" (non-zero exit, e.g. a sanitizer abort) or "TLE".
    """
    start = time.perf_counter()
    try:
        result = subprocess.run([str(exe)], input=stdin_text.encode(),
                                capture_output=True, timeout=time_limit)
    except subprocess.TimeoutExpired:
        return "TLE", "", "", time_limit
    elapsed = time.perf_counter() - start
    out = result.stdout.decode(errors="replace")
    err = result.stderr.decode(errors="replace")
    status = "OK" if result.returncode == 0 else "RE"
    return status, out, err, elapsed


def tokens_equal(got, expected):
    """Compare whitespace-separated tokens. Floats match within 1e-6; integers must match exactly.

    Real Codeforces problems use a checker for their exact tolerance, so this is an approximation.
    """
    a, b = got.split(), expected.split()
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x == y:
            continue
        if not any(c in x + y for c in ".eE"):  # not a float, so no tolerance
            return False
        try:
            fx, fy = float(x), float(y)
        except ValueError:
            return False
        if abs(fx - fy) > 1e-6 * max(1.0, abs(fy)):
            return False
    return True


def load_time_limit(problem):
    """Time limit in seconds from problem.json (Competitive Companion stores it in ms)."""
    meta = problem / "problem.json"
    if meta.exists():
        ms = json.loads(meta.read_text()).get("timeLimit")
        if ms:
            return ms / 1000
    return 2.0
