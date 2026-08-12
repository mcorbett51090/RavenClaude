#!/usr/bin/env bash
#
# mcorbett51090/dotfiles — GitHub Codespaces auto-provisioner
#
# Runs automatically on EVERY new Codespace (any repo) once you enable:
#   GitHub → Settings → Codespaces → "Automatically install dotfiles"
#   → select  mcorbett51090/dotfiles
#
# Design contract:
#  • Every optional step is failure-isolated (run_step): a broken step is logged
#    and skipped — this script ALWAYS exits 0 and can never abort a Codespace.
#  • Idempotent: re-runs install nothing already present.
#  • Tolerates minimal base images (Node/npm/code may be absent).
#  • No secrets in this repo.
#
set -euo pipefail

# ── persistent log: capture stdout AND stderr (create-time output is otherwise lost) ──
LOGFILE="${HOME}/.dotfiles-install.log"
exec > >(tee -a "$LOGFILE") 2>&1

# ── put install dirs on PATH IN THIS PROCESS ────────────────────────────────
# install.sh runs in a non-interactive shell; ~/.bashrc is NOT sourced here, so
# without this a tool installed in an early step is invisible to later steps.
export NPM_CONFIG_PREFIX="${HOME}/.npm-global"          # env var survives subshells
export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"

# ── pinned versions / config ────────────────────────────────────────────────
RUFF_VERSION="0.15.20"
ACTIONLINT_VERSION="1.7.12"
PRETTIER_MAJOR="3"
MARKETPLACE_REPO="mcorbett51090/RavenClaude"
MARKETPLACE_NAME="ravenclaude"
PLUGIN="ravenclaude-core"

# VS Code extensions installed when the `code` CLI is present. Edit freely.
VSCODE_EXTENSIONS=(
  "github.copilot"
  "github.copilot-chat"
  "esbenp.prettier-vscode"
  "charliermarsh.ruff"
)

# ── helpers ─────────────────────────────────────────────────────────────────
log()  { printf '[dotfiles] %s\n' "$*"; }
warn() { printf '[dotfiles][warn] %s\n' "$*" >&2; }
have() { command -v "$1" >/dev/null 2>&1; }

OK=0; SKIP=0; FAIL=0; STEP_I=0
STEPS_TOTAL=9

# run_step "<label>" <function> — never lets an optional step abort the run.
# A step returns 0 (ok), 75 (intentional skip), or any other code (soft fail).
run_step() {
  local label="$1" fn="$2" rc=0
  STEP_I=$((STEP_I + 1))
  printf '\n→ [%d/%d] %s\n' "$STEP_I" "$STEPS_TOTAL" "$label"
  ( set +e; "$fn" ); rc=$?
  case "$rc" in
    0)  OK=$((OK + 1));     log "✓ ${label}" ;;
    75) SKIP=$((SKIP + 1)); log "• skipped: ${label}" ;;
    *)  FAIL=$((FAIL + 1)); warn "✗ ${label} (rc=${rc}; non-fatal — see ${LOGFILE})" ;;
  esac
  return 0
}

append_once() {  # append_once <file> <line> <unique-marker>
  local file="$1" line="$2" marker="$3"
  [ -e "$file" ] || : > "$file"
  grep -qF -- "$marker" "$file" 2>/dev/null || printf '%s\n' "$line" >> "$file"
}

persist_path() {  # add <dir> to PATH for future interactive shells (.bashrc + .profile)
  local dir="$1"
  append_once "${HOME}/.bashrc"  "export PATH=\"${dir}:\$PATH\"" "${dir} #dotfiles-path"
  append_once "${HOME}/.profile" "export PATH=\"${dir}:\$PATH\"" "${dir} #dotfiles-path"
}

node_major() { node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0; }
node_ge_22() { have node && [ "$(node_major)" -ge 22 ]; }

# gh_dl <url> <out> — authenticated GitHub download dodges shared-IP rate limits.
# The token is attached ONLY for GitHub hosts (never leaked to other domains).
gh_dl() {
  local url="$1" out="$2"
  case "$url" in
    https://github.com/*|https://*.githubusercontent.com/*|https://api.github.com/*)
      if [ -n "${GITHUB_TOKEN:-}" ]; then
        curl -fsSL -H "Authorization: Bearer ${GITHUB_TOKEN}" "$url" -o "$out"
        return $?
      fi ;;
  esac
  curl -fsSL "$url" -o "$out"
}

arch_ruff() {        # uname -m → ruff release triple
  case "$(uname -m)" in
    x86_64)        echo "x86_64-unknown-linux-gnu" ;;
    aarch64|arm64) echo "aarch64-unknown-linux-gnu" ;;
    *)             echo "" ;;
  esac
}
arch_actionlint() {  # uname -m → actionlint arch token
  case "$(uname -m)" in
    x86_64)        echo "amd64" ;;
    aarch64|arm64) echo "arm64" ;;
    *)             echo "" ;;
  esac
}

# ── steps ───────────────────────────────────────────────────────────────────

step_node() {
  if node_ge_22; then log "node $(node -v) present (>=22)"; return 0; fi
  log "node missing or <22 — attempting to provide node>=22"
  if have nvm; then nvm install 22 >/dev/null 2>&1 && nvm alias default 22 >/dev/null 2>&1 && return 0; fi
  if have n && sudo -n true 2>/dev/null; then sudo n 22 >/dev/null 2>&1 && return 0; fi
  warn "no nvm/n/sudo path to node>=22; node-dependent steps will skip"
  return 75
}

step_claude() {
  if have claude; then log "claude present: $(claude --version 2>/dev/null || echo '?')"; return 0; fi
  # primary: native installer (no Node required); installs to ~/.local/bin
  local tmp; tmp="$(mktemp)"
  if gh_dl "https://claude.ai/install.sh" "$tmp" && bash "$tmp"; then
    rm -f "$tmp"
    have claude && return 0
  fi
  rm -f "$tmp"
  # fallback: npm (requires Node)
  if have npm; then
    npm install -g @anthropic-ai/claude-code && have claude && return 0
  fi
  warn "claude install failed (native installer and npm both failed)"
  return 1
}

# Deferred self-heal: if the plugin can't install now (e.g. before first login),
# retry once per interactive shell until it sticks, then stop checking.
install_plugin_selfheal() {
  local hook="${HOME}/.config/ravenclaude/plugin-selfheal.sh"
  mkdir -p "$(dirname "$hook")"
  cat > "$hook" <<EOF
# auto-generated by dotfiles install.sh — installs ${PLUGIN} once it can, then no-ops.
_rc_marker="\${HOME}/.config/ravenclaude/.plugin-installed"
if [ ! -f "\$_rc_marker" ] && command -v claude >/dev/null 2>&1; then
  if claude plugin list 2>/dev/null | grep -q '${PLUGIN}'; then
    touch "\$_rc_marker"
  else
    claude plugin marketplace add ${MARKETPLACE_REPO} >/dev/null 2>&1 || true
    if claude plugin install ${PLUGIN}@${MARKETPLACE_NAME} >/dev/null 2>&1; then
      touch "\$_rc_marker"; echo '[dotfiles] ${PLUGIN} installed (deferred).'
    fi
  fi
fi
unset _rc_marker
EOF
  append_once "${HOME}/.bashrc" "[ -f \"${hook}\" ] && source \"${hook}\"" "plugin-selfheal.sh #dotfiles"
}

step_plugin() {
  have claude || { warn "claude CLI absent — cannot install ${PLUGIN}"; return 75; }
  if claude plugin list 2>/dev/null | grep -q "${PLUGIN}"; then
    log "${PLUGIN} already installed"; return 0
  fi
  claude plugin marketplace add "${MARKETPLACE_REPO}" >/dev/null 2>&1 || true
  if claude plugin install "${PLUGIN}@${MARKETPLACE_NAME}" >/dev/null 2>&1 \
     && claude plugin list 2>/dev/null | grep -q "${PLUGIN}"; then
    log "installed ${PLUGIN}"; return 0
  fi
  install_plugin_selfheal
  warn "${PLUGIN} not installed yet — a deferred hook will retry on your next terminal"
  return 1
}

step_prettier() {
  if have prettier; then log "prettier $(prettier --version) present"; return 0; fi
  have npm || { warn "npm absent — skipping prettier"; return 75; }
  npm install -g "prettier@${PRETTIER_MAJOR}"
}

step_actionlint() {
  if have actionlint; then log "actionlint present: $(actionlint --version 2>/dev/null | head -1)"; return 0; fi
  have curl || { warn "curl absent — skipping actionlint"; return 75; }
  local arch; arch="$(arch_actionlint)"
  [ -n "$arch" ] || { warn "unsupported arch $(uname -m) — skipping actionlint"; return 75; }
  local base="https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}"
  local tarball="actionlint_${ACTIONLINT_VERSION}_linux_${arch}.tar.gz"
  local tmp; tmp="$(mktemp -d)"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmp'" RETURN
  gh_dl "${base}/${tarball}" "${tmp}/${tarball}" || { warn "actionlint download failed"; return 1; }
  gh_dl "${base}/actionlint_${ACTIONLINT_VERSION}_checksums.txt" "${tmp}/sums.txt" \
    || { warn "actionlint checksums download failed"; return 1; }
  ( cd "$tmp" && grep " ${tarball}\$" sums.txt | sha256sum -c - >/dev/null ) \
    || { warn "actionlint checksum MISMATCH — refusing to install"; return 1; }
  tar -xzf "${tmp}/${tarball}" -C "$tmp" actionlint || return 1
  mkdir -p "${HOME}/.local/bin"
  mv "${tmp}/actionlint" "${HOME}/.local/bin/actionlint"
  chmod +x "${HOME}/.local/bin/actionlint"
  persist_path "${HOME}/.local/bin"
}

step_ruff() {
  if have ruff; then log "ruff $(ruff --version) present"; return 0; fi
  have curl || { warn "curl absent — skipping ruff"; return 75; }
  local triple; triple="$(arch_ruff)"
  [ -n "$triple" ] || { warn "unsupported arch $(uname -m) — skipping ruff"; return 75; }
  local base="https://github.com/astral-sh/ruff/releases/download/${RUFF_VERSION}"
  local tarball="ruff-${triple}.tar.gz"
  local tmp; tmp="$(mktemp -d)"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmp'" RETURN
  gh_dl "${base}/${tarball}" "${tmp}/${tarball}" || { warn "ruff download failed"; return 1; }
  gh_dl "${base}/${tarball}.sha256" "${tmp}/sum.sha256" || { warn "ruff checksum download failed"; return 1; }
  local want; want="$(awk '{print $1}' "${tmp}/sum.sha256")"
  ( cd "$tmp" && printf '%s  %s\n' "$want" "$tarball" | sha256sum -c - >/dev/null ) \
    || { warn "ruff checksum MISMATCH — refusing to install"; return 1; }
  tar -xzf "${tmp}/${tarball}" -C "$tmp" || return 1
  local bin; bin="$(find "$tmp" -type f -name ruff | head -1)"
  [ -n "$bin" ] || { warn "ruff binary not found in tarball"; return 1; }
  mkdir -p "${HOME}/.local/bin"
  mv "$bin" "${HOME}/.local/bin/ruff"
  chmod +x "${HOME}/.local/bin/ruff"
  persist_path "${HOME}/.local/bin"
}

step_copilot() {
  if have copilot; then log "copilot CLI present"; return 0; fi
  have npm || { warn "npm absent — skipping Copilot CLI"; return 75; }
  node_ge_22 || { warn "Copilot CLI needs node>=22 (have $(node -v 2>/dev/null || echo none)) — skipping"; return 75; }
  npm install -g @github/copilot
}

step_vscode_ext() {
  have code || { warn "'code' CLI absent (headless) — skipping VS Code extensions"; return 75; }
  local installed; installed="$(code --list-extensions 2>/dev/null || true)"
  local ext
  for ext in "${VSCODE_EXTENSIONS[@]}"; do
    if printf '%s\n' "$installed" | grep -qix -- "$ext"; then
      log "ext present: $ext"
    elif code --install-extension "$ext" --force >/dev/null 2>&1; then
      log "installed ext: $ext"
    else
      warn "ext failed: $ext"
    fi
  done
  return 0
}

step_auth_nudge() {
  local need=0
  echo "──────── auth checklist (one-time, interactive — never automated) ────────"
  if have gh && ! gh auth status >/dev/null 2>&1; then
    echo "  • gh auth login        # GitHub CLI not authenticated"
    need=1
  fi
  if have claude; then
    echo "  • run 'claude'         # then complete the browser login if prompted"
    need=1
  fi
  [ "$need" -eq 0 ] && echo "  ✓ nothing to do — you're authenticated"
  echo "──────────────────────────────────────────────────────────────────────────"
  return 0
}

# ── orchestration ───────────────────────────────────────────────────────────
main() {
  log "bootstrap starting ($(date -u +%FT%TZ)) — full log: ${LOGFILE}"
  persist_path "${HOME}/.local/bin"
  persist_path "${HOME}/.npm-global/bin"

  run_step "Node >= 22"                       step_node
  run_step "Claude Code CLI"                  step_claude
  run_step "ravenclaude-core plugin"          step_plugin
  run_step "prettier@${PRETTIER_MAJOR}"       step_prettier
  run_step "actionlint v${ACTIONLINT_VERSION}" step_actionlint
  run_step "ruff ${RUFF_VERSION}"             step_ruff
  run_step "GitHub Copilot CLI"               step_copilot
  run_step "VS Code extensions"               step_vscode_ext
  run_step "Auth checklist"                   step_auth_nudge

  printf '\n[dotfiles] done: %d ok, %d skipped, %d soft-failed (all non-fatal). Log: %s\n' \
    "$OK" "$SKIP" "$FAIL" "$LOGFILE"
}

main "$@"
exit 0
