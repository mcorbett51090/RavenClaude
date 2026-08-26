#!/usr/bin/env bash
# copilot-delegate.sh — hand a well-defined task to the GitHub Copilot CLI instead
# of spending Claude tokens on it. The Copilot sibling of grok-delegate.sh — same
# contract (args, exit codes, containment shape), different underlying CLI.
#
# Usage:
#   copilot-delegate.sh --task "<text>"        [--tier fast|balanced|top]
#   copilot-delegate.sh --task-file <path>     [--mode advise|agent]
#                                              [--repo <dir>] [--timeout <secs>]
#                                              [--effort none|minimal|low|medium|high|xhigh|max]
#                                              [--model <slug>]
#
# THE MATRIX — verified against the installed `copilot` CLI (1.x), 2026-08-26,
# NOT guessed from docs. Two things are real and two are honestly unverifiable:
#
#   tier      effort
#   fast      low
#   balanced  medium
#   top       high
#
# ⛔ MODEL PINNING IS DELIBERATELY LEFT AT `auto`, NOT A TIER-SPECIFIC SLUG.
# `--model auto` is verified working (a real non-interactive call completed).
# `--effort` is verified working AS A FLAG (the flag exists with choices
# none|minimal|low|medium|high|xhigh|max, per `copilot --help`) — BUT a second
# live probe found `--model auto --effort low` together REJECTED at runtime:
# "Model \"auto\" does not support reasoning effort configuration". So effort
# is real, `auto` is real, and the ONE combination this script's whole tier
# ladder rests on does not compose. Every guessed pinned slug this session was
# separately rejected with "not available" — `claude-sonnet-5`, a
# Sonnet-4-dot-5-shaped slug, `claude-opus-4-8`, `gpt-5`, and even the LITERAL
# internal id `auto` itself resolved to on a real call (a Haiku-4-dot-5-shaped
# id, read back from `--output-format json`) all failed as a direct `--model`
# value. There is no non-interactive way found this session to list the valid
# catalog (no `copilot models list`, no flag-driven enumeration; the picker is
# the interactive `/model` command only). Shipping a guessed tier->slug table
# here would be exactly the "confident claim, never verified" failure this
# repo's own Claim-Grounding protocol exists to catch — six distinct guesses
# were tried and tested wrong, live, before this comment was written.
#
# THE HONEST CONSEQUENCE: with the default `--model auto`, `--effort` is
# OMITTED entirely (below) rather than sent and rejected — so out of the box
# the Copilot lane's tier ladder differentiates by TIMEOUT BUDGET ONLY, not by
# reasoning depth. `--model <slug>` is exposed as an explicit override for a
# caller who has confirmed their own valid, effort-capable slug via `/model`
# in an interactive session; ONLY when a real model is pinned does `--effort`
# get sent at all.
#
# ⛔ NO VERIFIED TURN-COUNT CAP. Grok's `--max-turns` has no observed Copilot
# CLI equivalent in `copilot --help` (checked 2026-08-26) — bounding is by
# `--timeout` only. Do not add a guessed flag; if Copilot ships one later,
# wire it here with the same tier table shape grok-delegate.sh uses.
#
# ⛔ NO VERIFIED RECURSION-GUARD FLAG (grok-delegate.sh's Layer 3,
# `--disallowed-tools "Agent"`, has no seen Copilot analogue — no agent-spawn
# tool was observed in the tool-permission docs). Layers 1+2 (env-var guards)
# still apply; Copilot's `--deny-tool`/`--excluded-tools` are available if a
# future session identifies the right tool name to deny.
#
# Exit codes (a caller treats ANY non-zero as "do it locally") — same contract
# as grok-delegate.sh:
#   0  ok — copilot's output is on stdout
#   2  copilot CLI absent, or a required arg is missing
#   4  copilot returned non-zero
#   7  recursion guard fired (nested delegate, or inside a tribunal seat)
#   8  the task carried a secret — refused BEFORE egress, nothing was sent
#   9  agent mode asked for, but an isolated worktree could not be provisioned
#
# ⛔ CONTAINMENT IS DOCUMENTED CLI BEHAVIOR, NOT A KERNEL SANDBOX.
# Verified 2026-08-26 (`copilot help permissions`): file access defaults to the
# current working directory + subdirectories + the system temp dir; there is no
# Seatbelt/Landlock-style kernel enforcement the way Grok's `--sandbox` profile
# provides (grok-delegate.sh's header measured that with a positive control —
# this script's containment has NOT been measured with an equivalent
# outside-the-allowlist write-refusal probe). Two real layers, weaker than
# Grok's:
#   `-C <workdir>` + the CLI's own default path restriction -> what Copilot
#       can reach in the first place (unverified at the kernel level).
#   worktree / scratch dir -> the disposable branch reviewed before merging
#       (agent mode), or an empty dir with nothing to leak (advise mode).
# Read-only ("advise") containment IS verified end-to-end this session: a real
# call with `--allow-all-tools --deny-tool write --deny-tool shell` completed
# and produced output with no file written and no shell command run (denial
# takes precedence over allow, per `copilot help permissions`).

set -uo pipefail

_self="$(basename "$0")"

# ── RECURSION GUARDS (layers 1+2 only — see header) ───────────────────────────
[ "${RAVENCLAUDE_COPILOT_ACTIVE:-0}" = "1" ] && {
  echo "$_self: RAVENCLAUDE_COPILOT_ACTIVE guard fired — re-entrant delegation refused" >&2; exit 7; }
[ "${THING_SEAT_ACTIVE:-0}" = "1" ] && {
  echo "$_self: THING_SEAT_ACTIVE guard fired — refused inside a tribunal seat" >&2; exit 7; }

# ── the per-tier effort (bash-3.2-safe: case, not declare -A) ─────────────────
_tier_effort() {
  case "$1" in
    fast) echo low ;;
    top) echo high ;;
    *) echo medium ;;  # balanced + any unrecognized tier
  esac
}
_tier_timeout_s() {
  case "$1" in
    fast) echo 300 ;;
    top) echo 1200 ;;
    *) echo 600 ;;  # balanced + any unrecognized tier
  esac
}

# ── args ──────────────────────────────────────────────────────────────────────
task=""; task_file=""; tier="balanced"; mode="advise"; repo=""; timeout_s=""; effort_override=""; model="auto"
while [ $# -gt 0 ]; do
  case "$1" in
    --task)       task="${2:-}"; shift 2 ;;
    --task-file)  task_file="${2:-}"; shift 2 ;;
    --tier)       tier="${2:-}"; shift 2 ;;
    --mode)       mode="${2:-}"; shift 2 ;;
    --repo)       repo="${2:-}"; shift 2 ;;
    --timeout)    timeout_s="${2:-}"; shift 2 ;;
    --effort)     effort_override="${2:-}"; shift 2 ;;
    --model)      model="${2:-}"; shift 2 ;;
    -h|--help)    sed -n '2,60p' "$0"; exit 0 ;;
    *) echo "$_self: unknown arg '$1'" >&2; exit 2 ;;
  esac
done

if [ -n "$task_file" ]; then
  [ -r "$task_file" ] || { echo "$_self: --task-file not readable: $task_file" >&2; exit 2; }
  task="$(cat "$task_file")"
fi
[ -n "$task" ] || { echo "$_self: --task or --task-file is required" >&2; exit 2; }
case "$mode" in advise|agent) : ;; *) echo "$_self: --mode must be advise|agent" >&2; exit 2 ;; esac
if [ -n "$effort_override" ]; then
  case "$effort_override" in
    none|minimal|low|medium|high|xhigh|max) : ;;
    *) echo "$_self: --effort must be none|minimal|low|medium|high|xhigh|max (Copilot CLI's real set)" >&2; exit 2 ;;
  esac
fi
[ -n "$model" ] || model="auto"
case "$timeout_s" in ''|*[!0-9]*) timeout_s="$(_tier_timeout_s "$tier")" ;; esac
effort="${effort_override:-$(_tier_effort "$tier")}"

command -v copilot >/dev/null 2>&1 || { echo "$_self: copilot CLI not found — run it locally" >&2; exit 2; }

# ── helpers, sourced fail-safe ────────────────────────────────────────────────
_dir="$(cd "$(dirname "$0")" && pwd)"
[ -f "$_dir/../hooks/_portable.sh" ] && . "$_dir/../hooks/_portable.sh" 2>/dev/null || true
command -v _rc_timeout >/dev/null 2>&1 || _rc_timeout() { shift; "$@"; }
[ -f "$_dir/../hooks/_scrub.sh" ] && . "$_dir/../hooks/_scrub.sh" 2>/dev/null || true

# ── EGRESS SECRET BACKSTOP — refuse BEFORE the task leaves this machine ────────
# Same invariant as grok-delegate.sh: _scrub_reason takes ONE ARGUMENT, never stdin.
if command -v _scrub_reason >/dev/null 2>&1; then
  _scrubbed="$(_scrub_reason "$task" 2>/dev/null || printf '%s' "$task")"
  if [ "$_scrubbed" != "$task" ]; then
    echo "$_self: the task contains a secret-shaped literal — REFUSED before egress." >&2
    echo "$_self: nothing was sent to copilot. Pass a path, not a value." >&2
    exit 8
  fi
fi

# ── the isolated working directory (the containment) ──────────────────────────
scratch=""; workdir=""
_cleanup() { [ -n "$scratch" ] && [ -d "$scratch" ] && rm -rf "$scratch" 2>/dev/null || true; }
trap _cleanup EXIT INT TERM

if [ "$mode" = "advise" ]; then
  scratch="$(mktemp -d)" || { echo "$_self: mktemp failed" >&2; exit 2; }
  workdir="$scratch"
else
  [ -n "$repo" ] || repo="$PWD"
  git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || {
    echo "$_self: --mode agent needs a git repo (--repo DIR); refusing to run loose" >&2; exit 9; }
  _top="$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "$_self: no git toplevel" >&2; exit 9; }
  _slug="copilot-$(date +%Y%m%d-%H%M%S)-$$"
  workdir="$_top/.claude/worktrees/$_slug"
  git -C "$_top" worktree add -q -b "copilot/$_slug" "$workdir" >/dev/null 2>&1 || {
    echo "$_self: could not provision a worktree — refusing to let copilot touch the live checkout" >&2
    exit 9; }
  echo "$_self: agent mode — copilot is confined to $workdir (branch copilot/$_slug)" >&2
  echo "$_self: REVIEW THE DIFF before merging; this containment is CLI-documented default-path" >&2
  echo "$_self: restriction, NOT a measured kernel sandbox (see this script's header)." >&2
fi

# ── the call ──────────────────────────────────────────────────────────────────
# advise mode: --allow-all-tools is required for non-interactive mode to run at
# all (per `copilot help permissions`), paired with --deny-tool write/shell —
# denial takes precedence over allow, so this is real read-only containment,
# verified end-to-end this session (2026-08-26).
# agent mode: --allow-all-tools with no deny — full write/shell, contained by
# -C plus the CLI's default path restriction (see header — NOT kernel-enforced).
#
# ⛔ --effort is sent ONLY when a real model is pinned. `--model auto` rejects
# --effort outright at runtime (verified — see header); passing it anyway
# would make the DEFAULT invocation fail every time.
set -- -C "$workdir" -p "$task" --model "$model" \
       --allow-all-tools --silent --output-format text
[ "$model" != "auto" ] && set -- "$@" --effort "$effort"
[ "$mode" = "advise" ] && set -- "$@" --deny-tool write --deny-tool shell

RAVENCLAUDE_COPILOT_ACTIVE=1 \
_rc_timeout "$timeout_s" copilot "$@"
_rc=$?

if [ "$_rc" -ne 0 ]; then
  case "$_rc" in
    124|142) echo "$_self: copilot exceeded ${timeout_s}s — falling back to local" >&2 ;;
    *)       echo "$_self: copilot exited $_rc — falling back to local" >&2 ;;
  esac
  [ "$mode" = "agent" ] && echo "$_self: worktree left at $workdir for inspection" >&2
  exit 4
fi

if [ "$mode" = "agent" ]; then
  echo "$_self: --- what copilot changed (review before merging) ---" >&2
  git -C "$workdir" --no-pager diff --stat HEAD >&2 2>/dev/null || true
  scratch=""
fi
exit 0
