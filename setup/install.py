#!/usr/bin/env python3
"""cf-kit installer: answer a few questions, and everything is set up.

usage: python3 setup/install.py [--yes] [--skip-editors]

  --yes           accept every default without asking (also used when there is no terminal)
  --skip-editors  don't touch VS Code or Sublime Text

It checks the compiler, configures the editors you pick, builds the precompiled header,
and finishes with the doctor report. Safe to run again.
"""
import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import find_compiler  # noqa: E402

COMPANION_PAGE = "https://github.com/jmerle/competitive-companion"
VSCODE_EXTENSIONS = ["vscodevim.vim", "ms-vscode.cpptools"]

USE_COLOR = sys.stdout.isatty()


def paint(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def step(number, title):
    print(f"\n{paint('1;34', f'[{number}]')} {paint('1', title)}")


def ok(message):
    print(f"    {paint('32', '✓')} {message}")


def warn(message):
    print(f"    {paint('33', '!')} {message}")


def info(message):
    print(f"    {paint('2', message)}")


class Prompter:
    """Asks questions on the terminal, or quietly takes the default when not interactive."""

    def __init__(self, assume_yes):
        self.interactive = sys.stdin.isatty() and not assume_yes

    def yes(self, question, default=True):
        if not self.interactive:
            return default
        hint = "[Y/n]" if default else "[y/N]"
        answer = input(f"    {question} {hint} ").strip().lower()
        if not answer:
            return default
        return answer in ("y", "yes")


def check_python():
    if sys.version_info < (3, 9):
        sys.exit("cf-kit needs Python 3.9 or newer.")


def setup_compiler(prompt):
    step(1, "Compiler")
    compiler = find_compiler(required=False)
    if compiler:
        ok(f"GCC found: {compiler}")
        return compiler

    warn("No GCC found. Apple's clang has no bits/stdc++.h, so cf-kit needs GCC.")
    brew = shutil.which("brew")
    if sys.platform == "darwin" and brew and prompt.yes("Install GCC with Homebrew now? (a few minutes)"):
        subprocess.run([brew, "install", "gcc"], check=False)
        compiler = find_compiler(required=False)
    elif sys.platform == "darwin":
        info("Install it with: brew install gcc")
    else:
        info("Install it with: sudo apt install g++   (or: sudo dnf install gcc-c++)")

    if not compiler:
        sys.exit("GCC is still missing. Install it, then run this installer again.")
    ok(f"GCC ready: {compiler}")
    return compiler


def intellisense_mode():
    os_name = "macos" if sys.platform == "darwin" else "linux"
    arch = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"
    return f"{os_name}-gcc-{arch}"


def find_code_cli():
    if shutil.which("code"):
        return shutil.which("code")
    app_cli = Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code")
    return str(app_cli) if app_cli.exists() else None


def setup_vscode(prompt, compiler):
    code = find_code_cli()
    if not prompt.yes("Set up VS Code (Vim keys, C/C++ IntelliSense)?"):
        info("Skipped VS Code.")
        return
    if code and prompt.yes(f"Install the recommended extensions ({', '.join(VSCODE_EXTENSIONS)})?"):
        for ext in VSCODE_EXTENSIONS:
            subprocess.run([code, "--install-extension", ext, "--force"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        ok("VS Code extensions installed")
    elif not code:
        info("VS Code's `code` command was not found. Open the folder in VS Code and accept")
        info("the recommended extensions when prompted (Vim, C/C++).")

    config = {
        "version": 4,
        "configurations": [{
            "name": "cf-kit",
            "compilerPath": compiler,
            "cppStandard": "gnu++20",
            "intelliSenseMode": intellisense_mode(),
            "includePath": ["${workspaceFolder}/include", "${default}"],
            "defines": ["LOCAL"],
        }],
    }
    (ROOT / ".vscode" / "c_cpp_properties.json").write_text(json.dumps(config, indent=4) + "\n")
    ok(f"IntelliSense configured for {compiler}")


def sublime_user_dir():
    if sys.platform == "darwin":
        base = Path.home() / "Library/Application Support/Sublime Text"
    else:
        base = Path.home() / ".config/sublime-text"
    return base, base / "Packages/User"


def write_build_system(user):
    judge = str(SCRIPTS / "judge.py")
    build = {
        "cmd": [sys.executable, judge, "$file"],
        "working_dir": "$file_path",
        "selector": "source.c++",
        "file_regex": r"^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
        "variants": [
            {"name": "Debug (sanitizers + bounds checks)",
             "cmd": [sys.executable, judge, "$file", "--debug"]},
        ],
    }
    (user / "CF-C++.sublime-build").write_text(json.dumps(build, indent=4) + "\n")


def write_snippets(user):
    snippets = json.loads((ROOT / ".vscode" / "cpp.code-snippets").read_text())
    for name, spec in snippets.items():
        body = spec["body"] if isinstance(spec["body"], str) else "\n".join(spec["body"])
        xml = (
            "<snippet>\n"
            f"    <content><![CDATA[\n{body}\n]]></content>\n"
            f"    <tabTrigger>{spec['prefix']}</tabTrigger>\n"
            "    <scope>source.c++</scope>\n"
            f"    <description>{name}</description>\n"
            "</snippet>\n"
        )
        (user / f"cp-{spec['prefix']}.sublime-snippet").write_text(xml)
    return len(snippets)


def write_preferences(user):
    """Enable Vintage by clearing ignored_packages. Keeps other settings; backs up unreadable files."""
    prefs = user / "Preferences.sublime-settings"
    data = {}
    if prefs.exists():
        try:
            data = json.loads(prefs.read_text())
        except json.JSONDecodeError:
            # Sublime files may contain comments, which json can't read. Keep a copy and start fresh.
            shutil.copy(prefs, user / "Preferences.sublime-settings.bak")
            warn("Preferences had comments; saved a copy as Preferences.sublime-settings.bak")
            data = {}
    data["ignored_packages"] = []
    prefs.write_text(json.dumps(data, indent=4) + "\n")


def setup_sublime(prompt):
    base, user = sublime_user_dir()
    if not base.exists():
        info("Sublime Text not found; skipping.")
        return
    if not prompt.yes("Set up Sublime Text (CF-C++ build, snippets, Vim mode)?"):
        info("Skipped Sublime Text.")
        return
    user.mkdir(parents=True, exist_ok=True)
    write_build_system(user)
    count = write_snippets(user)
    write_preferences(user)
    ok(f"Sublime: CF-C++ build system, {count} snippets, Vim mode enabled")


def setup_editors(prompt, compiler, skip):
    step(2, "Editors")
    if skip:
        info("Skipped (--skip-editors).")
        return
    setup_vscode(prompt, compiler)
    setup_sublime(prompt)


def build_pch():
    step(3, "Precompiled header")
    info("Building include/bits/stdc++.h.gch (a few seconds)...")
    result = subprocess.run([sys.executable, str(SCRIPTS / "pch.py")], capture_output=True, text=True)
    if result.returncode == 0:
        ok("Built. Compiles will be faster.")
    else:
        warn("Could not build it; compiles still work, just slower.")
        info(result.stderr.strip()[-400:])


def companion_step():
    step(4, "Browser extension")
    print("    Install Competitive Companion in your browser to import problems with one click.")
    print(f"    Details and store links: {COMPANION_PAGE}")


def run_doctor():
    step(5, "Checking everything")
    subprocess.run([sys.executable, str(SCRIPTS / "doctor.py")], check=False)


def next_steps():
    print(f"\n{paint('1', 'Done.')} Try the example:")
    print("    python3 scripts/judge.py examples/sum-of-two/sol.cpp")
    print("\nFor a real contest:")
    print("    python3 scripts/listen.py        # leave it running, then click Competitive Companion")
    print("    Guide: docs/guide.html (or docs/cf-kit-guide.pdf)\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yes", action="store_true", help="accept all defaults")
    parser.add_argument("--skip-editors", action="store_true", help="don't configure editors")
    args = parser.parse_args()

    sys.stdout.reconfigure(line_buffering=True)  # keep output in order with subprocesses
    print(paint("1", "cf-kit setup"))
    check_python()
    prompt = Prompter(args.yes)
    try:
        compiler = setup_compiler(prompt)
        setup_editors(prompt, compiler, args.skip_editors)
        build_pch()
        companion_step()
        run_doctor()
        next_steps()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled. Run the installer again any time; it is safe to repeat.")
        sys.exit(130)


if __name__ == "__main__":
    main()
