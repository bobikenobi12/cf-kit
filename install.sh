#!/usr/bin/env bash
# cf-kit bootstrap. Fetches the repository, then starts the interactive installer.
#
#   curl -fsSL https://raw.githubusercontent.com/bobikenobi12/cf-kit/main/install.sh | bash
#
# Environment overrides:
#   CF_KIT_DIR   where to clone (default: $HOME/cf-kit)
#   CF_KIT_REPO  git URL to clone (default: the public GitHub repository)
# Extra arguments are passed to setup/install.py, e.g.  bash install.sh --yes
set -euo pipefail

REPO_URL="${CF_KIT_REPO:-https://github.com/bobikenobi12/cf-kit.git}"
TARGET="${CF_KIT_DIR:-$HOME/cf-kit}"

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || die "python3 is required. Install Python 3.9+ and try again."
command -v git >/dev/null 2>&1 || die "git is required. On macOS run: xcode-select --install"

# Running from an existing checkout (./install.sh): use it instead of cloning again.
SELF="${BASH_SOURCE[0]:-}"
if [[ -n "$SELF" && -f "$SELF" && -f "$(dirname "$SELF")/setup/install.py" ]]; then
    TARGET="$(cd "$(dirname "$SELF")" && pwd)"
    say "Using existing checkout at $TARGET"
elif [[ -d "$TARGET/.git" ]]; then
    say "Updating $TARGET"
    git -C "$TARGET" pull --ff-only --quiet || die "could not update $TARGET (local changes?). Fix it or set CF_KIT_DIR."
else
    say "Downloading cf-kit to $TARGET"
    git clone --depth 1 --quiet "$REPO_URL" "$TARGET" || die "could not clone $REPO_URL"
fi

cd "$TARGET"
# When piped (curl | bash) stdin is the script, so read answers from the terminal.
# Opening /dev/tty is the only reliable test: -r passes even with no terminal attached.
if [[ -t 0 ]]; then
    python3 setup/install.py "$@"
elif { : </dev/tty; } 2>/dev/null; then
    python3 setup/install.py "$@" </dev/tty
else
    python3 setup/install.py --yes "$@"
fi
