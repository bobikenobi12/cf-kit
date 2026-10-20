#!/usr/bin/env python3
"""Build the precompiled <bits/stdc++.h> (include/bits/stdc++.h.gch).

Run once after setup, and again if you change compiler. It takes a few seconds
and makes every later compile of #include <bits/stdc++.h> much faster.
The flags must match the ones judge.py uses for release builds, or GCC ignores the file.
"""
import subprocess
import sys

from common import COMMON_FLAGS, INCLUDE_DIR, PCH, RELEASE_FLAGS, find_compiler


def main():
    compiler = find_compiler()
    header = INCLUDE_DIR / "bits" / "stdc++.h"
    cmd = [compiler, *COMMON_FLAGS, *RELEASE_FLAGS, "-x", "c++-header", str(header), "-o", str(PCH)]
    print(f"building {PCH.relative_to(PCH.parents[2])} with {compiler} ...", flush=True)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit("precompiled header build failed")
    print(f"done ({PCH.stat().st_size // 2**20} MB)")


if __name__ == "__main__":
    main()
