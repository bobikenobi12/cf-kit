# cf-kit

A ready-to-use C++ workspace for Codeforces. Problems import from your browser with one click, your editor runs the samples with a key press, and stress tests check your solution against a brute force.

**Docs:** [docs/index.html](docs/index.html) · **Guide (PDF):** [docs/cf-kit-guide.pdf](docs/cf-kit-guide.pdf)

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/bobikenobi12/cf-kit/main/install.sh | bash
```

You need `git`, Python 3.9+ and GCC. The installer asks a few yes/no questions and checks the rest. Options: `--yes` accepts every default, `--skip-editors` leaves VS Code and Sublime alone.

Then install the **Competitive Companion** browser extension and run `python3 scripts/listen.py`. Click the extension on a problem, and its folder appears in `contests/`.

## Try it without a contest

```sh
python3 scripts/judge.py examples/sum-of-two/sol.cpp      # run the samples
python3 scripts/stress.py examples/sum-of-two -n 200      # random tests vs brute force
python3 scripts/doctor.py                                 # check the setup
```

## Platforms

| Platform | Status |
| --- | --- |
| macOS (Apple Silicon, Homebrew GCC) | Tested |
| Linux (GCC from your package manager) | Best effort, tested in CI |

Apple's `g++` is clang and has no `bits/stdc++.h`, so cf-kit uses GCC. Set `CP_CXX` to choose a specific compiler.

## Contributing

Run `python3 scripts/doctor.py` and the example commands above before opening a pull request. Problem folders under `contests/` stay local and are not tracked.

## License

MIT. See [LICENSE](LICENSE).
