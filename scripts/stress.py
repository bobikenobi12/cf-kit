#!/usr/bin/env python3
"""Random stress test: compare sol.cpp with brute.cpp on inputs from gen.py.

usage: stress.py [problem dir] [-n COUNT] [--debug]

Runs `python3 gen.py <seed>` for seeds 1..COUNT, feeds each input to both programs,
and stops at the first mismatch. The failing input is saved to stress_fail/input.txt.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from common import compile_cpp, run_binary, tokens_equal

STRESS_TIME_LIMIT = 10  # seconds per run; a brute force can be slow on purpose


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("problem", nargs="?", default=".", help="directory with sol.cpp, brute.cpp, gen.py")
    parser.add_argument("-n", type=int, default=500, help="number of random tests")
    parser.add_argument("--debug", action="store_true", help="build sol.cpp with sanitizers")
    args = parser.parse_args()

    problem = Path(args.problem).resolve()
    gen = problem / "gen.py"
    if not gen.exists():
        sys.exit(f"{gen} not found")

    sol = compile_cpp(problem / "sol.cpp", debug=args.debug)
    brute = compile_cpp(problem / "brute.cpp")

    for seed in range(1, args.n + 1):
        gen_run = subprocess.run([sys.executable, str(gen), str(seed)], capture_output=True, text=True)
        if gen_run.returncode != 0:
            sys.exit(f"gen.py failed on seed {seed}:\n{gen_run.stderr}")
        test = gen_run.stdout

        b_status, expected, b_err, _ = run_binary(brute, test, STRESS_TIME_LIMIT)
        if b_status != "OK":
            sys.exit(f"brute.cpp {b_status} on seed {seed}:\n{b_err[-1500:]}")

        s_status, got, s_err, _ = run_binary(sol, test, STRESS_TIME_LIMIT)
        if s_status != "OK" or not tokens_equal(got, expected):
            fail_dir = problem / "stress_fail"
            fail_dir.mkdir(exist_ok=True)
            (fail_dir / "input.txt").write_text(test)
            print(f"seed {seed}: sol {s_status}")
            print(f"input:\n{test.rstrip()}")
            print(f"expected:\n{expected.rstrip()}")
            print(f"got:\n{got.rstrip()}")
            if s_err:
                print(s_err[-1500:])
            print(f"\nfailing input saved to {fail_dir / 'input.txt'}")
            sys.exit(1)

        if seed % 100 == 0:
            print(f"{seed}/{args.n} ok", flush=True)

    print(f"all {args.n} random tests match")


if __name__ == "__main__":
    main()
