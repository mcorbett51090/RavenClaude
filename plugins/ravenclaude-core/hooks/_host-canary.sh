#!/usr/bin/env bash
# _host-canary.sh
# Behavioral canary for a --host install (P16). Sourced by scripts/ravenclaude
# at the end of each host lane.
#
# NOT a files-exist check. The installer already knows it wrote a hooks file;
# MH-07 / MH-01 were "wired, reviewing nothing" — the file was there and the
# invocation path never fired. This plants a marker the probe writes ONLY when
# the host's real adapter / shim actually invokes it, then checks the marker.
#
# ── M10 HONEST LIMIT (read this before trusting the canary) ────────────────
# Live-host behavior (a running Copilot / Codex / Cursor / Gemini session) is
# un-exercisable in CI. What this gates is adapter I/O + the planted-marker
# round-trip — the same seam Gate 167 crosses for Copilot→tribunal. A host
# whose adapter is missing, whose payload shape drifted, or whose installer
# canary step was stubbed out to print success, is caught. A host whose live
# binary ignores the hooks file is owner-verified, not CI-proven.
#
# ── D4 ADVISORY ────────────────────────────────────────────────────────────
# The installer WARNS when the marker does not fire and continues. This is not
# a hard onboarding bar (owner ruling 2026-08-13, seed #5). Gate 207 is what
# has teeth on the mechanism itself.
#
# NOT a registered hook — leading underscore. No top-level `set`. bash-3.2
# safe. No heredoc nested in $() (Gate 3b).

# Fallbacks so the helper is callable outside the installer (Gate 207).
if ! command -v ok >/dev/null 2>&1; then
  ok() { printf '  ✓ %s\n' "$*"; }
fi
if ! command -v warn >/dev/null 2>&1; then
  warn() { printf '  ! %s\n' "$*" >&2; }
fi
if ! command -v note >/dev/null 2>&1; then
  note() { printf '  %s\n' "$*"; }
fi

_rc_canary_core() {
  if [ -n "${CORE:-}" ] && [ -d "$CORE/hooks" ]; then
    printf '%s\n' "$CORE"
    return 0
  fi
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  printf '%s\n' "$(cd "$here/.." && pwd)"
}

# Bounded adapter invoke. `_rc_timeout` lives in _portable.sh; if it is not
# already sourced, source it. A hung adapter must not stall install.
_rc_canary_ensure_timeout() {
  command -v _rc_timeout >/dev/null 2>&1 && return 0
  local portable
  portable="$(_rc_canary_core)/hooks/_portable.sh"
  if [ -f "$portable" ]; then
    # shellcheck source=/dev/null
    . "$portable"
  fi
  command -v _rc_timeout >/dev/null 2>&1 && return 0
  _rc_timeout() { shift; "$@"; }
}

# CANARY_INVOKE_ANCHOR — Gate 207 teeth mutate this function. If the name
# disappears, the mutant builder fails loud rather than claiming teeth it
# does not have.
_rc_canary_invoke() {
  local host="$1" probe="$2" payload="$3" core adapter
  core="$(_rc_canary_core)"
  _rc_canary_ensure_timeout
  case "$host" in
    copilot)
      adapter="$core/hooks/copilot-hook-adapter.sh"
      [ -f "$adapter" ] || return 1
      printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" bash-pretool "$probe" >/dev/null 2>&1 || true
      ;;
    codex)
      adapter="$core/hooks/codex-hook-env.sh"
      [ -f "$adapter" ] || return 1
      printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" "$probe" >/dev/null 2>&1 || true
      ;;
    gemini)
      adapter="$core/hooks/gemini-hook-adapter.sh"
      [ -f "$adapter" ] || return 1
      printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" pretool "$probe" >/dev/null 2>&1 || true
      ;;
    cursor)
      adapter="$core/hooks/cursor-hook-adapter.sh"
      [ -f "$adapter" ] || return 1
      printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" shell-pretool "$probe" >/dev/null 2>&1 || true
      ;;
    claude-code)
      printf '%s' "$payload" | _rc_timeout 8 bash "$probe" >/dev/null 2>&1 || true
      ;;
    *)
      return 1
      ;;
  esac
  return 0
}

_rc_canary_payload() {
  local host="$1" cwd="$2"
  case "$host" in
    copilot)
      printf '%s' '{"toolName":"bash","toolArgs":"{\"command\":\"true\"}","cwd":"'"$cwd"'","sessionId":"rc-canary"}'
      ;;
    gemini)
      printf '%s' '{"tool_name":"run_shell_command","tool_input":{"command":"true"},"cwd":"'"$cwd"'","session_id":"rc-canary"}'
      ;;
    cursor)
      printf '%s' '{"command":"true","cwd":"'"$cwd"'","conversation_id":"rc-canary"}'
      ;;
    *)
      # Codex + Claude Code: native Claude-shaped stdin.
      printf '%s' '{"tool_name":"Bash","tool_input":{"command":"true"},"cwd":"'"$cwd"'","session_id":"rc-canary"}'
      ;;
  esac
}

_rc_canary_hooks_supported() {
  local host="$1" map
  map="$(_rc_host_support_path 2>/dev/null || true)"
  if [ -z "$map" ] || [ ! -f "$map" ]; then
    # Fallback if rearm helper is not sourced: derive from this file.
    map="$(_rc_canary_core)/knowledge/host-support.json"
  fi
  [ -f "$map" ] || { printf 'no\n'; return 0; }
  command -v python3 >/dev/null 2>&1 || { printf 'no\n'; return 0; }
  python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))
cell=((d.get("components") or {}).get("hooks") or {}).get(sys.argv[2]) or {}
print("yes" if cell.get("supported") is True else "no")
' "$map" "$host" 2>/dev/null || printf 'no\n'
}

# _rc_host_canary HOST [PROJECT]
# Return 0 if the planted marker fired, 1 if the host has no hook path (skip),
# 2 if the invocation ran (or was claimed to) and the marker did not fire.
_rc_host_canary() {
  local host="${1:-}" project="${2:-$PWD}"
  local outdir probe token payload supported
  [ -n "$host" ] || return 1
  supported="$(_rc_canary_hooks_supported "$host")"
  if [ "$supported" != "yes" ]; then
    note "canary: $host has no hook path — skipped (not a files-exist check)"
    return 1
  fi

  outdir="$(mktemp -d "${TMPDIR:-/tmp}/rc-canary.XXXXXX")"
  token="rc-canary-$$-$RANDOM"
  probe="$outdir/probe.sh"
  # Overrides let Gate 207 plant its own marker so a mutant that returns 0
  # without invoking the probe is visible to the checker.
  RC_CANARY_TOKEN="${RC_CANARY_TOKEN:-$token}"
  RC_CANARY_OUT="${RC_CANARY_OUT:-$outdir/marker}"
  export RC_CANARY_TOKEN RC_CANARY_OUT
  printf '%s\n' '#!/usr/bin/env bash' >"$probe"
  printf '%s\n' 'printf "%s\n" "${RC_CANARY_TOKEN:-}" > "${RC_CANARY_OUT:-/dev/null}"' >>"$probe"
  printf '%s\n' 'exit 0' >>"$probe"
  chmod +x "$probe"

  payload="$(_rc_canary_payload "$host" "$project")"
  # CANARY_INVOKE_ANCHOR (call site) — do not rename; Gate 207 mutates this.
  _rc_canary_invoke "$host" "$probe" "$payload"

  if [ -f "$RC_CANARY_OUT" ] && [ "$(cat "$RC_CANARY_OUT" 2>/dev/null)" = "$RC_CANARY_TOKEN" ]; then
    ok "canary: $host invocation path fired (planted marker)"
    rm -rf "$outdir"
    return 0
  fi
  warn "canary: $host invocation path did not fire the planted marker — guardrails may be inert on this host."
  note "  Advisory (D4): install continues. Live-host behavior is owner-verified (M10)."
  rm -rf "$outdir"
  return 2
}
