#!/usr/bin/env python3
"""Check that cf-kit works on this machine, and say how to fix whatever doesn't.

usage: python3 scripts/doctor.py

Exit code is 0 when nothing essential is broken. Warnings are optional extras.
"""
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

from common import INCLUDE_DIR, PCH, ROOT, find_compiler

PORT = 27121
EXAMPLE = ROOT / "examples" / "sum-of-two" / "sol.cpp"

failures = 0


def report(ok_, label, fix=""):
    global failures
    if ok_ is True:
        print(f"  \033[32m✓\033[0m {label}")
    elif ok_ is None:
        print(f"  \033[33m!\033[0m {label}" + (f"\n      {fix}" if fix else ""))
    else:
        failures += 1
        print(f"  \033[31m✗\033[0m {label}" + (f"\n      fix: {fix}" if fix else ""))


def check_python():
    v = sys.version_info
    report(v >= (3, 9), f"Python {v.major}.{v.minor}", "install Python 3.9 or newer")


def check_compiler():
    compiler = find_compiler(required=False)
    if not compiler:
        report(False, "GCC not found", "brew install gcc   (Linux: sudo apt install g++)")
        return
    version = subprocess.run([compiler, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    report(True, f"GCC: {version}")

    # A real compile of a program that includes bits/stdc++.h, the same way judge.py does.
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "probe.cpp"
        src.write_text("#include <bits/stdc++.h>\nint main() { std::cout << 42 << '\\n'; }\n")
        result = subprocess.run([compiler, "-std=gnu++20", f"-I{INCLUDE_DIR}", str(src),
                                 "-o", str(Path(tmp) / "probe")], capture_output=True, text=True)
        report(result.returncode == 0, "compiles bits/stdc++.h programs",
               "the compiler is missing the standard headers; reinstall GCC or set CP_CXX")


def check_pch():
    if PCH.exists():
        report(True, f"precompiled header built ({PCH.stat().st_size // 2**20} MB)")
    else:
        report(None, "precompiled header not built (compiles work, just slower)",
               "python3 scripts/pch.py")


def check_port():
    try:
        with socket.socket() as s:
            s.bind(("127.0.0.1", PORT))
        report(True, f"port {PORT} is free for the Competitive Companion listener")
    except OSError:
        report(None, f"port {PORT} is in use",
               "fine if scripts/listen.py is already running; otherwise another program holds it")


def check_editors():
    code = shutil.which("code") or ""
    report(None if not code else True,
           "VS Code `code` command" + (f": {code}" if code else " not on PATH (optional)"),
           "in VS Code run: Shell Command: Install 'code' command in PATH" if not code else "")
    sublime = Path.home() / "Library/Application Support/Sublime Text"
    if sys.platform != "darwin":
        sublime = Path.home() / ".config/sublime-text"
    report(None if not sublime.exists() else True,
           "Sublime Text installed" if sublime.exists() else "Sublime Text not found (optional)")


def check_example():
    if not EXAMPLE.exists():
        report(False, "example problem is missing", "re-clone the repository")
        return
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "judge.py"), str(EXAMPLE)],
                            capture_output=True, text=True)
    report(result.returncode == 0, "example problem passes its samples",
           "run: python3 scripts/judge.py examples/sum-of-two/sol.cpp   and read the output")


def main():
    print("cf-kit doctor\n")
    check_python()
    check_compiler()
    check_pch()
    check_port()
    check_editors()
    check_example()
    print()
    if failures:
        print(f"{failures} problem(s) need fixing. Details above.")
        sys.exit(1)
    print("All essential checks passed.")


if __name__ == "__main__":
    main()
