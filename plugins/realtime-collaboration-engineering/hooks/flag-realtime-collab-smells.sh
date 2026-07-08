#!/usr/bin/env bash
# flag-realtime-collab-smells.sh — advisory PreToolUse hook for the realtime-collaboration-engineering plugin.
# Flags mechanically-detectable collaborative-systems design smells on Edit/Write/MultiEdit of .md/.txt files.
# Advisory by default (exit 0, prints a notice); set RTC_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect prose files where these patterns are meaningful.
case "$file" in
  *.md | *.txt) ;;
  *) exit 0 ;;
esac

findings=()

# 1. A merge-model design that names CRDT/OT but never names a consistency/merge guarantee.
if grep -nEi 'crdt|operational transform|\bot\b|merge model|conflict[- ]free' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'eventual consistency|strong eventual|server[- ]authoritative|last[- ]writer|converge|intention preserv|causal' "$file" >/dev/null 2>&1; then
    findings+=("A merge-model design (CRDT/OT) with no consistency guarantee named — state server-authoritative vs strong eventual consistency, and what 'merged' means on conflict (see choose-crdt-or-ot).")
  fi
fi

# 2. A presence/cursor feature with no sign it is kept separate/ephemeral from the document.
if grep -nEi 'presence|awareness|live cursor|cursors?|selection( range)?|who.?s (here|online)' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'ephemeral|separate channel|out of the document|expire|throttl|last[- ]write[- ]wins' "$file" >/dev/null 2>&1; then
    findings+=("A presence/cursor feature with no ephemeral/separate-channel handling noted — presence must be throttled, expiring, and kept OUT of the persisted document (see build-presence-and-awareness).")
  fi
fi

# 3. A specific library/protocol reference with no retrieval date or verify-at-use flag.
if grep -nEi 'yjs|automerge|loro|sharedb|liveblocks|partykit|webrtc|websocket|y-websocket|electricsql|convex|replicache' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'verify-at-use|retrieved|as of|20[0-9]{2}-[0-9]{2}|20[0-9]{2}' "$file" >/dev/null 2>&1; then
    findings+=("A library/protocol reference with no retrieval date or verify-at-use flag — realtime tooling is volatile; add a date + [verify-at-use] (see realtime-collab-tooling-2026.md).")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── realtime-collaboration-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${RTC_STRICT:-0}" = "1" ]; then
  echo "(blocking: RTC_STRICT=1)" >&2
  exit 2
fi
exit 0
