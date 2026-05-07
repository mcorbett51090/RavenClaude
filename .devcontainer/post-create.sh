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

log "Setup complete. Available tools: claude, gh, node."
