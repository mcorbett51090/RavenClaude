#!/usr/bin/env bash
# dod-gate.sh — Stop-hook definition-of-done gate.
#
# Closes the "hallucinating" gap that command review cannot: it gates work
# CORRECTNESS, not command safety. If source files changed this session AND a
# `definition_of_done.cmd` is configured in .ravenclaude/comfort-posture.yaml,
# it runs that command (tests / build / lint) when the agent tries to STOP and
# BLOCKS the stop until the command passes — so "looks done" becomes "is done"
# without the human being the verification loop (Anthropic best-practices Layer 5).
#
# Self-limited: blocks at most `max_blocks` (default 8) consecutive times per
# session, then force-allows with a warning — Claude Code force-overrides Stop
# after 8, but Copilot CLI has no such guarantee, so the cap must be ours.
#
# No `definition_of_done.cmd` configured -> exit 0 (the advisory remind-tests.sh
# nudge still fires). No posture file -> zero cost. Deterministic: the gate is a
# command's exit code, no model in the loop, so it ports to Copilot unchanged via
# the adapter's `stop` mode. Config:
#   definition_of_done:
#     cmd: "npm test && npm run lint"
#     max_blocks: 8

set -uo pipefail

# Structured hook-event substrate (P0.2). Sourced fail-safe — a missing helper
# becomes a no-op so the emit calls below can never throw or block the verdict.
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

payload=""
[ ! -t 0 ] && payload="$(cat)"
cwd="$PWD"
sid="stop"
if command -v jq >/dev/null 2>&1 && [ -n "$payload" ]; then
  c="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"; [ -n "$c" ] && cwd="$c"
  s="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)"; [ -n "$s" ] && sid="$s"
fi

posture="${cwd}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0

# Pull definition_of_done.cmd + max_blocks (PyYAML with a tolerant fallback).
# Python read into a var + run via `python3 -c`, NOT a heredoc nested in `$()`
# (bash 3.2 mis-parses that nesting — see guard-destructive.sh + the
# audit-gates no-heredoc-in-cmd-substitution gate). read -d '' returns non-zero at EOF.
IFS= read -r -d '' __DOD_CMD_PY <<'PY' || true
import sys
try:
    import yaml; d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
print(dod.get("cmd","") if isinstance(dod, dict) else "")
PY
dod_cmd="$(python3 -c "$__DOD_CMD_PY" "$posture" 2>/dev/null || true)"
IFS= read -r -d '' __MAX_BLOCKS_PY <<'PY' || true
import sys
try:
    import yaml; d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
mb = dod.get("max_blocks", 8) if isinstance(dod, dict) else 8
try: mb = int(mb)
except Exception: mb = 8
print(mb)
PY
max_blocks="$(python3 -c "$__MAX_BLOCKS_PY" "$posture" 2>/dev/null || echo 8)"
[ -z "$dod_cmd" ] && exit 0    # no DoD configured -> advisory remind-tests handles the nudge
case "$max_blocks" in (*[!0-9]*|"") max_blocks=8;; esac

# Only gate if source actually changed this session (mirror remind-tests' filter).
# Use --porcelain=v1 -z: the NUL-delimited form emits each path as a RAW, UNQUOTED
# record (porcelain v1's default quotes/space-splits paths, so the prior awk `$2`
# field-parse silently missed any changed file with a space in its name, and split
# rename `old -> new` lines — under-counting to 0 and skipping the gate entirely).
# grep -c matches the extension as a whole-line suffix (not a fixed field), so
# spaces in the path are irrelevant; -z rename records emit old+new as separate
# raw records, both scanned — we only need whether ANY changed path is source.
code_changed="$(git -C "$cwd" status --porcelain=v1 -z 2>/dev/null \
  | tr '\0' '\n' \
  | grep -cE '\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$')" || true
[ "${code_changed:-0}" -eq 0 ] && exit 0

safe_sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
[ -z "$safe_sid" ] && safe_sid="stop"
bdir="${cwd}/.ravenclaude/runs/thing/dod"
mkdir -p "$bdir" 2>/dev/null || true
bf="${bdir}/${safe_sid}"
blocks=0
[ -r "$bf" ] && blocks="$(cat "$bf" 2>/dev/null || echo 0)"
case "$blocks" in (*[!0-9]*|"") blocks=0;; esac

# ── First-run trust gate (closes Codex desktop trust review Finding 1) ──────
# $dod_cmd is shell-executed via `bash -c` below, but it came from a YAML field
# (definition_of_done.cmd) that a malicious PR could edit. Before the very first
# run per session per cmd value, refuse to execute and surface the literal cmd
# plus the `touch <path>` authorization step. After the user/agent touches the
# confirm file, this gate is silent for the rest of the session for this cmd.
# Rotating the YAML cmd re-triggers (hash mismatch); a new session re-triggers
# (safe_sid in path). Set `definition_of_done.trusted: true` in posture YAML
# to skip the gate entirely (you've reviewed the YAML and accept silent exec).
IFS= read -r -d '' __DOD_TRUSTED_PY <<'PY' || true
import sys
try:
    import yaml
    d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
print("true" if (isinstance(dod, dict) and dod.get("trusted") is True) else "false")
PY
dod_trusted="$(python3 -c "$__DOD_TRUSTED_PY" "$posture" 2>/dev/null || echo "false")"

if [ "$dod_trusted" != "true" ]; then
  cmd_hash="$(printf '%s' "$dod_cmd" | sha256sum 2>/dev/null | cut -c1-16)"
  [ -z "$cmd_hash" ] && cmd_hash="nohash"
  confirm_dir="${cwd}/.ravenclaude/runs/dod-gate/${safe_sid}"
  confirm_file="${confirm_dir}/confirmed-${cmd_hash}"
  if [ ! -f "$confirm_file" ]; then
    mkdir -p "$confirm_dir" 2>/dev/null || true
    cat >&2 <<EOF

[dod-gate] FIRST-RUN TRUST CHECK — refusing to execute until authorized.

definition_of_done.cmd from .ravenclaude/comfort-posture.yaml:
  $dod_cmd

To authorize for this session (one-time, this cmd value):
  touch "$confirm_file"

To trust definition_of_done permanently for this repo (no further prompts):
  set 'definition_of_done.trusted: true' in .ravenclaude/comfort-posture.yaml

If you did NOT set this cmd, remove it from the YAML before doing anything else.

EOF
    _emit_hook_event "dod-gate.sh" "deny" "Stop" "$cmd_hash" "dod-first-run-untrusted" 2
    exit 2
  fi
fi

# Run the definition-of-done command.
out="$(cd "$cwd" && bash -c "$dod_cmd" 2>&1)"; rc=$?

if [ "$rc" -eq 0 ]; then
  rm -f "$bf" 2>/dev/null || true
  exit 0   # work is done — allow the stop
fi

blocks=$((blocks + 1))
printf '%s' "$blocks" > "$bf" 2>/dev/null || true

if [ "$blocks" -ge "$max_blocks" ]; then
  rm -f "$bf" 2>/dev/null || true
  printf '%s\n' "Definition-of-done still failing after ${blocks} attempts; releasing the Stop gate so the session can end. The gate command (\`${dod_cmd}\`) is NOT passing — review before relying on this work." >&2
  exit 0   # force-allow so we can't deadlock
fi

# Block the stop and feed the failing output back so the agent keeps working.
tail="$(printf '%s' "$out" | tail -c 1500 | tr -d '\000-\010\013\014\016-\037')"
reason="Definition-of-done not met (attempt ${blocks}/${max_blocks}). The gate command \`${dod_cmd}\` failed (exit ${rc}). Fix it before stopping:
${tail}"
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg r "$reason" '{decision:"block",reason:$r}'
else
  printf '%s\n' "$reason" >&2
  exit 2
fi
exit 0
