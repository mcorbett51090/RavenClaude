#!/usr/bin/env bash
# setup-worktree-hygiene.sh — idempotent worktree-hygiene provisioning.
#
# Wires the machine-level conveniences that make one-session-one-worktree the path
# of least resistance. Every step is idempotent — a second run makes NO change and
# adds NO duplicate shell-rc block.
#
#   1. git rebase-on-pull defaults (global):  pull.rebase=true, rebase.autoStash=true
#   2. install `rcwt` -> ~/.local/bin/rcwt    (install -m 755, only when content differs)
#   3. ensure ~/.local/bin is on PATH         (marker-bounded block in ~/.bashrc + ~/.zshrc,
#                                              mirroring .devcontainer/post-create.sh's idiom)
#   4. --with-git-hook (OPT-IN, HIGH BLAST):  install the Layer-3 global chain-through
#                                              pre-commit + git config --global core.hooksPath
#
# The --with-git-hook step is deliberately opt-in: setting a global core.hooksPath
# touches every repo's git-hook resolution (it can shadow Husky/lefthook), so it is
# never done by default. A repo that sets its OWN core.hooksPath still wins (git
# precedence) — the chain-through hook documents that.
#
# Usage:
#   scripts/setup-worktree-hygiene.sh                 # steps 1-3 (safe defaults)
#   scripts/setup-worktree-hygiene.sh --with-git-hook # + step 4 (global git hook)
#
# Portability: set -euo pipefail. macOS bash 3.2 / BSD-safe (no declare -A /
# mapfile / grep -P / timeout(1) / sed -i / ${x^^} / globstar).

set -euo pipefail

WITH_GIT_HOOK=0
for arg in "$@"; do
  case "$arg" in
    --with-git-hook) WITH_GIT_HOOK=1 ;;
    -h|--help)
      sed -n '2,20p' "${BASH_SOURCE[0]:-$0}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "setup-worktree-hygiene.sh: unknown argument '$arg' (try --with-git-hook or --help)" >&2
      exit 2
      ;;
  esac
done

log() { printf '[worktree-hygiene] %s\n' "$*"; }

# Resolve the repo root from this script's own location (scripts/ lives at <repo>/scripts/),
# so rcwt + the hook template are found no matter where the script is invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RCWT_SRC="$REPO_ROOT/plugins/ravenclaude-core/bin/rcwt"
HOOK_TEMPLATE="$REPO_ROOT/plugins/ravenclaude-core/templates/git-hooks-global/pre-commit"

BIN_DIR="$HOME/.local/bin"

# ── 1. git rebase-on-pull defaults (global) ───────────────────────────────────
if command -v git >/dev/null 2>&1; then
  log "Setting git rebase-on-pull defaults (global)..."
  git config --global pull.rebase true
  git config --global rebase.autoStash true
  log "  pull.rebase=true, rebase.autoStash=true"
else
  log "SKIP: git not found — cannot set rebase defaults."
fi

# ── 2. install rcwt -> ~/.local/bin/rcwt (only when content differs) ──────────
log "Installing rcwt -> $BIN_DIR/rcwt..."
mkdir -p "$BIN_DIR"
rcwt_dest="$BIN_DIR/rcwt"
if [ ! -f "$RCWT_SRC" ]; then
  log "  SKIP: rcwt source not found at $RCWT_SRC"
elif [ -f "$rcwt_dest" ] && cmp -s "$RCWT_SRC" "$rcwt_dest"; then
  log "  already current (no change)"
else
  install -m 755 "$RCWT_SRC" "$rcwt_dest"
  log "  installed"
fi

# ── 3. ensure ~/.local/bin on PATH via a marker-bounded shell-rc block ────────
# Same marker-bounded idiom as .devcontainer/post-create.sh's autostart block:
# append exactly once, guarded by the BEGIN marker; the block's own `case` guard
# makes the PATH edit idempotent at shell-eval time too. Both bash and zsh rc
# files get it so the PATH works whichever login shell the user runs.
PATH_BEGIN="# >>> ravenclaude ~/.local/bin PATH >>>"
PATH_END="# <<< ravenclaude ~/.local/bin PATH <<<"

ensure_path_block() {
  rc="$1"
  if [ -f "$rc" ] && grep -qF "$PATH_BEGIN" "$rc" 2>/dev/null; then
    log "  PATH block already present in $rc"
    return 0
  fi
  # `>>` creates the file if absent; the block is POSIX-sh (works in bash + zsh).
  cat >> "$rc" <<EOF

$PATH_BEGIN
# Ensure ~/.local/bin (where 'rcwt' installs) is on PATH. Idempotent.
case ":\$PATH:" in
  *":\$HOME/.local/bin:"*) ;;
  *) export PATH="\$HOME/.local/bin:\$PATH" ;;
esac
$PATH_END
EOF
  log "  added ~/.local/bin PATH block to $rc"
}

log "Ensuring ~/.local/bin is on PATH..."
ensure_path_block "$HOME/.bashrc"
ensure_path_block "$HOME/.zshrc"

# ── 4. --with-git-hook (OPT-IN): global chain-through pre-commit + hooksPath ───
if [ "$WITH_GIT_HOOK" -eq 1 ]; then
  log "Installing GLOBAL chain-through git pre-commit (--with-git-hook)..."
  if ! command -v git >/dev/null 2>&1; then
    log "  SKIP: git not found."
  elif [ ! -f "$HOOK_TEMPLATE" ]; then
    log "  SKIP: hook template not found at $HOOK_TEMPLATE"
  else
    HOOKS_DIR="$HOME/.config/git/hooks"
    mkdir -p "$HOOKS_DIR"
    hook_dest="$HOOKS_DIR/pre-commit"
    if [ -f "$hook_dest" ] && cmp -s "$HOOK_TEMPLATE" "$hook_dest"; then
      log "  global pre-commit already current (no change)"
    else
      install -m 755 "$HOOK_TEMPLATE" "$hook_dest"
      log "  installed chain-through pre-commit -> $hook_dest"
    fi
    git config --global core.hooksPath "$HOOKS_DIR"
    log "  git config --global core.hooksPath=$HOOKS_DIR"
    log "  NOTE: a repo that sets its OWN core.hooksPath still wins (git precedence);"
    log "        the chain-through hook execs a project's .git/hooks/pre-commit first."
  fi
else
  log "Skipping global git hook (pass --with-git-hook to install it — opt-in, high-blast)."
fi

log "Done."
