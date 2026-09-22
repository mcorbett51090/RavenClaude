#!/usr/bin/env bash
# alias-deprecation-advisory.sh — SessionStart soak advisory for posture aliases.
#
# When a consumer posture still relies on deprecated keys
# (`handoff_tax.pin_explore`, `model_tier_surfaces.*`) as the effective source
# (or they diverge from `model_matrix.surfaces.*`), emit a one-line deprecation
# notice via additionalContext. Quiet when seed leftovers match the new keys.
#
# NOT a Stop/per-turn nag. Joins the existing SessionStart matcher group.
# Never writes posture (House Rule 3). Always exits 0; SessionStart cannot block.
#
# Once-per-session: marker under .ravenclaude/runs/<session_id>/ so resume/clear
# re-fires of SessionStart do not re-nag within the same session id.

set -uo pipefail

_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
# Forced exit 0 (SessionStart never blocks). 3rd arg empty = also show UI notice.
if [ -f "$_rc_hd/_advise.sh" ]; then . "$_rc_hd/_advise.sh"; rc_advise_init SessionStart 0; fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$PROJECT_DIR/.ravenclaude/comfort-posture.yaml"
[ -f "$CFG" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

ENGINE="${CLAUDE_PLUGIN_ROOT:-}/scripts/alias-deprecation-advisory.py"
if [ ! -f "$ENGINE" ]; then
  ENGINE="$_rc_hd/../scripts/alias-deprecation-advisory.py"
fi
[ -f "$ENGINE" ] || exit 0

# Session marker — prefer CLAUDE_SESSION_ID, else stdin .session_id.
SID="${CLAUDE_SESSION_ID:-}"
INPUT=""
if [ -z "$SID" ] || [ -t 0 ]; then
  :
fi
# Always drain stdin (SessionStart payload); may also supply session_id.
INPUT="$(cat 2>/dev/null || true)"
if [ -z "$SID" ] && [ -n "$INPUT" ]; then
  SID="$(printf '%s' "$INPUT" | python3 -c '
import json,sys
try:
  d=json.load(sys.stdin)
  print(d.get("session_id") or d.get("sessionId") or "")
except Exception:
  print("")
' 2>/dev/null || true)"
fi
# Sanitize session id for path use (attacker-influenceable on some hosts).
SID="$(printf '%s' "$SID" | tr -cd 'A-Za-z0-9._-' | head -c 128)"
if [ -n "$SID" ]; then
  MARK_DIR="$PROJECT_DIR/.ravenclaude/runs/$SID"
  MARK="$MARK_DIR/alias-deprecation-advised"
  if [ -f "$MARK" ]; then
    exit 0
  fi
fi

NOTICE="$(python3 "$ENGINE" check --project "$PROJECT_DIR" 2>/dev/null)" || exit 0
[ -n "$NOTICE" ] || exit 0

# Deliver: _advise.sh buffers fd2 → additionalContext (+ UI notice) at EXIT.
printf '%s\n' "$NOTICE" >&2

if [ -n "$SID" ]; then
  mkdir -p "$MARK_DIR" 2>/dev/null || true
  : >"$MARK" 2>/dev/null || true
fi

exit 0
