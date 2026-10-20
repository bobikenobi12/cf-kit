#!/usr/bin/env python3
"""Compile a solution and check it against the tests saved for its problem.

usage: judge.py [solution.cpp] [--debug]

Tests live in <problem dir>/tests/N.in with answers in N.ans. listen.py writes them
from Competitive Companion; you can also add files by hand.
--debug builds with AddressSanitizer, UBSan and _GLIBCXX_DEBUG, so out-of-bounds
accesses and overflows stop the program with a message instead of passing silently.
"""
import argparse
import difflib
import sys
from pathlib import Path

from common import compile_cpp, load_time_limit, run_binary, tokens_equal


def show_diff(expected, got, max_lines=20):
    diff = difflib.unified_diff(expected.splitlines(), got.splitlines(),
                                "expected", "got", lineterm="", n=1)
    for i, line in enumerate(diff):
        if i == max_lines:
            print("     ...")
            break
        print("     " + line)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", default="sol.cpp")
    parser.add_argument("--debug", action="store_true", help="sanitizers + bounds checks")
    args = parser.parse_args()

    src = Path(args.source).resolve()
    problem = src.parent
    tests = sorted((problem / "tests").glob("*.in"), key=lambda p: (len(p.stem), p.stem))
    if not tests:
        sys.exit(f"no tests in {problem / 'tests'}. Run scripts/listen.py or add N.in / N.ans by hand.")

    exe = compile_cpp(src, debug=args.debug)
    limit = load_time_limit(problem)
    print(f"{src.name}{' (debug)' if args.debug else ''}, time limit {limit:g}s")

    passed = 0
    for inp in tests:
        ans = inp.with_suffix(".ans")
        if not ans.exists():
            print(f"test {inp.stem}: no {ans.name}, skipped")
            continue
        status, out, err, secs = run_binary(exe, inp.read_text(), limit)
        if status == "OK" and not tokens_equal(out, ans.read_text()):
            status = "WA"
        print(f"test {inp.stem:>3}  {status:<3}  {secs * 1000:7.0f} ms")

        if status == "OK":
            passed += 1
        elif status == "WA":
            show_diff(ans.read_text(), out)
        elif status == "RE":
            print("     " + err[-1500:].replace("\n", "\n     "))
        # TLE: nothing more to show

    print(f"\npassed {passed}/{len(tests)}")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()
