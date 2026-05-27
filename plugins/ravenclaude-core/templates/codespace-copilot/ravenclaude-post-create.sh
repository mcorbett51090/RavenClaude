#!/usr/bin/env bash
# RavenClaude + GitHub Copilot CLI — Codespace auto-setup (consumer-side).
#
# Drop this file (plus the sibling devcontainer.json) into a consumer repo's
# .devcontainer/ — either with `ravenclaude init-codespace` or by hand (see
# README.md in templates/codespace-copilot/). It runs automatically when the
# Codespace is built or rebuilt and leaves the repo fully wired for GitHub
# Copilot CLI, with no commands to type:
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

# 1. GitHub Copilot CLI (needs Node 22+). Best-effort; nudge if it can't install.
if command -v copilot >/dev/null 2>&1; then
  log "GitHub Copilot CLI present: $(copilot --version 2>/dev/null || echo '?')"
else
  log "Installing GitHub Copilot CLI (npm install -g @github/copilot)..."
  npm install -g @github/copilot >/dev/null 2>&1 \
    && log "  installed" \
    || log "  WARN: could not install automatically — run 'npm install -g @github/copilot' (needs Node 22+)."
fi

# 2. Clone the RavenClaude marketplace if we don't already have it (uses gh auth).
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

# 3. One-shot wire-up of THIS repo (skills + hooks + MCP + posture + rc alias).
log "Wiring this repo for Copilot (skills + hooks + MCP + posture + alias)..."
bash "$RC_DIR/scripts/ravenclaude" setup --project "$PWD"

log "Setup complete. Open a NEW terminal and type 'rc' to launch Copilot with RavenClaude."
