#!/usr/bin/env bash
# Idempotent post-create setup for RavenClaude — the central Claude hub.
# Runs automatically after the devcontainer is built or rebuilt.
#
# This hub is intentionally domain-neutral. Only general-purpose Claude
# tooling is installed here. Domain-specific tools (e.g. pac for Power
# Platform, sfdx for Salesforce) belong in their respective Expert repos.

set -euo pipefail

log() { printf "\n[post-create] %s\n" "$*"; }

# ── Claude Code CLI ─────────────────────────────────────────────────
log "Checking Claude Code CLI..."
if command -v claude >/dev/null 2>&1; then
  log "  already installed: $(claude --version 2>/dev/null || echo 'version unknown')"
else
  log "  installing @anthropic-ai/claude-code..."
  npm install -g @anthropic-ai/claude-code
  log "  installed: $(claude --version 2>/dev/null || echo 'version unknown')"
fi

# ── GitHub CLI auth nudge (non-blocking) ────────────────────────────
if command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    log "  gh CLI present but not authenticated — run 'gh auth login' when ready."
  fi
fi

# ── Headless Chrome deps for mermaid-cli (dashboard generator) ──────
# The dashboard generator (per docs/proposals/2026-05-22-003-per-plugin-dashboard.md
# §4.8) pre-renders Mermaid decision trees to static SVG at build time via
# `npx @mermaid-js/mermaid-cli mmdc`. mmdc downloads chrome-headless-shell
# which dynamically links the libs below. Without them mmdc fails with
# "libatk-1.0.so.0: cannot open shared object file" and similar.
#
# Verified on Ubuntu 24.04 (Noble) devcontainer 2026-05-22 — see
# docs/research/2026-05-22-dashboard-ux/spikes/mermaid-prerender/REPORT.md §2.
# Ubuntu 24.04 renamed several libs to *t64 (64-bit time_t transition).
#
# apt-get install -y is idempotent (no-op on already-installed packages).
log "Installing headless Chrome deps for mermaid-cli (idempotent)..."
if sudo -n true 2>/dev/null; then
  sudo apt-get install -y \
    libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libasound2t64 \
    libgbm1 libxfixes3 libxshmfence1 libnss3 libnspr4 \
    libpangocairo-1.0-0 libpangoft2-1.0-0 fonts-liberation \
    libxcomposite1 libxdamage1 libxrandr2 libxkbcommon0 \
    libdrm2 libxext6 libxrender1 libcairo2 \
    >/dev/null 2>&1 \
    && log "  done" \
    || log "  WARN: some packages didn't install — mermaid-cli may not work locally. CI runners have these pre-installed."
else
  log "  SKIP: no passwordless sudo. Install manually if running mermaid-cli locally:"
  log "        sudo apt-get install -y libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libasound2t64 \\\\"
  log "          libgbm1 libxfixes3 libxshmfence1 libnss3 libnspr4 libpangocairo-1.0-0 libpangoft2-1.0-0 \\\\"
  log "          fonts-liberation libxcomposite1 libxdamage1 libxrandr2 libxkbcommon0 libdrm2 libxext6 \\\\"
  log "          libxrender1 libcairo2"
fi

# ── qrcode (optional) for serve-dashboards.py phone QR ──────────────
# serve-dashboards.py prints a scannable QR of the forwarded URL so the
# dashboard can be opened (and "Save & apply" run) from a phone. The lib is
# optional — the server degrades to printing the URL + an install hint without
# it — but installing here makes the QR appear by default. ASCII renderer only,
# no Pillow/image deps. Non-fatal if pip is unavailable or offline.
log "Installing qrcode (optional — phone QR for serve-dashboards.py)..."
python3 -m pip install --quiet --disable-pip-version-check qrcode >/dev/null 2>&1 \
  && log "  done" \
  || log "  SKIP: qrcode not installed (serve-dashboards.py will print the URL + a hint instead)."

log "Setup complete. Available tools: claude, gh, node."
