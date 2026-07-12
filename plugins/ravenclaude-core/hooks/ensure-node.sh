#!/usr/bin/env bash
# ensure-node.sh — OPTIONAL Node.js provisioning for ravenclaude-core.
#
# Node is NOT required by ravenclaude-core itself (its gates are python + bash).
# This is a convenience for CONSUMER projects whose tooling/gates need `node`
# (e.g. .mjs test gates). Claude Code plugins have no install-time execution and
# committing per-platform node binaries to the marketplace git repo is
# impractical — so node is fetched ON DEMAND into the plugin's PERSISTENT data
# dir (CLAUDE_PLUGIN_DATA, which survives plugin updates) and wired onto PATH.
#
# TWO MODES:
#   (no args, SessionStart)  fast + network-free. If a system node >= MIN_MAJOR
#       is already present, do nothing. Else if a RavenClaude-provisioned node
#       exists, add it to PATH for this session via CLAUDE_ENV_FILE. Else, if the
#       project looks node-relevant, inject a one-line nudge to run /node-setup.
#       Never blocks; always exits 0 (SessionStart hooks cannot block anyway).
#   --install   download the latest Node LTS static build for this OS/arch from
#       nodejs.org into CLAUDE_PLUGIN_DATA, VERIFY the SHASUMS256 checksum, and
#       symlink node/npm/npx. Run once via /ravenclaude-core:node-setup.
#
# Fail-silent in the default mode; loud + fail-closed (never installs an
# unverified binary) in --install mode.

set -u

MIN_MAJOR=18   # consumer JS tooling generally wants >= 18
DATA="${CLAUDE_PLUGIN_DATA:-$HOME/.local/share/ravenclaude-core}"
NODE_BIN_DIR="$DATA/bin"
# Absolute path to THIS script, so the nudge can print a copy-paste-able command
# regardless of whether CLAUDE_PLUGIN_ROOT is exported in the caller's shell.
SELF="$(cd "$(dirname "$0")" 2>/dev/null && pwd)/$(basename "$0")"

log() { printf '%s\n' "$*" >&2; }

detect_platform() {
  local os arch
  case "$(uname -s)" in
    Darwin) os=darwin ;;
    Linux)  os=linux ;;
    MINGW*|MSYS*|CYGWIN*) os=win ;;
    *) os=unsupported ;;
  esac
  case "$(uname -m)" in
    arm64|aarch64) arch=arm64 ;;
    x86_64|amd64)  arch=x64 ;;
    *) arch=unsupported ;;
  esac
  printf '%s %s\n' "$os" "$arch"
}

install_node() {
  command -v python3 >/dev/null 2>&1 || { log "[node-setup] python3 is required to resolve the LTS version."; exit 1; }
  command -v curl    >/dev/null 2>&1 || { log "[node-setup] curl is required."; exit 1; }
  local os arch
  read -r os arch < <(detect_platform)
  if [ "$os" = win ]; then
    log "[node-setup] Windows detected. This bash provisioner targets macOS/Linux."
    log "[node-setup] Install Node from https://nodejs.org/en/download and make sure 'node' is on PATH."
    exit 1
  fi
  if [ "$os" = unsupported ] || [ "$arch" = unsupported ]; then
    log "[node-setup] unsupported platform: $(uname -s)/$(uname -m)."
    exit 1
  fi

  local tmp; tmp="$(mktemp -d)" || { log "[node-setup] mktemp failed."; exit 1; }
  trap 'rm -rf "$tmp"' EXIT

  log "[node-setup] resolving the latest Node LTS for ${os}-${arch}…"
  curl -fsSL https://nodejs.org/dist/index.json -o "$tmp/index.json" \
    || { log "[node-setup] could not fetch the Node version index (offline?)."; exit 1; }

  local ver
  ver="$(python3 - "$tmp/index.json" "$os" "$arch" <<'PY'
import json, sys
idx, os_, arch = sys.argv[1], sys.argv[2], sys.argv[3]
tag = ("osx-%s-tar" % arch) if os_ == "darwin" else ("linux-%s" % arch)
for r in json.load(open(idx)):
    if r.get("lts") and any(tag in f for f in r.get("files", [])):
        print(r["version"]); break
PY
)"
  [ -n "$ver" ] || { log "[node-setup] could not determine an LTS version for this platform."; exit 1; }

  local pkg="node-${ver}-${os}-${arch}.tar.gz"
  local base="https://nodejs.org/dist/${ver}"
  log "[node-setup] downloading ${pkg}…"
  curl -fsSL "${base}/${pkg}"          -o "$tmp/$pkg"            || { log "[node-setup] download failed."; exit 1; }
  curl -fsSL "${base}/SHASUMS256.txt"  -o "$tmp/SHASUMS256.txt"  || { log "[node-setup] checksum-file download failed."; exit 1; }

  log "[node-setup] verifying SHASUMS256 checksum…"
  local sumline; sumline="$(grep "  ${pkg}\$" "$tmp/SHASUMS256.txt" || true)"
  [ -n "$sumline" ] || { log "[node-setup] no checksum line for ${pkg} — aborting."; exit 1; }
  local verified=""
  if command -v shasum >/dev/null 2>&1; then
    ( cd "$tmp" && printf '%s\n' "$sumline" | shasum -a 256 -c - ) >/dev/null 2>&1 && verified=1
  elif command -v sha256sum >/dev/null 2>&1; then
    ( cd "$tmp" && printf '%s\n' "$sumline" | sha256sum -c - ) >/dev/null 2>&1 && verified=1
  else
    log "[node-setup] no shasum/sha256sum available to verify — refusing to install an unverified binary."; exit 1
  fi
  [ -n "$verified" ] || { log "[node-setup] CHECKSUM MISMATCH for ${pkg} — aborting (not installing an unverified binary)."; exit 1; }

  mkdir -p "$DATA/opt" "$NODE_BIN_DIR"
  local ndir="$DATA/opt/node-${ver}-${os}-${arch}"
  rm -rf "$ndir"
  tar -xzf "$tmp/$pkg" -C "$DATA/opt" || { log "[node-setup] extraction failed."; exit 1; }
  local b
  for b in node npm npx; do ln -sf "$ndir/bin/$b" "$NODE_BIN_DIR/$b"; done

  log "[node-setup] installed Node ${ver} into ${NODE_BIN_DIR}"
  "$NODE_BIN_DIR/node" --version >&2 2>/dev/null || true
  log "[node-setup] New sessions get it on PATH automatically (via the ensure-node.sh SessionStart hook)."
  log "[node-setup] For THIS shell:  export PATH=\"${NODE_BIN_DIR}:\$PATH\""
  exit 0
}

# ---- --install mode --------------------------------------------------------
case "${1:-}" in
  --install) install_node ;;
esac

# ---- default mode (SessionStart): fast, network-free -----------------------

# 1) A sufficient system node already exists → nothing to do.
if command -v node >/dev/null 2>&1; then
  maj="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
  if [ "${maj:-0}" -ge "$MIN_MAJOR" ] 2>/dev/null; then exit 0; fi
fi

# 2) A RavenClaude-provisioned node exists → put it on PATH for this session.
if [ -x "$NODE_BIN_DIR/node" ]; then
  if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    printf 'export PATH="%s:$PATH"\n' "$NODE_BIN_DIR" >> "$CLAUDE_ENV_FILE"
  fi
  exit 0
fi

# 3) Nothing available. Only nudge when the project actually looks node-relevant,
#    to avoid noise for non-JS projects. Cheap cwd probe, no recursion.
node_relevant() {
  [ -f package.json ] && return 0
  [ -d node_modules ] && return 0
  ls ./*.mjs ./*.cjs >/dev/null 2>&1 && return 0
  ls ./scripts/*.mjs >/dev/null 2>&1 && return 0
  return 1
}
if node_relevant; then
  msg="Node.js isn't installed but this project appears to use it (found package.json / .mjs). ravenclaude-core can provision a local Node LTS on demand — run  /ravenclaude-core:node-setup  (or:  bash \"${SELF}\" --install ). It downloads into the plugin's persistent data dir, verifies the checksum, and auto-adds node to PATH each session. No sudo, no system-wide install."
  python3 - "$msg" <<'PY' 2>/dev/null || true
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": sys.argv[1]}}))
PY
fi
exit 0
