#!/usr/bin/env bash
# runaway-brake.sh — PreToolUse deterministic runaway / rabbit-hole brake.
#
# Replaces the native Claude Code `auto`-mode 3-consecutive / 20-total block
# brake, which is Anthropic-API/Claude-only and therefore UNAVAILABLE under
# GitHub Copilot CLI (Claude + ChatGPT + Grok routing). This is the portable,
# model-agnostic equivalent: it counts tool calls per session and trips when the
# agent THRASHES (too many byte-identical calls in a row — the "looping on a
# fabricated error" rabbit-hole signal) or blows a generous total-call ceiling.
#
# No-ops (allow, exit 0) unless .ravenclaude/comfort-posture.yaml exists, so a
# non-adopter pays nothing (one stat). Opt out entirely with `runaway: off`.
# Tune with:
#   runaway:
#     max_consecutive: 8     # identical calls in a row before tripping
#     max_total: 1200         # total tool calls this session before tripping
#
# Deterministic: no model in the loop. Ports to Copilot via the bash-pretool
# adapter (a Claude exit-2 block -> a Copilot deny). State is a per-session
# counter file under .ravenclaude/runs/thing/runaway/ (the same per-session
# pattern the tribunal's fatigue counter uses); a new session_id starts fresh.

set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0
payload=""
[ ! -t 0 ] && payload="$(cat)"
[ -z "$payload" ] && exit 0

cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"
posture="${cwd}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0   # not opted in -> zero cost

# Explicit opt-out.
grep -Eq '^[[:space:]]*runaway:[[:space:]]*off[[:space:]]*$' "$posture" 2>/dev/null && exit 0

max_consec="$(sed -n 's/^[[:space:]]*max_consecutive:[[:space:]]*\([0-9]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
max_total="$(sed -n 's/^[[:space:]]*max_total:[[:space:]]*\([0-9]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$max_consec" ] && max_consec=8
[ -z "$max_total" ] && max_total=1200

sid="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)"
[ -z "$sid" ] && exit 0
safe_sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
[ -z "$safe_sid" ] && exit 0

dir="${cwd}/.ravenclaude/runs/thing/runaway"
mkdir -p "$dir" 2>/dev/null || exit 0
f="${dir}/${safe_sid}"

# Stable hash of this tool call (name + sorted input).
h="$(printf '%s' "$payload" | jq -cS '{t:(.tool_name//""),i:(.tool_input//{})}' 2>/dev/null | cksum | cut -d' ' -f1)"
[ -z "$h" ] && h="0"

total=0; last="-"; consec=0
if [ -r "$f" ]; then
  read -r total last consec < "$f" 2>/dev/null || { total=0; last="-"; consec=0; }
fi
case "$total" in (*[!0-9]*|"") total=0;; esac
case "$consec" in (*[!0-9]*|"") consec=0;; esac

total=$((total + 1))
if [ "$h" = "$last" ]; then consec=$((consec + 1)); else consec=1; fi
printf '%s %s %s\n' "$total" "$h" "$consec" > "$f" 2>/dev/null || true

trip=""
if [ "$consec" -ge "$max_consec" ]; then
  trip="repeated the same tool call ${consec} times in a row (limit ${max_consec})"
elif [ "$total" -ge "$max_total" ]; then
  trip="made ${total} tool calls this session (limit ${max_total})"
fi

if [ -n "$trip" ]; then
  printf '%s\n' "Runaway brake: the agent ${trip}. Paused to prevent a rabbit hole / runaway. Intervene, or raise the limit under \`runaway:\` in .ravenclaude/comfort-posture.yaml (or set \`runaway: off\`)." >&2
  exit 2
fi
exit 0
