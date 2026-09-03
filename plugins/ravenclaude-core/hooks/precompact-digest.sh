#!/usr/bin/env bash
# precompact-digest.sh — PreCompact hook (archival only).
#
# Fires just before Claude Code (or, per its documented schema, any host
# projecting the same PreCompact event) compacts the session. Reads the
# PreCompact stdin payload, and if it carries a `transcript_path`, launches
# P1's digest engine (../scripts/precompact-digest.py) DETACHED to extract a
# curated critical-info digest before the compaction boundary,
# writing it to .ravenclaude/runs/<session>/precompact-digest-<timestamp>.md.
#
# P2 of the precompact-critical-context FORGE plan
# (.ravenclaude/runs/forge/precompact-critical-context/plan.md).
# Hardened per the P4 security review
# (.ravenclaude/runs/forge/precompact-critical-context/security-review-p4.md):
#
# B1 — POSTURE GATE (this file). `cheap_lane.mode` absent or `off` in
# .ravenclaude/comfort-posture.yaml => this hook is FULLY INERT: it writes
# nothing, calls nothing, and exits 0 before even resolving the digest
# engine. This is the same "absent ⇒ off" contract every opt-in knob in this
# repo uses (cheap_lane itself, decision_review, orchestrator, ...) — the
# feature literally reuses the cheap lane as its transport, so it is gated
# by the SAME knob rather than inventing a second one. The fail-closed
# EGRESS FLOOR (orchestrator_repo_pii: false OR cheap_lane_zdr_confirmed:
# true) is a SEPARATE, second gate, enforced inside the Python engine's
# extract_digest() — even with cheap_lane on, no byte leaves this machine
# unless that floor is also open. See precompact-digest.py's own header.
#
# B2 — DETACHED, NEVER a short synchronous ceiling. The prior design ran the
# engine under a 10s `_rc_timeout`, far below the engine's own 60s/90s
# subprocess budgets and real cold-start times (~24-29s) — so on the real
# path NO digest was EVER produced, while the transmission to the external
# processor still happened before the reader was killed (data left, no
# benefit arrived — proven with a sentinel in the P4 review). Fixed by
# launching the engine as a background, disowned worker and returning
# WITHOUT waiting on it or killing it on any timer. The worker still
# respects the ENGINE's OWN internal timeouts (60s cheap-lane / 90s
# fallback, set in precompact-digest.py) — this hook adds no ceiling of its
# own on top of those. `setsid` is used when available (Linux); stock macOS
# ships no `setsid` binary (the same tool-absence class as GNU `timeout` —
# see _portable.sh), so the fallback is the standard "background inside a
# subshell that itself exits immediately" daemonize idiom: the worker is
# reparented once its immediate parent (the launching subshell) exits, and
# is never part of THIS hook process's own job-control group, so it is never
# killed when this hook returns. No zombie is created either way — this
# hook never `wait`s on the worker, so its exit status is simply never
# collected here, which is the intended fire-and-forget contract.
#
# C5 (folds into B1) — a derived-values-only audit event is emitted for
# EVERY egress attempt AND every floor-block, via the shared
# `_emit_hook_event` (hooks/_emit-event.sh), from INSIDE the detached
# worker (after checking the engine's small JSON receipt) — never from the
# engine itself, and never containing digest/transcript content.
#
# ⛔ FIRE-AND-FORGET BY DESIGN — THIS MUST NEVER BLOCK A TURN.
# ------------------------------------------------------------
# `PreCompact` on Claude Code CAN block via `exit 2` (CLAUDE.md v0.244.1,
# `[docs-verified 2026-08-12]`) — this hook deliberately never does. This is
# archival, not gating: claim 20 in the precompact-critical-context
# claims-table proves PreCompact's `systemMessage`/`stopReason`/exit-code are
# a VERIFIED NO-OP on VS Code Copilot Chat — `executePreCompactHook()` has no
# consumer for any of them, and PreCompact never fires there on a manual
# `/compact` at all. So a hook that tried to warn or block through this event
# would be a silent no-op on that host, and an ACTUAL block on Claude Code —
# the only contract that is safe on BOTH hosts is "write a file, never object."
#
# `precompact-digest.py` itself may exit 3 (no digest written — either the
# egress floor blocked it, the excerpt was empty, or both extraction paths
# failed/were refused). That is an expected, non-fatal outcome: no digest is
# written, and this hook still exits 0 exactly as it would on success — the
# worker treats it as "no digest, but never block", per the engine's own
# contract. Because the worker is detached, this hook's own exit code is
# ALWAYS 0 (or an early inert exit) — it never depends on the engine at all.
#
# Follows this repo's own hook-authoring discipline (see compact-anchor.sh,
# the sibling this pairs with, and its digest-pointer extension in P2b): EXIT
# trap armed FIRST, before anything can abort; no `set -e` (a failed command
# must never become a non-zero exit the harness could misread as a block);
# bash 3.2-safe (no `declare -A` / `mapfile` / `${x^^}` / `shopt -s globstar`);
# no GNU-only `timeout` / `grep -P` / `sed -i`.
trap 'exit 0' EXIT
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || exit 0

# Sourced fail-safe helper for the audit-event emit (B1 C5). Absent helper ->
# a no-op stub, so a partial/corrupted install never turns a missing sourced
# file into a hard failure; the digest archival itself still proceeds.
_pcd_emit_helper="$here/_emit-event.sh"
[ -f "$_pcd_emit_helper" ] && . "$_pcd_emit_helper" 2>/dev/null || true
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

command -v python3 >/dev/null 2>&1 || exit 0

# Resolve the digest engine: ${CLAUDE_PLUGIN_ROOT} when installed, else in-repo
# (mirrors compact-anchor.sh's own resolution, one directory over).
engine="${CLAUDE_PLUGIN_ROOT:-}/scripts/precompact-digest.py"
[ -f "$engine" ] || engine="$here/../scripts/precompact-digest.py"
[ -f "$engine" ] || exit 0

payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

# Extract `transcript_path` + `session_id` from the trusted PreCompact payload
# (claims-table row 3: {timestamp, cwd, session_id, hook_event_name,
# transcript_path} — all but hook_event_name optional). jq is preferred; a
# conservative grep fallback mirrors _emit-event.sh's own no-jq shape so a
# jq-less host degrades rather than going dark.
transcript_path=""
session_id=""
if command -v jq >/dev/null 2>&1; then
  transcript_path="$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null || true)"
  session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
else
  transcript_path="$(printf '%s' "$payload" \
    | grep -o '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]*"' 2>/dev/null \
    | head -n1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null || true)"
  session_id="$(printf '%s' "$payload" \
    | grep -o '"session_id"[[:space:]]*:[[:space:]]*"[^"]*"' 2>/dev/null \
    | head -n1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' 2>/dev/null || true)"
fi

# transcript_path is OPTIONAL on the documented payload — absent means
# nothing to archive, not an error.
[ -z "$transcript_path" ] && exit 0
[ -f "$transcript_path" ] || exit 0

# Path-safe session token. MUST mirror _emit-event.sh's _ee_sanitize_session
# AND compact-anchor.py's reader (P2b) — the three derivations have to agree,
# or this hook writes into a run-dir the reader never looks in.
sid="$(printf '%s' "$session_id" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
case "$sid" in .|..|"") sid="unknown" ;; esac

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
export CLAUDE_PROJECT_DIR="$project_dir"

# --------------------------------------------------------------------------
# B1 — posture gate. `cheap_lane.mode` absent or `off` => fully inert. Read
# with the same minimal-scalar sed idiom worktree-guard.sh / claude-orchestrate.sh
# already use for a top-level/nested comfort-posture.yaml key — no PyYAML.
# --------------------------------------------------------------------------
posture="$project_dir/.ravenclaude/comfort-posture.yaml"

_pcd_block() { # $1=top-level block key  $2=file
  sed -n "/^${1}:/,/^[^[:space:]]/p" "$2" 2>/dev/null
}
_pcd_scalar() { # $1=block key  $2=nested key  $3=file
  _pcd_block "$1" "$3" | sed -n "s/^[[:space:]]*${2}:[[:space:]]*//p" \
    | sed -E 's/[[:space:]]*#.*$//; s/[[:space:]]+$//' | head -1
}

cheap_lane_mode="$(_pcd_scalar cheap_lane mode "$posture" 2>/dev/null || true)"
case "$cheap_lane_mode" in
  ""|off|Off|OFF) exit 0 ;;
esac

run_dir="$project_dir/.ravenclaude/runs/$sid"
mkdir -p "$run_dir" 2>/dev/null || exit 0

ts="$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || echo unknown)"
out_path="$run_dir/precompact-digest-$ts.md"
receipt_path="$run_dir/.precompact-digest-$ts.receipt.json"

# --------------------------------------------------------------------------
# B2 — the detached worker. Runs the engine to completion (bounded only by
# the engine's OWN internal per-call timeouts), then reads the small
# derived-values-only receipt the engine wrote and forwards it to
# _emit_hook_event (C5) — all AFTER this hook has already returned.
# --------------------------------------------------------------------------
_pcd_worker() {
  python3 "$engine" \
    --input "$transcript_path" \
    --out "$out_path" \
    --receipt "$receipt_path" \
    >/dev/null 2>&1

  [ -f "$receipt_path" ] || return 0

  local destination bytes outcome attempted
  if command -v jq >/dev/null 2>&1; then
    destination="$(jq -r '.destination // "none"' "$receipt_path" 2>/dev/null || echo none)"
    bytes="$(jq -r '.bytes_sent // 0' "$receipt_path" 2>/dev/null || echo 0)"
    outcome="$(jq -r '.outcome // "unknown"' "$receipt_path" 2>/dev/null || echo unknown)"
    attempted="$(jq -r '.attempted // false' "$receipt_path" 2>/dev/null || echo false)"
  else
    destination="$(grep -o '"destination"[[:space:]]*:[[:space:]]*"[^"]*"' "$receipt_path" 2>/dev/null \
      | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')"
    bytes="$(grep -o '"bytes_sent"[[:space:]]*:[[:space:]]*[0-9]*' "$receipt_path" 2>/dev/null \
      | head -1 | sed 's/.*:[[:space:]]*//')"
    outcome="$(grep -o '"outcome"[[:space:]]*:[[:space:]]*"[^"]*"' "$receipt_path" 2>/dev/null \
      | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')"
    attempted="$(grep -o '"attempted"[[:space:]]*:[[:space:]]*[a-z]*' "$receipt_path" 2>/dev/null \
      | head -1 | sed 's/.*:[[:space:]]*//')"
    [ -n "$destination" ] || destination="none"
    [ -n "$bytes" ] || bytes=0
    [ -n "$outcome" ] || outcome="unknown"
    [ -n "$attempted" ] || attempted="false"
  fi

  rm -f "$receipt_path" 2>/dev/null || true

  # Only emit for the two cases the review asked for: a real egress attempt
  # (cheap-lane or claude-fallback was actually invoked, whether it
  # succeeded or not) or a floor-block. A merely-empty excerpt (nothing to
  # send, nothing blocked) emits nothing — there is no event to report.
  case "$outcome" in
    blocked)
      _emit_hook_event "precompact-digest.sh" "deny" "PreCompact" "none" \
        "precompact-egress-floor-blocked produced=none" 0 2>/dev/null || true
      ;;
    ok|refused|unavailable)
      if [ "$outcome" = "refused" ]; then
        # A secret was detected in transcript-derived content on its way to an
        # external model, and egress was refused. That is a CONTROL FIRING, and a
        # control firing is a deny. Additive: the receipt below is unchanged.
        _emit_hook_event "precompact-digest.sh" "deny" "PreCompact" "none" \
          "precompact-secret-refusal produced=none" 0 2>/dev/null || true
      fi
      if [ "$attempted" = "true" ]; then
        _emit_hook_event "precompact-digest.sh" "allow" "PreCompact" "$destination" \
          "precompact-egress-attempt bytes=${bytes} outcome=${outcome}" 0 2>/dev/null || true
      fi
      ;;
  esac
  return 0
}

# Portable fire-and-forget daemonize: background the worker INSIDE a subshell
# that itself exits immediately. This is the "setsid or equivalent" this
# hook needs — genuine `setsid` is a Linux-only binary (absent on stock
# macOS, the same tool-absence class as GNU `timeout`; see _portable.sh), so
# rather than depend on a tool that is not universally present, this uses
# the standard portable idiom: `_pcd_worker` is backgrounded (`&`) inside a
# `( ... )` subshell, and that subshell — which is this hook's only direct
# child — exits as soon as the fork completes. The grandchild worker is then
# reparented (to init/launchd or the nearest subreaper) rather than staying
# a job of THIS hook's own process, so it is never torn down when this hook
# returns, and this hook never blocks waiting on it either way.
( _pcd_worker </dev/null >/dev/null 2>&1 & ) 2>/dev/null

exit 0
