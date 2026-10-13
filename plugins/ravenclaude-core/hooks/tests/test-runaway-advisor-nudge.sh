#!/usr/bin/env bash
# test-runaway-advisor-nudge.sh — Gate 53c fixture (v0.352.0).
#
# runaway-brake.sh adds an advisory (exit 0, PreToolUse additionalContext) when
# the SAME mutating tool call repeats for the 2nd time in a row: "re-read the
# error, then consult the advisor before retrying". The brake itself (exit 2 at
# max_consecutive) is unchanged.
#
#   N1  call #1 of a mutating command → exit 0, no stdout
#   N2  call #2 identical → exit 0, stdout is ONE JSON object whose
#       hookSpecificOutput.additionalContext mentions the advisor, no permissionDecision
#   N3  call #3 identical → exit 0, no stdout (nudge fires once per streak)
#   N4  2 identical READ-ONLY calls → no nudge (carve-out stays transparent)
#   N5  the brake still trips (exit 2) at max_consecutive
#   N6  no posture file → no stdout at all (zero-cost opt-in unchanged)
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-runaway-advisor-nudge.sh
# Run via gate:   bash scripts/audit-gates.sh --check 53

set -uo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT" || exit 1
HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/runaway-brake.sh"
PASS=0; FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

ROOT="$(mktemp -d)"; NOPOST="$(mktemp -d)"
trap 'rm -r -- "$ROOT" "$NOPOST"' EXIT
mkdir -p "$ROOT/.ravenclaude"
printf 'categories:\n  shell_readonly: allow\nrunaway:\n  max_consecutive: 4\n' > "$ROOT/.ravenclaude/comfort-posture.yaml"

payload() { # cwd sid command
  jq -cn --arg c "$1" --arg s "$2" --arg k "$3" '{cwd:$c,session_id:$s,tool_name:"Bash",tool_input:{command:$k}}'
}
call() { # cwd sid command -> sets OUT, RC
  OUT="$(payload "$1" "$2" "$3" | bash "$HOOK" 2>/dev/null)"; RC=$?
}

S="sess-nudge-$RANDOM$RANDOM"
call "$ROOT" "$S" "npm test"
[ "$RC" = 0 ] && [ -z "$OUT" ] && pass "N1 first call: exit 0, silent" || fail "N1 first call rc=$RC out='$OUT'"

call "$ROOT" "$S" "npm test"
ctx="$(printf '%s' "$OUT" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
pd="$(printf '%s' "$OUT" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null)"
ev="$(printf '%s' "$OUT" | jq -r '.hookSpecificOutput.hookEventName // empty' 2>/dev/null)"
if [ "$RC" = 0 ] && printf '%s' "$ctx" | grep -qi 'advisor' && [ -z "$pd" ] && [ "$ev" = "PreToolUse" ]; then
  pass "N2 second identical call: exit 0 + additionalContext names the advisor, no permissionDecision"
else
  fail "N2 second identical call rc=$RC out='$OUT'"
fi

call "$ROOT" "$S" "npm test"
[ "$RC" = 0 ] && [ -z "$OUT" ] && pass "N3 third call: silent (one nudge per streak)" || fail "N3 third call rc=$RC out='$OUT'"

call "$ROOT" "$S" "npm test"
[ "$RC" = 2 ] && pass "N5 brake still trips at max_consecutive=4 (exit 2)" || fail "N5 brake did not trip, rc=$RC"

S2="sess-nudge-ro-$RANDOM$RANDOM"
call "$ROOT" "$S2" "git status"; call "$ROOT" "$S2" "git status"
[ -z "$OUT" ] && pass "N4 repeated read-only call: no nudge" || fail "N4 read-only repeat produced '$OUT'"

S3="sess-nudge-np-$RANDOM$RANDOM"
call "$NOPOST" "$S3" "npm test"; call "$NOPOST" "$S3" "npm test"
[ "$RC" = 0 ] && [ -z "$OUT" ] && pass "N6 no posture: silent no-op" || fail "N6 no posture rc=$RC out='$OUT'"

echo "  passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
