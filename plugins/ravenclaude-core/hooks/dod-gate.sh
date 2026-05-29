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
dod_cmd="$(python3 - "$posture" <<'PY' 2>/dev/null || true
import sys
try:
    import yaml; d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
print(dod.get("cmd","") if isinstance(dod, dict) else "")
PY
)"
max_blocks="$(python3 - "$posture" <<'PY' 2>/dev/null || echo 8
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
)"
[ -z "$dod_cmd" ] && exit 0    # no DoD configured -> advisory remind-tests handles the nudge
case "$max_blocks" in (*[!0-9]*|"") max_blocks=8;; esac

# Only gate if source actually changed this session (mirror remind-tests' filter).
code_changed="$(git -C "$cwd" status --porcelain 2>/dev/null \
  | awk '$2 ~ /\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$/ {n++} END {print n+0}')"
[ "${code_changed:-0}" -eq 0 ] && exit 0

safe_sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
[ -z "$safe_sid" ] && safe_sid="stop"
bdir="${cwd}/.ravenclaude/runs/thing/dod"
mkdir -p "$bdir" 2>/dev/null || true
bf="${bdir}/${safe_sid}"
blocks=0
[ -r "$bf" ] && blocks="$(cat "$bf" 2>/dev/null || echo 0)"
case "$blocks" in (*[!0-9]*|"") blocks=0;; esac

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
