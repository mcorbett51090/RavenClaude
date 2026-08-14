#!/usr/bin/env bash
# _rearm-notice.sh
# Shared re-arm notice for hosts whose guardrails silently disarm after an
# update (P18). Sourced by scripts/ravenclaude at install / update / status.
#
# NOT a registered hook — the leading underscore keeps it out of the hook count
# (same convention as _portable.sh / _emit-event.sh).
#
# activation_gate is the SSOT in knowledge/host-support.json, pinned by Gate 154:
#   hash_trust    — Codex: hooks are skipped until `/hooks` re-trusts the new hash
#   version_floor — Copilot: below 1.0.52 a sub-agent's tool calls are not hooked
#   none          — no extra activation step
#
# Carries no top-level `set` (it is sourced). Every function is bash-3.2 safe.
# No heredoc nested in $() (Gate 3b).

# Resolve the host-support map. Prefer the installer's CORE; fall back to this
# file's plugin root so the helper is callable standalone (Gate 207).
_rc_host_support_path() {
  if [ -n "${_RC_HOST_SUPPORT:-}" ] && [ -f "$_RC_HOST_SUPPORT" ]; then
    printf '%s\n' "$_RC_HOST_SUPPORT"
    return 0
  fi
  if [ -n "${CORE:-}" ] && [ -f "$CORE/knowledge/host-support.json" ]; then
    printf '%s\n' "$CORE/knowledge/host-support.json"
    return 0
  fi
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  printf '%s\n' "$here/../knowledge/host-support.json"
}

# _rc_activation_gate HOST — print hash_trust | version_floor | none.
# Fail-safe: missing map / missing python3 / unknown host → none (do not break
# an install over a lookup).
_rc_activation_gate() {
  local host="${1:-}"
  local map
  map="$(_rc_host_support_path)"
  if [ -z "$host" ] || [ ! -f "$map" ] || ! command -v python3 >/dev/null 2>&1; then
    printf 'none\n'
    return 0
  fi
  python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))
info=(d.get("hosts") or {}).get(sys.argv[2]) or {}
print(info.get("activation_gate") or "none")
' "$map" "$host" 2>/dev/null || printf 'none\n'
}

# Distinctive tokens Gate 207 greps for. Do not reword without updating the gate.
#   hash_trust    → "BY HASH" and "/hooks"
#   version_floor → "version floor" and "1.0.52"
_RC_REARM_HASH_TOKEN="BY HASH"
_RC_REARM_FLOOR_TOKEN="version floor"

# _rc_rearm_notice HOST SURFACE [PROJECT]
# SURFACE is install | update | status (status is the one-line form).
# A host whose activation_gate is `none` is a silent no-op.
_rc_rearm_notice() {
  local host="${1:-}" surface="${2:-install}" project="${3:-}"
  local gate n hooks
  gate="$(_rc_activation_gate "$host")"
  case "$gate" in
    hash_trust)
      n=0
      hooks="${project:+$project/.codex/hooks.json}"
      if [ -n "$hooks" ] && [ -f "$hooks" ] && command -v python3 >/dev/null 2>&1; then
        n="$(python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))
print(sum(len(g.get("hooks") or []) for ev in (d.get("hooks") or {}).values() for g in ev))
' "$hooks" 2>/dev/null || echo 0)"
      fi
      if [ "$surface" = "status" ]; then
        if command -v note >/dev/null 2>&1; then
          note "$host: hooks trusted $_RC_REARM_HASH_TOKEN — run /hooks to confirm they are TRUSTED"
        else
          printf '  %s: hooks trusted %s — run /hooks to confirm they are TRUSTED\n' "$host" "$_RC_REARM_HASH_TOKEN"
        fi
        return 0
      fi
      printf '\n'
      if command -v warn >/dev/null 2>&1; then
        warn "$host trusts hooks $_RC_REARM_HASH_TOKEN — re-trust after every update."
        note "Run /hooks inside $host and trust the ${n:-0} RavenClaude hook(s)."
        note "Until you do, they are SKIPPED — and no banner will say so, because the"
        note "SessionStart banner is itself a hook. Re-run /hooks after every 'git pull'."
        note "For teams: managed-hooks (requirements.toml) auto-trust by policy and is"
        note "the only configuration where these survive an update unattended."
      else
        printf '  ! %s trusts hooks %s — re-trust after every update.\n' "$host" "$_RC_REARM_HASH_TOKEN"
        printf '  Run /hooks inside %s and trust the %s RavenClaude hook(s).\n' "$host" "${n:-0}"
      fi
      ;;
    version_floor)
      # Prefer the installer's live copilot_version_check when sourced into it;
      # standalone (Gate 207) prints the static floor reminder so the notice is
      # still greppable when no copilot binary is on PATH.
      if [ "$surface" != "status" ] && command -v copilot_version_check >/dev/null 2>&1; then
        copilot_version_check
        return 0
      fi
      if command -v note >/dev/null 2>&1; then
        note "$host: $_RC_REARM_FLOOR_TOKEN is 1.0.52 — below it, sub-agent tool calls are NOT hooked."
      else
        printf '  %s: %s is 1.0.52 — below it, sub-agent tool calls are NOT hooked.\n' \
          "$host" "$_RC_REARM_FLOOR_TOKEN"
      fi
      ;;
    *)
      return 0
      ;;
  esac
}

# _rc_rearm_wired_hosts PROJECT SURFACE
# Emit a notice for every host that is actually wired in PROJECT and whose
# activation_gate is not `none`. This is the update/status entry point — one
# abstraction instead of a per-host copy (Codex hash-trust + Copilot floor).
_rc_rearm_wired_hosts() {
  local project="${1:-}" surface="${2:-update}"
  [ -n "$project" ] || return 0
  if [ -f "$project/.codex/hooks.json" ]; then
    _rc_rearm_notice "codex" "$surface" "$project"
  fi
  if [ -f "$project/.github/hooks/ravenclaude.json" ]; then
    _rc_rearm_notice "copilot" "$surface" "$project"
  fi
}
