#!/usr/bin/env bash
# RavenClaude + GitHub Copilot CLI — Codespace auto-setup (consumer-side).
#
# Drop this file (plus the sibling devcontainer.json) into a consumer repo's
# .devcontainer/ — either with `ravenclaude init-codespace` or by hand (see
# README.md in templates/codespace-copilot/). It runs automatically when the
# Codespace is built or rebuilt and leaves the repo fully wired for GitHub
# Copilot CLI, with no commands to type:
#   - installs prerequisites (Node 22+, git-lfs) on Debian-family images if missing,
#   - installs the Copilot CLI if missing (needs Node 22+),
#   - clones the RavenClaude marketplace once,
#   - wires skills + enforcement hooks + MCP into this repo,
#   - seeds + applies a balanced comfort-posture,
#   - adds an `rc` alias so launching Copilot is one word.
#
# Override the clone location / source repo with RAVENCLAUDE_DIR / RAVENCLAUDE_REPO
# (e.g. if you forked the marketplace).
set -euo pipefail
log() { printf '\n[ravenclaude] %s\n' "$*"; }

RC_DIR="${RAVENCLAUDE_DIR:-$HOME/RavenClaude}"
RC_REPO="${RAVENCLAUDE_REPO:-mcorbett51090/RavenClaude}"

# Choose a privilege-escalation prefix once: empty for root, `sudo` for the
# common Codespace `codespace`/`vscode` user. apt-get and a system-wide
# `npm install -g` both need it on the Python/Node/etc. devcontainer images
# that ship without writable /usr/lib/node_modules for the default user.
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  fi
fi

# 1a. Node 22+ — Copilot CLI requires it. If absent (some devcontainer images
#     ship Python or Java only), install LTS via the NodeSource script. On a
#     non-Debian image we just warn; the user can add Node to their image.
node_major() { node --version 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/'; }
if command -v node >/dev/null 2>&1 && [ "$(node_major)" -ge 22 ] 2>/dev/null; then
  log "Node present: $(node --version)"
else
  log "Node 22+ missing — installing via NodeSource LTS..."
  if command -v apt-get >/dev/null 2>&1 && command -v curl >/dev/null 2>&1; then
    if curl -fsSL https://deb.nodesource.com/setup_lts.x | $SUDO -E bash - >/dev/null 2>&1 \
       && $SUDO apt-get install -y nodejs >/dev/null 2>&1; then
      log "  installed Node $(node --version)"
    else
      log "  WARN: NodeSource install failed — install Node 22+ manually and rerun this script."
    fi
  else
    log "  WARN: non-Debian image (no apt-get) — install Node 22+ for your distro and rerun."
  fi
fi

# 1b. git-lfs — common-enough prerequisite (any consumer repo with LFS-tracked
#     assets will fail `git push` without it). Cheap to install; quiet on
#     non-Debian images.
if command -v git-lfs >/dev/null 2>&1; then
  log "git-lfs present: $(git-lfs version 2>/dev/null | head -n1)"
else
  log "git-lfs missing — installing..."
  if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get install -y git-lfs >/dev/null 2>&1 \
      && git lfs install --skip-repo >/dev/null 2>&1 \
      && log "  installed" \
      || log "  WARN: could not install git-lfs — run '$SUDO apt-get install -y git-lfs' yourself if you need it."
  else
    log "  WARN: non-Debian image — install git-lfs for your distro if you need it."
  fi
fi

# 2. GitHub Copilot CLI (needs Node 22+). Try the unprivileged install first,
#    then fall back to sudo (the typical case on a non-template image where
#    /usr/lib/node_modules isn't writable for the default user).
if command -v copilot >/dev/null 2>&1; then
  log "GitHub Copilot CLI present: $(copilot --version 2>/dev/null || echo '?')"
else
  log "Installing GitHub Copilot CLI (npm install -g @github/copilot)..."
  if npm install -g @github/copilot >/dev/null 2>&1; then
    log "  installed"
  elif [ -n "$SUDO" ] && $SUDO npm install -g @github/copilot >/dev/null 2>&1; then
    log "  installed (via sudo — global npm dir wasn't writable for the default user)"
  else
    log "  WARN: could not install automatically — run '$SUDO npm install -g @github/copilot' (needs Node 22+)."
  fi
fi

# 3. Clone the RavenClaude marketplace if we don't already have it (uses gh auth).
if [ -d "$RC_DIR/.git" ]; then
  log "RavenClaude marketplace already present at $RC_DIR"
else
  log "Cloning RavenClaude marketplace ($RC_REPO) -> $RC_DIR ..."
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh repo clone "$RC_REPO" "$RC_DIR" >/dev/null 2>&1 \
      || git clone "https://github.com/$RC_REPO.git" "$RC_DIR"
  elif ! git clone "https://github.com/$RC_REPO.git" "$RC_DIR"; then
    log "ERROR: could not clone $RC_REPO (private repo? run 'gh auth login' and rebuild the Codespace)."
    exit 0 # degrade gracefully — don't fail the whole Codespace build
  fi
fi

# 4. One-shot wire-up of THIS repo (skills + hooks + MCP + posture + rc alias).
log "Wiring this repo for Copilot (skills + hooks + MCP + posture + alias)..."
bash "$RC_DIR/scripts/ravenclaude" setup --project "$PWD"

# 5. Terminal status indicators — VS Code tab 🔔 + chime + idle-watcher so parallel
#    agent terminals announce when they need input. Idempotent; non-fatal.
TI_SETUP="$RC_DIR/plugins/ravenclaude-core/skills/terminal-status-indicators/setup-terminal-indicators.sh"
if [ -f "$TI_SETUP" ]; then
  log "Installing terminal status indicators (bell + chime + idle-watcher)..."
  bash "$TI_SETUP" --project "$PWD" >/dev/null 2>&1 \
    && log "  done — open a new terminal, then 'watch-terminals'" \
    || log "  SKIP: terminal-indicators setup failed (non-fatal)."
fi

log "Setup complete. Open a NEW terminal and type 'rc' to launch Copilot with RavenClaude."
