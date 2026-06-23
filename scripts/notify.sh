#!/usr/bin/env bash
# notify.sh
# Notification CHANNEL for this marketplace's own sessions (marketplace-only —
# registered in .claude/settings.json under hooks.Notification, NOT in any
# plugin's hooks.json, so it never ships to consumers).
#
# Why this exists: in a Claude Code on-the-web / scheduled-routine session the
# managed PushNotification tool may be absent (it is, in this environment), so a
# routine that finds something worth surfacing has no built-in way to reach the
# maintainer. This script is the egress: it fires on the Claude Code
# `Notification` hook event and delivers the notification message to a
# configurable sink, while always leaving a durable local record.
#
# It is also invocable directly so an agent routine can push an ad-hoc summary:
#   echo "3 new auth errors since the 14:32 deploy — see PR #475" | scripts/notify.sh
#   scripts/notify.sh "one-line summary as an argument"
#
# Sinks (both best-effort, both fail-safe):
#   1. ALWAYS — append one JSON line to
#        ${CLAUDE_PROJECT_DIR:-.}/.ravenclaude/runs/notifications/YYYY-MM-DD.jsonl
#      (that dir is gitignored, so this never pollutes the working tree). This is
#      the always-on record even when no remote sink is configured.
#   2. OPT-IN — if RAVENCLAUDE_NOTIFY_WEBHOOK is set, POST {"text":"<message>"}
#      to it (Slack / Mattermost / Google-Chat-style incoming webhook). Set it
#      to your channel's webhook URL to receive pushes; unset, this step no-ops.
#
# Design invariants (mirrors the repo's other hooks):
#   * FAIL-SAFE — every step is best-effort; any failure (no jq, no curl, no
#     network, unwritable path) is swallowed. A notification must never block or
#     break the session that triggered it.
#   * ALWAYS exits 0.
#   * No secrets in the log line; the webhook URL is read from the env, never
#     echoed.
set -uo pipefail

proj="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Resolve the message: stdin payload (Notification hook JSON) → $1 → raw stdin.
payload=""
if [ ! -t 0 ]; then payload="$(cat 2>/dev/null || true)"; fi
msg=""
if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  msg="$(printf '%s' "$payload" | jq -r '.message // .summary // empty' 2>/dev/null || true)"
fi
if [ -z "$msg" ] && [ "$#" -gt 0 ]; then msg="$*"; fi
if [ -z "$msg" ] && [ -n "$payload" ]; then msg="$payload"; fi
if [ -z "$msg" ]; then msg="(empty notification)"; fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
day="$(date -u +%Y-%m-%d)"

# Sink 1 — durable local record (always).
logdir="${proj}/.ravenclaude/runs/notifications"
mkdir -p "$logdir" 2>/dev/null || true
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg ts "$ts" --arg msg "$msg" \
    '{ts:$ts, message:$msg}' >>"${logdir}/${day}.jsonl" 2>/dev/null || true
else
  printf '{"ts":"%s","message":"%s"}\n' "$ts" "${msg//\"/\\\"}" \
    >>"${logdir}/${day}.jsonl" 2>/dev/null || true
fi

# Sink 2 — remote push (opt-in via RAVENCLAUDE_NOTIFY_WEBHOOK).
hook_url="${RAVENCLAUDE_NOTIFY_WEBHOOK:-}"
if [ -n "$hook_url" ] && command -v curl >/dev/null 2>&1; then
  if command -v jq >/dev/null 2>&1; then
    body="$(jq -cn --arg t "$msg" '{text:$t}' 2>/dev/null || printf '{"text":"%s"}' "${msg//\"/\\\"}")"
  else
    body="$(printf '{"text":"%s"}' "${msg//\"/\\\"}")"
  fi
  curl -fsS --connect-timeout 5 -m 10 -X POST -H 'Content-Type: application/json' \
    -d "$body" "$hook_url" >/dev/null 2>&1 || true
fi

exit 0
