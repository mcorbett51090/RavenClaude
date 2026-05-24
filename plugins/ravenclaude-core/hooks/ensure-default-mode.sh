#!/usr/bin/env bash
# ensure-default-mode.sh
# SessionStart hook. The comfort-posture allow/ask/deny rules in
# .claude/settings.json only take effect when the session is in the "default"
# permission mode. If a session loads in a bypass mode (acceptEdits or
# bypassPermissions) — e.g. a sticky mode carried over via Shift+Tab or a
# launch flag — those rules are partially or fully ignored. This hook detects
# that and prints a one-line heads-up so the configured posture isn't silently
# overridden.
#
# It cannot CHANGE the mode (Claude Code does not expose mode-setting from a
# hook). The real guarantee is permissions.defaultMode="default", which the
# /set-posture translator writes into settings.json. This hook is the
# belt-and-suspenders warning for the mid-session-toggle case.
#
# Output goes to stderr — Claude sees it as a system notice, the user sees it
# in the transcript. Always exits 0 (advisory only; never blocks a session).

set -euo pipefail

# SessionStart delivers a JSON payload on stdin. Read it (non-blocking-safe).
input="$(cat 2>/dev/null || true)"
[[ -z "$input" ]] && exit 0

# Extract permission_mode. Prefer python3 (present in the devcontainer and most
# consumer environments); fall back to a tolerant grep so the hook degrades
# gracefully rather than erroring when python3 is absent.
mode=""
if command -v python3 >/dev/null 2>&1; then
  mode="$(
    printf '%s' "$input" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("permission_mode", "") or "")
except Exception:
    print("")
' 2>/dev/null || true
  )"
fi
if [[ -z "$mode" ]]; then
  # Fallback: pull the first "permission_mode": "<value>" out of the raw JSON.
  mode="$(printf '%s' "$input" \
    | grep -o '"permission_mode"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | head -n1 \
    | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' || true)"
fi

case "$mode" in
  acceptEdits | bypassPermissions)
    cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Session loaded in "$mode" mode.

  Your comfort-posture allow/ask/deny rules (.claude/settings.json) are
  partially or fully bypassed in this mode. Press Shift+Tab to return to
  "default" mode so the configured permission rules take effect.

  (permissions.defaultMode is pinned to "default" for new sessions; this
  warning means the mode was changed after start.)
────────────────────────────────────────────────────────────────────

EOF
    ;;
esac

exit 0
