#!/usr/bin/env bash
# Gate 185 — the probe recorder must classify a NON-result apart from a
# NEGATIVE result, and must recognise a bidirectional control as POSITIVE.
#
# ── WHY (issue #860) ────────────────────────────────────────────────────────
# `log-probe.sh` checked its NEG list FIRST, over the whole combined output of
# one tool call. Two consequences, both measured in a real session:
#
#   1. A BIDIRECTIONAL CONTROL recorded as `negative`. One command probing a
#      known-good and a known-absent subject emits a 2xx AND a 4xx; NEG matched
#      the 4xx first. But that command is precisely the disconfirming probe the
#      gate demands — it PROVES the probe can return something else. So running
#      the prescribed remedy ADDED an unresolved negative instead of clearing
#      one, and the more thorough the control, the more stuck the author got.
#      The gate printed a remedy that its own recorder punished.
#
#   2. RATE-LIMITING recorded as `negative` — an absence claim the probe never
#      earned. A 429 means "I could not ask", not "it is not there", and it is
#      unclearable: every retry returns 429, so the only exit is the override.
#      A gate whose sole remedy is its own override teaches the override.
#
# ⛔ The failure mode this pins is NOT "too strict". It is a MIS-CLASSIFICATION
# that inverts the gate: a non-result stated as an absence, and a control
# stated as a failure. Both manufacture the false premise the gate exists to
# stop — this mechanism was, in these two shapes, generating them.
#
# No cleanup of the temp dir: `rm -rf` in a fixture file is itself denied by
# the destructive guard (issue #861, same class), and the OS reaps /tmp.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../log-probe.sh"
GUARD="$HERE/../guard-premise.sh"
FAILED=0

_pass() { printf '    ok   %s\n' "$1"; }
_fail() { printf '    FAIL %s\n' "$1"; FAILED=1; }

# record <session> <stdout-text> ; echoes the verdict the recorder wrote
record() {
  local sid="$1" out="$2"
  python3 - "$out" "$sid" <<'PY' | bash "$HOOK" >/dev/null 2>&1
import json, sys
print(json.dumps({
  "tool_name": "Bash",
  "session_id": sys.argv[2],
  "tool_input": {"command": "probe https://example.test/pkg/thing/json"},
  "tool_response": {"stdout": sys.argv[1], "stderr": ""},
}))
PY
  python3 - "$PROJ/.ravenclaude/runs/premise/$sid" <<'PY'
import glob, json, os, sys
# The ledger is scoped per git WORKTREE as of v0.245.0 — <sid>/scopes/<scope>/probe-ledger.jsonl —
# so one agent laptop-full of parallel siblings cannot fill one shared file. This test drives one
# recorder invocation per session id from a single cwd, so exactly one scope dir exists; glob it
# rather than hard-coding the key, which would re-break the moment the derivation changes.
cands = sorted(glob.glob(os.path.join(sys.argv[1], "scopes", "*", "probe-ledger.jsonl")))
try:
    print(json.loads(open(cands[-1]).read().strip().splitlines()[-1])["verdict"])
except Exception:
    print("(none)")
PY
}

expect() {  # expect <label> <stdout-text> <want-verdict>
  local got; got="$(record "s$(echo "$1" | tr -cd 'a-z0-9')" "$2")"
  [ "$got" = "$3" ] && _pass "$1 -> $3" || _fail "$1: want=$3 got=$got"
}

PROJ="$(mktemp -d)"; export CLAUDE_PROJECT_DIR="$PROJ"

echo "  [1] a NON-result is not a negative result"
expect "rate-limited-429"   "429"                  indeterminate
expect "rate-limited-words" "Too Many Requests"    indeterminate
expect "server-error-503"   "503"                  indeterminate
expect "timeout"            "Operation timed out"  indeterminate
expect "unreachable"        "Connection refused"   indeterminate

echo "  [2] a real absence is still a negative"
expect "http-404"           "404"                  negative
expect "cmd-not-found"      "command not found"    negative

echo "  [3] a bidirectional control is POSITIVE, in either order"
expect "control-200-404"    "200 404"              positive
expect "control-404-200"    "404 200"              positive
expect "plain-200"          "200"                  positive

# ── [4] end-to-end: the gate must not block on a NON-result ────────────────
# A new source module while ONLY an indeterminate is on the ledger must pass.
echo "  [4] the gate does not block on a non-result"
E2E="$(mktemp -d)"; export CLAUDE_PROJECT_DIR="$E2E"
record "e2e" "429" >/dev/null
PROJ="$E2E"
verdict_out="$(python3 - "$E2E" <<'PY' | bash "$GUARD" 2>&1
import json, os, sys
proj = sys.argv[1]
print(json.dumps({
  "tool_name": "Write",
  "session_id": "e2e",
  "tool_input": {"file_path": os.path.join(proj, "src", "newmod.py"), "content": "x = 1\n"},
}))
PY
)"; rc=$?
if [ "$rc" -eq 0 ] && ! printf '%s' "$verdict_out" | grep -q 'PREMISE GATE'; then
  _pass "indeterminate alone does not deny a new module"
else
  _fail "indeterminate alone denied a new module (rc=$rc)"
fi

echo
[ "$FAILED" -eq 0 ] && echo "  probe-verdict-classes: PASS" || echo "  probe-verdict-classes: FAIL"
exit "$FAILED"
