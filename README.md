# cf-kit

A C++ workspace for Codeforces. Import problems from your browser with one click, run the samples with a key press, and stress test your solution against a brute force.

Read the **[guide](docs/index.html)** ([PDF](docs/cf-kit-guide.pdf)) for how it works and why.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/bobikenobi12/cf-kit/main/install.sh | bash
```

You need `git`, Python 3.9+ and GCC. The installer asks a few yes/no questions. Use `--yes` to accept every default, or `--skip-editors` to leave VS Code and Sublime Text alone.

Then install the [Competitive Companion](https://github.com/jmerle/competitive-companion) browser extension and run `python3 scripts/listen.py`.

## Try it

```sh
python3 scripts/judge.py examples/sum-of-two/sol.cpp      # run the samples
python3 scripts/stress.py examples/sum-of-two -n 200      # random tests against a brute force
python3 scripts/doctor.py                                 # check the setup
```

## Platforms

- **macOS** (Apple Silicon, Homebrew GCC): tested.
- **Linux**: not tested yet.

Apple's `g++` is clang and has no `bits/stdc++.h`, so cf-kit uses GCC. Set `CP_CXX` to choose a specific compiler.

## Contributing

Run `python3 scripts/doctor.py` and the commands above before opening a pull request. Your problems under `contests/` stay local and are not tracked.

## License

MIT. See [LICENSE](LICENSE).
