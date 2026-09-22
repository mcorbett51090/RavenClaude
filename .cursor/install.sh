#!/usr/bin/env bash
# Idempotent Cloud Agent install for the RavenClaude marketplace.
#
# The marketplace is markdown + shell + JSON manifests. The Cursor default base
# image already ships python3, node/npx, jq, git and gh. This script adds only
# the pieces the CI gates and dashboard generator need but the base image lacks:
#   - ruff        (validate-marketplace Gate 9b + audit-gates ruff fixture)
#   - jsonschema  (validate-schemas)
#   - actionlint  (validate-marketplace Gate 10 + audit-gates Gate 188)
#   - headless-Chrome shared libs (scripts/generate-dashboards.py -> mermaid-cli)
#   - qrcode      (optional phone QR for scripts/serve-dashboards.py)
#
# Versions are pinned to the exact ones CI uses (.github/workflows/
# validate-marketplace.yml) so a local gate run matches the required checks.
# Everything here is idempotent: re-running is a no-op once satisfied.
set -euo pipefail

log() { printf '\n[cursor-install] %s\n' "$*"; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# ── Put the pip --user bin dir on PATH (this shell + future interactive ones) ──
USER_BIN="$(python3 -m site --user-base)/bin"
export PATH="$USER_BIN:$PATH"
BASHRC="${HOME}/.bashrc"
PATH_BEGIN="# >>> ravenclaude user-bin PATH >>>"
if [ -f "$BASHRC" ] && ! grep -qxF "$PATH_BEGIN" "$BASHRC" 2>/dev/null; then
  {
    echo "$PATH_BEGIN"
    echo 'export PATH="$(python3 -m site --user-base)/bin:$PATH"'
    echo "# <<< ravenclaude user-bin PATH <<<"
  } >>"$BASHRC"
fi

# ── Python lint/validate tooling (pinned to CI versions) ─────────────────────
log "Installing pinned Python tooling (ruff, jsonschema, qrcode)..."
python3 -m pip install --quiet --user --disable-pip-version-check \
  'ruff==0.15.8' 'jsonschema' 'qrcode'
log "  ruff $(ruff --version 2>/dev/null || echo '?')"

# ── actionlint (pinned, checksum-verified) → user bin, no sudo needed ────────
AL_VER=1.7.7
AL_SHA=023070a287cd8cccd71515fedc843f1985bf96c436b7effaecce67290e7e0757
if ! command -v actionlint >/dev/null 2>&1 || [ "$(actionlint --version 2>/dev/null | head -1)" != "$AL_VER" ]; then
  log "Installing actionlint ${AL_VER}..."
  mkdir -p "$USER_BIN"
  tmp="$(mktemp -d)"
  if curl -fsSL "https://github.com/rhysd/actionlint/releases/download/v${AL_VER}/actionlint_${AL_VER}_linux_amd64.tar.gz" -o "$tmp/al.tgz" \
    && echo "${AL_SHA}  ${tmp}/al.tgz" | sha256sum -c - >/dev/null 2>&1; then
    tar -xzf "$tmp/al.tgz" -C "$tmp" actionlint
    install -m 0755 "$tmp/actionlint" "$USER_BIN/actionlint"
    log "  installed: $("$USER_BIN/actionlint" --version | head -1)"
  else
    log "  WARN: actionlint download/checksum failed — Gate 10 will fall back to its own resolver."
  fi
  rm -rf "$tmp"
fi

# ── Headless-Chrome shared libs for mermaid-cli (dashboard generator) ────────
# Idempotent (apt-get install is a no-op on satisfied packages). Guarded on
# passwordless sudo; non-fatal because the dashboard is already committed as
# a prebuilt index.html and only regeneration needs mermaid.
if sudo -n true 2>/dev/null; then
  log "Installing headless-Chrome deps for mermaid-cli (idempotent)..."
  sudo apt-get update -qq >/dev/null 2>&1 || true
  sudo apt-get install -y \
    libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libasound2t64 \
    libgbm1 libxfixes3 libxshmfence1 libnss3 libnspr4 \
    libpangocairo-1.0-0 libpangoft2-1.0-0 fonts-liberation \
    libxcomposite1 libxdamage1 libxrandr2 libxkbcommon0 \
    libdrm2 libxext6 libxrender1 libcairo2 >/dev/null 2>&1 \
    && log "  done" \
    || log "  WARN: some Chrome libs did not install — mermaid regeneration may not work locally."
else
  log "  SKIP: no passwordless sudo — install Chrome libs manually if regenerating dashboards."
fi

log "Install complete. Tools: python3, node, npx, jq, git, gh, ruff, actionlint."
