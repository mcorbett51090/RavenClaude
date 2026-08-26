#!/usr/bin/env bash
# grok-delegate.sh — hand a well-defined task to the Grok CLI instead of spending
# Claude tokens on it. The mirror of claude-orchestrate.sh, pointed the other way.
#
# claude-orchestrate.sh routes a NON-Claude host's work TO Claude (buy quality).
# This routes a Claude host's everyday work OUT to Grok (buy cost).
#
# Usage:
#   grok-delegate.sh --task "<text>"        [--tier fast|balanced|top]
#   grok-delegate.sh --task-file <path>     [--mode advise|agent]
#                                           [--repo <dir>] [--timeout <secs>]
#                                           [--max-turns <n>]
#
# Exit codes (a caller treats ANY non-zero as "do it locally"):
#   0  ok — grok's output is on stdout
#   2  grok CLI absent, or a required arg is missing
#   4  grok returned non-zero
#   7  recursion guard fired (nested delegate, or inside a tribunal seat)
#   8  the task carried a secret — refused BEFORE egress, nothing was sent
#   9  agent mode asked for, but an isolated worktree could not be provisioned
#
# ⛔ CONTAINMENT IS THE WORKTREE, NOT GROK'S PERMISSION FLAGS.
# Measured on this host 2026-08-26, grok 1.0.4, each probe with a positive control
# proving it could return the other answer:
#   `--tools ""`                       -> read a canary file anyway  (an allowlist
#                                          with no entries means "no allowlist")
#   `--sandbox read-only`              -> WROTE a file anyway
#   `--sandbox read-only` (no bypass)  -> WROTE a file anyway (confound removed)
#   `--sandbox workspace`  (control)   -> wrote, as expected
#
# ⛔ CORRECTED 2026-08-26 — that conclusion was WRONG, and the flaw was the test,
# not grok. Every probe above ran inside
# /private/tmp/.../scratchpad/groktest — i.e. under `/private/tmp`, one of the
# paths `--sandbox read-only`'s OWN allowlist grants write access to (grok needs
# temp dirs for session bookkeeping). The "leak" was a write to a path the profile
# explicitly permits.
# control: re-ran read-only in a workspace OUTSIDE every allowlisted path
# (~/rc-scratch-outside-tmp — no /tmp, /var/tmp, or ~/.grok in it) -> write
# REFUSED; grok's own reply: "an environment restriction, not a missing-permission
# bit"; it fell back to /tmp rather than wrongly claiming success. Logged in
# ~/.grok/sandbox-events.jsonl:
#   {"event_type":"FsViolation","profile":"read-only","operation":"write",
#    "target":"/Users/matthewcorbett/rc-scratch-outside-tmp/wrote_real.txt"}
# Positive control, same location: `--sandbox workspace` -> write SUCCEEDED.
# Seatbelt (the macOS kernel primitive) really is enforcing this.
#
# `--tools ""` was a separate, real footgun and stays fixed: an EMPTY allowlist
# means "no allowlist", not "no tools" — a CLI-argument mistake, not a containment
# failure — so it is simply not passed below. `--disallowed-tools "Agent"` is the
# verified recursion guard.
#
# CONTAINMENT IS NOW TWO LAYERS, DELIBERATELY BOTH:
#   `--sandbox <profile>`  -> KERNEL-enforced (Seatbelt/Landlock). The real boundary.
#   worktree / scratch dir -> what grok can reach in the first place, and — for
#                              agent mode — the disposable branch reviewed before
#                              merging. Not a substitute for the sandbox; a second,
#                              independent layer, because a session-scoped kernel
#                              boundary and a git-scoped review boundary fail for
#                              different reasons.
# ⛔ Before changing either layer, re-run the outside-allowlist probe above and
# read ~/.grok/sandbox-events.jsonl — never trust a probe run inside a path the
# profile already allowlists.

set -uo pipefail

_self="$(basename "$0")"

# ── RECURSION GUARDS ──────────────────────────────────────────────────────────
# Layer 1: a delegate inside a delegate. Exported before the grok call below.
[ "${RAVENCLAUDE_GROK_ACTIVE:-0}" = "1" ] && {
  echo "$_self: RAVENCLAUDE_GROK_ACTIVE guard fired — re-entrant delegation refused" >&2; exit 7; }
# Layer 2: never delegate from inside a tribunal seat — a seat's verdict must not
# depend on a second vendor's availability.
[ "${THING_SEAT_ACTIVE:-0}" = "1" ] && {
  echo "$_self: THING_SEAT_ACTIVE guard fired — refused inside a tribunal seat" >&2; exit 7; }
# Layer 3 is structural and lives at the call site: --disallowed-tools "Agent"
# stops grok spawning its own subagents, so the tree cannot fan out unbounded.

# ── args ──────────────────────────────────────────────────────────────────────
task=""; task_file=""; tier="balanced"; mode="advise"; repo=""; timeout_s=600; max_turns=30
while [ $# -gt 0 ]; do
  case "$1" in
    --task)       task="${2:-}"; shift 2 ;;
    --task-file)  task_file="${2:-}"; shift 2 ;;
    --tier)       tier="${2:-}"; shift 2 ;;
    --mode)       mode="${2:-}"; shift 2 ;;
    --repo)       repo="${2:-}"; shift 2 ;;
    --timeout)    timeout_s="${2:-}"; shift 2 ;;
    --max-turns)  max_turns="${2:-}"; shift 2 ;;
    -h|--help)    sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "$_self: unknown arg '$1'" >&2; exit 2 ;;
  esac
done

if [ -n "$task_file" ]; then
  [ -r "$task_file" ] || { echo "$_self: --task-file not readable: $task_file" >&2; exit 2; }
  task="$(cat "$task_file")"
fi
[ -n "$task" ] || { echo "$_self: --task or --task-file is required" >&2; exit 2; }
case "$mode" in advise|agent) : ;; *) echo "$_self: --mode must be advise|agent" >&2; exit 2 ;; esac
case "$timeout_s" in ''|*[!0-9]*) timeout_s=600 ;; esac
case "$max_turns" in ''|*[!0-9]*) max_turns=30 ;; esac

command -v grok >/dev/null 2>&1 || { echo "$_self: grok CLI not found — run it locally" >&2; exit 2; }

# ── helpers, sourced fail-safe ────────────────────────────────────────────────
_dir="$(cd "$(dirname "$0")" && pwd)"
[ -f "$_dir/../hooks/_portable.sh" ] && . "$_dir/../hooks/_portable.sh" 2>/dev/null || true
# ⛔ Degrade to UNBOUNDED, never to "don't run". A missing helper must not silently
# turn a delegation into a no-op that sends the work back to Claude unnoticed.
command -v _rc_timeout >/dev/null 2>&1 || _rc_timeout() { shift; "$@"; }
[ -f "$_dir/../hooks/_scrub.sh" ] && . "$_dir/../hooks/_scrub.sh" 2>/dev/null || true

# ── EGRESS SECRET BACKSTOP — refuse BEFORE the task leaves this machine ────────
# Grok is a SECOND vendor. A secret in the brief is a disclosure to a party the
# user did not choose when they typed it. Refuse locally; never transmit and warn.
# ⛔ _scrub_reason takes ONE ARGUMENT — it does NOT read stdin. Piping to it
# returns the EMPTY STRING, which compares unequal to the task and refuses
# EVERY delegation as "secret detected". That shipped here for one test cycle
# and was caught only by a live end-to-end run: the guard test passed for the
# wrong reason (it returns 8 for all input), and the control I paired it with
# set the recursion env var, so it short-circuited BEFORE this block and never
# exercised this path at all. A control must isolate the SAME code path.
if command -v _scrub_reason >/dev/null 2>&1; then
  _scrubbed="$(_scrub_reason "$task" 2>/dev/null || printf '%s' "$task")"
  if [ "$_scrubbed" != "$task" ]; then
    echo "$_self: the task contains a secret-shaped literal — REFUSED before egress." >&2
    echo "$_self: nothing was sent to grok. Pass a path, not a value." >&2
    exit 8
  fi
fi

# ── tier -> model + effort, from the shared substrate map ─────────────────────
_map="$_dir/../knowledge/substrate-tier-map.json"
model=""; effort=""
if [ -r "$_map" ] && command -v python3 >/dev/null 2>&1; then
  _resolved="$(python3 - "$_map" "$tier" <<'PY' 2>/dev/null || true
import json, sys
try:
    m = json.load(open(sys.argv[1]))
    row = (m.get("hosts", {}).get("grok", {}) or {}).get(sys.argv[2])
except Exception:
    row = None
if isinstance(row, dict):
    print("%s\t%s" % (row.get("model", ""), row.get("effort", "")))
elif isinstance(row, str):
    print("%s\t" % row)
PY
)"
  model="$(printf '%s' "$_resolved" | cut -f1)"
  effort="$(printf '%s' "$_resolved" | cut -f2)"
fi
# The map is the source of truth; this is only the floor if it is unreadable.
[ -n "$model" ] || model="grok-4.5"

# ── the isolated working directory (THE containment) ─────────────────────────
scratch=""; workdir=""
_cleanup() { [ -n "$scratch" ] && [ -d "$scratch" ] && rm -rf "$scratch" 2>/dev/null || true; }
trap _cleanup EXIT INT TERM

if [ "$mode" = "advise" ]; then
  # Nothing of the user's is reachable: an empty temp dir with no repo in it.
  scratch="$(mktemp -d)" || { echo "$_self: mktemp failed" >&2; exit 2; }
  workdir="$scratch"
else
  # agent mode — a DISPOSABLE git worktree. Never the user's checkout.
  [ -n "$repo" ] || repo="$PWD"
  git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || {
    echo "$_self: --mode agent needs a git repo (--repo DIR); refusing to run loose" >&2; exit 9; }
  _top="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "$_self: no git toplevel" >&2; exit 9; }
  _slug="grok-$(date +%Y%m%d-%H%M%S)-$$"
  workdir="$_top/.claude/worktrees/$_slug"
  git -C "$_top" worktree add -q -b "grok/$_slug" "$workdir" >/dev/null 2>&1 || {
    echo "$_self: could not provision a worktree — refusing to let grok touch the live checkout" >&2
    exit 9; }
  echo "$_self: agent mode — grok is confined to $workdir (branch grok/$_slug)" >&2
  echo "$_self: REVIEW THE DIFF before merging; grok's permission flags do not contain on this host." >&2
fi

# ── the call ──────────────────────────────────────────────────────────────────
# --sandbox is the KERNEL boundary (Seatbelt/Landlock) — verified above, not
# assumed. advise mode gets `read-only` (nothing should be written at all, and if
# the model tries, the kernel refuses it); agent mode gets `workspace` (writes
# confined to $workdir — the disposable worktree — plus grok's own state dir and
# temp, never the primary checkout).
# --disallowed-tools "Agent" is recursion layer 3: grok must not spawn its own
# subagents, or one delegation fans out into a tree nobody is counting.
# --max-turns bounds the agent loop — the cost control that makes this worth doing.
sandbox_profile="read-only"
[ "$mode" = "agent" ] && sandbox_profile="workspace"
set -- --cwd "$workdir" --sandbox "$sandbox_profile" --model "$model" \
       --disallowed-tools "Agent" --max-turns "$max_turns"
[ -n "$effort" ] && set -- "$@" --effort "$effort"
[ "$mode" = "agent" ] && set -- "$@" --permission-mode acceptEdits

RAVENCLAUDE_GROK_ACTIVE=1 \
_rc_timeout "$timeout_s" grok "$@" -p "$task"
_rc=$?

if [ "$_rc" -ne 0 ]; then
  # 124 GNU timeout, 142 perl alarm.
  case "$_rc" in
    124|142) echo "$_self: grok exceeded ${timeout_s}s — falling back to local" >&2 ;;
    *)       echo "$_self: grok exited $_rc — falling back to local" >&2 ;;
  esac
  [ "$mode" = "agent" ] && echo "$_self: worktree left at $workdir for inspection" >&2
  exit 4
fi

if [ "$mode" = "agent" ]; then
  echo "$_self: --- what grok changed (review before merging) ---" >&2
  git -C "$workdir" --no-pager diff --stat HEAD >&2 2>/dev/null || true
  # Do NOT clean up an agent worktree: its diff is the deliverable.
  scratch=""
fi
exit 0
