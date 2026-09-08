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
#
# ── SESSIONSTART LANE (plan.md Phase 6, F-3/F-4) ────────────────────────────
# The PreToolUse lane above (_rc_host_canary / _rc_canary_invoke / _rc_canary_
# payload) is unmodified by this addition — see _rc_host_sessionstart_canary /
# _rc_canary_sessionstart_payload / _rc_canary_sessionstart_adapter below. The
# new lane drives each adapter's existing `sessionstart` mode (the bare shim
# for codex) with a SessionStart-shaped payload and asserts TWO things: the
# planted marker fired (invocation) AND the probe's own additionalContext
# sentinel actually reached the adapter's stdout (delivery) — a hook that
# runs but whose context is swallowed by an adapter I/O bug is invisible to
# an invocation-only check. Deliberately asserts invocation + delivery ONLY —
# never a `source`/`compact` filter (Cursor cannot express a matcher; Gemini's
# matcher fidelity is a declared none-unverified residual; see plan.md §1.2).

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
  local host="$1" probe="$2" payload="$3" mode="${4:-pretool}" core adapter
  core="$(_rc_canary_core)"
  _rc_canary_ensure_timeout
  if [ "$mode" = "sessionstart" ]; then
    # SessionStart lane (plan.md Phase 6) — an early return, so nothing below
    # this block (the PreToolUse `case "$host" in` dispatch) is touched by a
    # sessionstart-mode call, and the existing 3-arg call site in
    # _rc_host_canary (mode defaults to "pretool") is byte-behaviorally
    # unchanged.
    if [ "$host" = "claude-code" ]; then
      printf '%s' "$payload" | _rc_timeout 8 bash "$probe"
      return $?
    fi
    adapter="$(_rc_canary_sessionstart_adapter "$host")" || return 1
    [ -n "$adapter" ] && [ ! -f "$adapter" ] && return 1
    case "$host" in
      copilot)
        printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" sessionstart "$probe"
        return $?
        ;;
      codex)
        printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" "$probe"
        return $?
        ;;
      gemini)
        printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" sessionstart "$probe"
        return $?
        ;;
      cursor)
        printf '%s' "$payload" | _rc_timeout 8 bash "$adapter" sessionstart "$probe"
        return $?
        ;;
      *)
        return 1
        ;;
    esac
  fi
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

# _rc_canary_sessionstart_payload HOST CWD SOURCE
# Host-shaped SessionStart payloads (F-4 field set: source, session_id, cwd,
# transcript_path), mirroring _rc_canary_payload's per-host style above.
# Field NAMING follows each host's own established convention elsewhere in
# this file / its adapter: camelCase for Copilot, snake_case for Gemini /
# Codex / Claude Code, and Cursor's workspace_roots[]/conversation_id shape
# (cursor-hook-adapter.sh's _root()/_field conversation_id).
_rc_canary_sessionstart_payload() {
  local host="$1" cwd="$2" src="${3:-startup}"
  case "$host" in
    copilot)
      printf '%s' '{"source":"'"$src"'","sessionId":"rc-canary","cwd":"'"$cwd"'","workspaceRoot":"'"$cwd"'","transcriptPath":"/tmp/rc-canary-transcript.jsonl"}'
      ;;
    cursor)
      printf '%s' '{"source":"'"$src"'","conversation_id":"rc-canary","workspace_roots":["'"$cwd"'"],"cwd":"'"$cwd"'","transcript_path":"/tmp/rc-canary-transcript.jsonl"}'
      ;;
    gemini)
      printf '%s' '{"source":"'"$src"'","session_id":"rc-canary","cwd":"'"$cwd"'","transcript_path":"/tmp/rc-canary-transcript.jsonl"}'
      ;;
    *)
      # Codex + Claude Code: native Claude-shaped SessionStart stdin.
      printf '%s' '{"source":"'"$src"'","session_id":"rc-canary","cwd":"'"$cwd"'","transcript_path":"/tmp/rc-canary-transcript.jsonl"}'
      ;;
  esac
}

# _rc_canary_sessionstart_adapter HOST — print the sessionstart-lane adapter
# (or bare shim) path for HOST, or an empty string for claude-code (no
# adapter — the probe itself is invoked directly). Returns 1 for an
# unrecognised host. Single source of truth shared by _rc_canary_invoke's
# sessionstart branch and the pre-flight skip check in
# _rc_host_sessionstart_canary, so the two can never disagree about what
# "adapter present" means.
_rc_canary_sessionstart_adapter() {
  local host="$1" core
  core="$(_rc_canary_core)"
  case "$host" in
    copilot) printf '%s\n' "$core/hooks/copilot-hook-adapter.sh" ;;
    codex) printf '%s\n' "$core/hooks/codex-hook-env.sh" ;;
    gemini) printf '%s\n' "$core/hooks/gemini-hook-adapter.sh" ;;
    cursor) printf '%s\n' "$core/hooks/cursor-hook-adapter.sh" ;;
    claude-code) printf '%s\n' "" ;;
    *) return 1 ;;
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

# _rc_host_sessionstart_canary HOST [PROJECT]
# Tier-A SessionStart lane (plan.md Phase 6, F-3/F-4). Drives HOST's adapter
# (or bare shim, for codex) through its existing `sessionstart` mode with a
# SessionStart-shaped payload and asserts TWO things, not one:
#   1. INVOCATION — did the planted probe actually run? (same marker-file
#      technique as _rc_host_canary above)
#   2. DELIVERY   — did the probe's own additionalContext sentinel actually
#      reach the adapter's stdout? A hook that runs but whose context is
#      swallowed by a bug in an adapter's I/O translation is currently
#      invisible to an invocation-only check — this is what makes it visible.
# Deliberately does NOT assert a `compact`-source filter — see the header
# note at the top of this file and plan.md §Phase 6's boundary statement.
#
# Return codes (distinct from _rc_host_canary's 0/1/2 above, so a caller
# never has to guess which lane produced a given code):
#   0  both the marker fired AND the sentinel reached stdout
#   1  host/adapter unavailable — skip (never a silent pass)
#   2  DELIVERY failure — marker fired, sentinel did not reach stdout
#   3  INVOCATION failure — the planted marker never fired
_rc_host_sessionstart_canary() {
  local host="${1:-}" project="${2:-$PWD}"
  local outdir probe token sentinel payload supported adapter rc out
  local marker_ok sentinel_ok
  [ -n "$host" ] || return 1
  supported="$(_rc_canary_hooks_supported "$host")"
  if [ "$supported" != "yes" ]; then
    note "canary(sessionstart): $host has no hook path — skipped (not a files-exist check)"
    return 1
  fi
  if [ "$host" != "claude-code" ]; then
    adapter="$(_rc_canary_sessionstart_adapter "$host")"
    rc=$?
    if [ "$rc" -ne 0 ]; then
      note "canary(sessionstart): $host is not a recognised sessionstart-lane host — skipped"
      return 1
    fi
    if [ -n "$adapter" ] && [ ! -f "$adapter" ]; then
      note "canary(sessionstart): $host adapter not found at $adapter — skipped (not a silent pass)"
      return 1
    fi
  fi

  outdir="$(mktemp -d "${TMPDIR:-/tmp}/rc-canary-ss.XXXXXX")"
  token="rc-canary-ss-$$-$RANDOM"
  sentinel="rc-sessionstart-sentinel-${token}"
  probe="$outdir/probe.sh"
  # Overrides let a mutant-driving test plant its own token/sentinel, same
  # contract as RC_CANARY_TOKEN/RC_CANARY_OUT above.
  RC_CANARY_TOKEN="${RC_CANARY_TOKEN:-$token}"
  RC_CANARY_OUT="${RC_CANARY_OUT:-$outdir/marker}"
  RC_CANARY_SENTINEL="${RC_CANARY_SENTINEL:-$sentinel}"
  export RC_CANARY_TOKEN RC_CANARY_OUT RC_CANARY_SENTINEL
  printf '%s\n' '#!/usr/bin/env bash' >"$probe"
  printf '%s\n' 'printf "%s\n" "${RC_CANARY_TOKEN:-}" > "${RC_CANARY_OUT:-/dev/null}"' >>"$probe"
  printf '%s\n' 'printf "{\"hookSpecificOutput\":{\"additionalContext\":\"%s\"}}\n" "${RC_CANARY_SENTINEL:-}"' >>"$probe"
  printf '%s\n' 'exit 0' >>"$probe"
  chmod +x "$probe"

  payload="$(_rc_canary_sessionstart_payload "$host" "$project" "startup")"
  # CANARY_INVOKE_ANCHOR (sessionstart call site) — mirrors the PreToolUse
  # call site above; do not rename _rc_canary_invoke.
  out="$(_rc_canary_invoke "$host" "$probe" "$payload" sessionstart)"

  marker_ok=0
  sentinel_ok=0
  if [ -f "$RC_CANARY_OUT" ] && [ "$(cat "$RC_CANARY_OUT" 2>/dev/null)" = "$RC_CANARY_TOKEN" ]; then
    marker_ok=1
  fi
  if printf '%s' "$out" | grep -qF "$RC_CANARY_SENTINEL"; then
    sentinel_ok=1
  fi
  rm -rf "$outdir"

  if [ "$marker_ok" -eq 1 ] && [ "$sentinel_ok" -eq 1 ]; then
    ok "canary(sessionstart): $host invocation fired AND sentinel context delivered"
    return 0
  fi
  if [ "$marker_ok" -eq 1 ]; then
    warn "canary(sessionstart): $host DELIVERY failure — marker fired but the additionalContext sentinel did not reach stdout."
    return 2
  fi
  warn "canary(sessionstart): $host INVOCATION failure — the planted marker did not fire."
  return 3
}

# ── TIER D LANE — a real short-lived host session (plan.md Phase 7, §1.3) ──
#
# Everything above this line (_rc_host_canary / _rc_host_sessionstart_canary) is
# TIER A — it drives an ADAPTER SEAM with a synthetic payload. Tier A proves the
# seam; it cannot prove the host's own BINARY honors a real on-disk hook config
# (M10, stated at the top of this file). Tier D closes that gap the only way
# that is actually possible: spawn a real, bounded, tool-less one-shot host
# session against a SCRATCH project whose hook config wires ONLY the planted
# probe, and check whether the marker fired for real.
#
# Reuses the mechanism Plan-B's Finding 3 already live-proved this session (see
# plan.md §1.3 "Claude Code -> D"), rather than re-deriving it: a scratch
# `.claude/settings.json` `SessionStart` hook wired to a probe, driven by
# `claude -p "<no-op>"`, with `claude --help`'s `--bare` flag ("skip hooks, LSP,
# plugin sync") as the corroborating negative control.
#
# ── FOUR NON-NEGOTIABLE PROPERTIES (plan.md Phase 7) — read before editing ──
#  1. NEVER runs against the real project. The scratch dir (`mktemp -d`) is the
#     ONLY `cwd` ever used for the spawn below — never the caller's $PWD, never
#     $CLAUDE_PROJECT_DIR. Verified by A7.3 (git status --porcelain on the REAL
#     project tree is empty after a run).
#  2. POSITIVE CONTROL before any "did not fire" is trusted. The bidirectional
#     evidence (A7.1 fires on a real probe path, A7.2 does NOT fire on a
#     nonexistent one) lives in the acceptance-test script, not baked into every
#     runtime call — same precedent as Tier A above, whose bidirectionality
#     lives in Gate 207's fixtures, not inside `_rc_host_canary` itself.
#  3. Absent CLI => explicit skip (never silent, never a downgrade with no
#     note). Every skip path below calls `note`/`warn` before returning 1.
#  4. Every scratch hook-config write is a SINGLE-SHOT `printf '%s' "$json" >
#     "$file"` from a fully-constructed variable. NEVER a heredoc — this repo's
#     own command-review tribunal denies a heredoc-shaped `cat` write to a
#     scratch `.claude/settings.json` path while the identical content via a
#     single printf succeeds immediately (verified live this session). A denied
#     write here means the probe's marker is never planted and Tier D reports
#     "did-not-fire" — indistinguishable from a genuine regression.
#
# ── HONEST LIMIT ──────────────────────────────────────────────────────────
# A one-shot `-p` spawn exercises the `startup` source only — it does NOT
# exercise `resume` / `clear` / `compact` (no CLI trigger fires those without an
# existing session to act on). Tier D proves the host binary dispatches
# SessionStart for real; it says nothing about the other three sources.
#
# ── PER-HOST SCOPE (plan.md §1.3) ───────────────────────────────────────────
# Only claude-code and copilot have a verified one-shot, non-interactive,
# scratch-scoped spawn mechanism (`claude -p` / `copilot -p`). codex (hook
# trust-by-hash — a freshly-written scratch config is untrusted by
# construction), cursor (no verified one-shot invocation; fails OPEN on a
# malformed hook response, so an inconclusive D result there is actively
# misleading), and gemini (CLI presence unestablished on the dev machine) are
# all declared Tier A in §1.3 — Tier D for them is a documented non-goal here,
# not a silent gap.

# _rc_canary_tier_d_hosts — the only hosts with a built mechanism. Single
# source of truth for both the availability check and the CLI-name lookup, so
# they cannot silently disagree about which hosts are in scope.
_rc_canary_tier_d_cli_for() {
  case "$1" in
    claude-code) printf '%s\n' "claude" ;;
    copilot) printf '%s\n' "copilot" ;;
    *) return 1 ;;
  esac
}

# _rc_canary_tier_d_write_probe PROBE TOKEN MARKER — plant the marker-writer.
# Values are baked in directly (not via env-var indirection) so the check does
# not depend on an untested assumption that a host's real binary propagates
# arbitrary parent-process env vars all the way down into its own internally
# spawned hook subprocess — a chain Tier A never has to cross (its "spawn" is
# our own direct invocation of the adapter script).
_rc_canary_tier_d_write_probe() {
  local probe="$1" token="$2" marker="$3"
  printf '%s\n' '#!/usr/bin/env bash' >"$probe"
  printf 'printf "%%s\\n" "%s" > "%s"\n' "$token" "$marker" >>"$probe"
  printf '%s\n' 'exit 0' >>"$probe"
  chmod +x "$probe" 2>/dev/null
}

# _rc_canary_tier_d_write_config HOST SCRATCH PROBE — wire ONLY the planted
# probe on SessionStart into a scratch project's hook config. Property 4:
# every write here is a single-shot `printf '%s' "$json" > "$file"` from a
# fully-constructed variable — no heredoc anywhere in this function.
_rc_canary_tier_d_write_config() {
  local host="$1" scratch="$2" probe="$3" dir file json
  case "$host" in
    claude-code)
      dir="$scratch/.claude"
      mkdir -p "$dir" 2>/dev/null || return 1
      file="$dir/settings.json"
      json=$(printf '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"bash \\"%s\\""}]}]}}' "$probe")
      printf '%s' "$json" >"$file"
      ;;
    copilot)
      dir="$scratch/.github/hooks"
      mkdir -p "$dir" 2>/dev/null || return 1
      # `.github/hooks/NAME.json` is repository-scoped; git-init the scratch
      # dir so Copilot resolves it as a repository rather than an ad-hoc path.
      command -v git >/dev/null 2>&1 && git init -q "$scratch" >/dev/null 2>&1
      file="$dir/tier-d-probe.json"
      json=$(printf '{"version":1,"hooks":{"SessionStart":[{"type":"command","bash":"bash \\"%s\\"","timeoutSec":8}]}}' "$probe")
      printf '%s' "$json" >"$file"
      ;;
    *)
      return 1
      ;;
  esac
  [ -s "$file" ]
}

# _rc_canary_tier_d_spawn HOST SCRATCH — the bounded, tool-less one-shot spawn.
# `cd` into the scratch dir in a SUBSHELL (never the caller's shell) so
# property 1 holds even if a future edit forgets to pass an explicit cwd flag.
_rc_canary_tier_d_spawn() {
  local host="$1" scratch="$2"
  case "$host" in
    claude-code)
      ( cd "$scratch" 2>/dev/null && _rc_timeout 25 claude -p "reply with just the word OK" --tools "" ) >/dev/null 2>&1
      return $?
      ;;
    copilot)
      ( cd "$scratch" 2>/dev/null && _rc_timeout 25 copilot -C "$scratch" -p "reply with just the word OK" --model auto --allow-all-tools --deny-tool write --deny-tool shell --silent --output-format text ) >/dev/null 2>&1
      return $?
      ;;
    *)
      return 1
      ;;
  esac
}

# _rc_host_tier_d_canary HOST [PROJECT] — the Tier D entry point.
#
# Return codes (distinct from both _rc_host_canary's 0/1/2 and
# _rc_host_sessionstart_canary's 0/1/2/3 — a caller must never have to guess
# which lane produced a given code):
#   0  the host's own binary dispatched SessionStart for real (marker fired)
#   1  SKIP — tier D unavailable for this host, CLI absent, or kill-switched
#      (RC_SELFTEST_TIER=a). Falls back to tier A. NEVER silent.
#   2  the spawn ran (CLI present, scratch config wired) but the marker did
#      NOT fire — a candidate regression on the host's real dispatch path
#   3  HARNESS error (scratch provisioning / config write failed) — NOT a
#      dispatch verdict; must not be conflated with 2 (property 2)
_rc_host_tier_d_canary() {
  local host="${1:-}" project="${2:-$PWD}"
  local cli scratch outdir token marker probe rc marker_ok
  [ -n "$host" ] || return 1

  case "${RC_SELFTEST_TIER:-}" in
    [Aa])
      note "canary(tier-d): RC_SELFTEST_TIER=a — forced to tier A everywhere; skip (tier D unavailable) -> falls back to tier A"
      return 1
      ;;
  esac

  cli="$(_rc_canary_tier_d_cli_for "$host" 2>/dev/null)" || {
    note "canary(tier-d): $host has no built Tier D mechanism (declared tier A in plan.md §1.3) — skip (tier D unavailable) -> falls back to tier A"
    return 1
  }
  if ! command -v "$cli" >/dev/null 2>&1; then
    note "canary(tier-d): $host CLI ('$cli') not found on PATH — skip (tier D unavailable) -> falls back to tier A"
    return 1
  fi

  scratch="$(mktemp -d "${TMPDIR:-/tmp}/rc-canary-tier-d.XXXXXX" 2>/dev/null)" || {
    warn "canary(tier-d): $host could not create a scratch project dir — HARNESS error, not a dispatch verdict"
    return 3
  }
  outdir="$scratch/.rc-tier-d-out"
  mkdir -p "$outdir" 2>/dev/null || {
    warn "canary(tier-d): $host could not create the scratch output dir — HARNESS error, not a dispatch verdict"
    rm -rf "$scratch" 2>/dev/null
    return 3
  }
  token="rc-tier-d-$$-$RANDOM"
  marker="$outdir/marker"
  probe="$outdir/probe.sh"
  _rc_canary_tier_d_write_probe "$probe" "$token" "$marker"

  if ! _rc_canary_tier_d_write_config "$host" "$scratch" "$probe"; then
    warn "canary(tier-d): $host could not wire the scratch hook config — HARNESS error, not a dispatch verdict"
    rm -rf "$scratch" 2>/dev/null
    return 3
  fi

  _rc_canary_ensure_timeout
  # PROPERTY 1 — the scratch dir above is the ONLY cwd this spawn ever uses.
  _rc_canary_tier_d_spawn "$host" "$scratch"
  rc=$?

  marker_ok=0
  if [ -f "$marker" ] && [ "$(cat "$marker" 2>/dev/null)" = "$token" ]; then
    marker_ok=1
  fi
  rm -rf "$scratch" 2>/dev/null

  if [ "$marker_ok" -eq 1 ]; then
    ok "canary(tier-d): $host real session dispatched SessionStart (planted marker fired for real)"
    return 0
  fi
  warn "canary(tier-d): $host real session did NOT dispatch the planted SessionStart marker (spawn exit=$rc) — candidate regression on the host's own binary, not just the adapter seam."
  return 2
}

# _rc_canary_declared_tier HOST — the plan.md §1.3 declared tier for HOST
# (D | A | S). Single source of truth so a future caller (Phase 8's `rc hooks
# selftest`) and this phase's own anti-degradation acceptance test (A7.6)
# cannot silently disagree about what "declared D" means.
#
# copilot is declared D "if present, else A" (§1.3) — the "D" here is the
# ASPIRATION the ledger is judged against; A7.5 is what actually MEASURES
# whether a given run achieves it. That is the whole point of anti-degradation:
# declaring D is not the same as achieving it, and this function must not
# collapse that distinction by only ever returning what was last observed.
_rc_canary_declared_tier() {
  case "$1" in
    claude-code) printf 'D\n' ;;
    copilot) printf 'D\n' ;;
    codex) printf 'A\n' ;;
    cursor) printf 'A\n' ;;
    gemini) printf 'A\n' ;;
    grok) printf 'S\n' ;;
    *) printf 'A\n' ;;
  esac
}

# _rc_canary_anti_degradation DECLARED ACHIEVED — plan.md §1.3's invariant,
# implemented as real code rather than left as prose: "A tier-A pass on a
# host whose declared tier is D is a FAIL — this is the anti-silent-
# degradation clause, and it is what stops the harness from failing toward
# green." Prints PASS or FAIL to stdout (never silent) and returns 0/1 to
# match, so a caller can branch on either.
_rc_canary_anti_degradation() {
  local declared="${1:-}" achieved="${2:-}"
  if [ "$declared" = "D" ] && [ "$achieved" != "D" ]; then
    printf 'FAIL\n'
    return 1
  fi
  printf 'PASS\n'
  return 0
}
