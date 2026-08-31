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

# ── MUST-FAIL HALVES ────────────────────────────────────────────────────────
# A gate with no mutant is a gate that can pass for an unrelated reason. Each
# flag below builds a mutant hook in a temp dir, repoints HOOK/GUARD at it, and
# re-runs the WHOLE test: the assertions the mutation breaks must go red, so
# `audit-gates.sh` calling this with the flag under `must_fail` proves the new
# assertions are measuring the fix and not the weather.
MUTANT="${1:-}"
if [ -n "$MUTANT" ]; then
  _M="$(mktemp -d)"
  cp "$HERE/../log-probe.sh" "$HERE/../guard-premise.sh" "$_M/" 2>/dev/null || true
  cp "$HERE/../_emit-event.sh" "$HERE/../_scrub.sh" "$_M/" 2>/dev/null || true
  python3 - "$_M" "$MUTANT" <<'PY'
import os, sys
d, flag = sys.argv[1], sys.argv[2]
if flag == "--must-fail-http-gating":
    # Revert the is_http gate: bare 3-digit numbers become status codes again,
    # exactly as they were when `wc -l` recorded http-454.
    p = os.path.join(d, "log-probe.sh")
    s = open(p).read()
    old = 'is_http = (\n    tool == "WebFetch"'
    assert old in s, "is_http block drifted -- update the mutant"
    open(p, "w").write(s.replace(old, "is_http = (\n    True"))
elif flag == "--must-fail-emit":
    # Remove the substrate emit; the deny still happens, silently.
    p = os.path.join(d, "guard-premise.sh")
    s = open(p).read()
    old = '_gp_emit "$_gp_rule"'
    assert old in s, "the emit call drifted -- update the mutant"
    open(p, "w").write(s.replace(old, ':  # emit removed by the mutant'))
else:
    raise SystemExit("unknown mutant flag: " + flag)
PY
  HOOK="$_M/log-probe.sh"
  GUARD="$_M/guard-premise.sh"
fi

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

# ── [5] A BARE NUMBER IS NOT A STATUS CODE (measured 2026-08-18) ───────────
# Of the 204 negatives on this machine, 54 carried an `http-NNN` label and ALL
# 54 came from a Bash command with no network client in it. These four are the
# verbatim shapes off the real ledgers. They are not hypotheticals — each one
# put an UNRESOLVED negative family on a live scope, and three of seven scopes
# were carrying nothing else.
#
# record_cmd <session> <command> <stdout> <tool>  -> echoes the recorded verdict
record_cmd() {
  local sid="$1"
  python3 - "$2" "$3" "$sid" "${4:-Bash}" <<'PY' | bash "$HOOK" >/dev/null 2>&1
import json, sys
print(json.dumps({
  "tool_name": sys.argv[4],
  "session_id": sys.argv[3],
  "cwd": __import__("os").environ.get("CLAUDE_PROJECT_DIR", "."),
  "tool_input": {"command": sys.argv[1], "url": sys.argv[1]},
  "tool_response": {"stdout": sys.argv[2], "stderr": ""},
}))
PY
  python3 - "$CLAUDE_PROJECT_DIR/.ravenclaude/runs/premise/$sid" <<'PY'
import glob, json, os, sys
cands = sorted(glob.glob(os.path.join(sys.argv[1], "scopes", "*", "probe-ledger.jsonl")))
try:
    print(json.loads(open(cands[-1]).read().strip().splitlines()[-1])["verdict"])
except Exception:
    print("(none)")
PY
}
expect_cmd() {  # expect_cmd <label> <command> <stdout> <want> [tool]
  local got; got="$(record_cmd "c$(echo "$1" | tr -cd 'a-z0-9')" "$2" "$3" "${5:-Bash}")"
  [ "$got" = "$4" ] && _pass "$1 -> $4" || _fail "$1: want=$4 got=$got"
}

FP="$(mktemp -d)"; export CLAUDE_PROJECT_DIR="$FP"
echo "  [5] a bare number in ordinary stdout is NOT an HTTP status"
expect_cmd "wc-l-454"       'wc -l schemas/design-schema.schema.json' '     454 schemas/x.json'      positive
expect_cmd "ls-la-448"      'ls -la /Users/x/RavenClaude'             'total 448'                    positive
expect_cmd "git-stat-447"   'git diff origin/main --stat'             ' 3 files changed, 447 ins(+)' positive
expect_cmd "git-show-403"   'git show 5a985b95 --stat | head -60'     ' 12 files changed, 403 ins'   positive

# ── [6] POSITIVE CONTROL — a genuine HTTP probe is UNCHANGED ───────────────
# ⛔ Without this half, [5] passes just as well on a hook that classifies
# nothing at all. These prove the narrowing is a narrowing and not a deletion.
echo "  [6] a genuine HTTP probe still classifies exactly as before"
expect_cmd "wget-404"     'wget -S https://example.test/missing'      '404'                       negative
expect_cmd "ghapi-404"    'gh api /repos/x/y/nope'                    '404 Not Found'             negative
expect_cmd "wget-503"     'wget -S https://example.test/x'            '503 Service Unavailable'   indeterminate
expect_cmd "webfetch-429" 'https://example.test/rl'                   '429'                       indeterminate WebFetch
expect_cmd "requests-404" 'python3 -c "import requests; requests.get(u)"' '404'                   negative
# textual markers were never gated and must not become gated
expect_cmd "no-such-file" 'ls /no/such/place'  'ls: /no/such/place: No such file or directory'    negative
expect_cmd "cmd-notfound" 'foo --bar'          'bash: foo: command not found'                     negative

# ── [7] THE DENY IS OBSERVABLE — it must reach the event substrate ─────────
# MEASURED 2026-08-18: 463 hook events across 4 real sessions from SIX hooks,
# and ZERO from guard-premise.sh. So its real fire rate — and therefore its
# false-positive rate — could not be measured from the substrate at all, and
# Heimdall/Víðarr reported a clean perimeter while it was denying. A guard you
# cannot measure is a guard nobody can tune.
#
# The line must carry DERIVED VALUES ONLY: the target BASENAME and a fixed rule
# token, never the unresolved subject or the prose claim (attacker-influenceable
# text, and this log is read back into the dashboard and the banner).
echo "  [7] a deny reaches hook-events.jsonl, derived values only"
EM="$(mktemp -d)"; export CLAUDE_PROJECT_DIR="$EM"
record_cmd "emit" 'wget -S https://example.test/missing' '404' >/dev/null
python3 - "$EM" <<'PY' > "$EM/deny.json"
import json, os, sys
p = sys.argv[1]
print(json.dumps({"tool_name": "Write", "session_id": "emit", "cwd": p,
                  "tool_input": {"file_path": os.path.join(p, "src", "newmod.py"),
                                 "content": "x = 1\n"}}))
PY
bash "$GUARD" < "$EM/deny.json" >/dev/null 2>&1; _rc=$?
[ "$_rc" -eq 2 ] && _pass "the new module is denied (exit 2)" \
                || _fail "expected a deny (exit 2), got exit $_rc"
_EV="$(find "$EM/.ravenclaude/runs" -name hook-events.jsonl -exec cat {} \; 2>/dev/null)"
printf '%s' "$_EV" | grep -q '"hook":"guard-premise.sh"' \
  && _pass "the deny emitted a guard-premise.sh event" \
  || _fail "no guard-premise.sh event on the substrate"
printf '%s' "$_EV" | grep -q '"rule":"premise-unresolved-negative"' \
  && _pass "the event names the rule that fired" \
  || _fail "the event does not name premise-unresolved-negative"
printf '%s' "$_EV" | grep -q '"path":"newmod.py"' \
  && _pass "the event carries the BASENAME, not the full path" \
  || _fail "the event path is not the bare basename"
printf '%s' "$_EV" | grep -q 'example.test' \
  && _fail "LEAK: the unresolved subject reached the substrate" \
  || _pass "derived only: the probe subject never reaches the substrate"

# An EXEMPT write must stay silent — an observability hook that logs the
# allow path floods the substrate and buries the denies it exists to surface.
_before="$(printf '%s' "$_EV" | grep -c 'guard-premise' || true)"
python3 - "$EM" <<'PY' > "$EM/allow.json"
import json, os, sys
p = sys.argv[1]
print(json.dumps({"tool_name": "Write", "session_id": "emit", "cwd": p,
                  "tool_input": {"file_path": os.path.join(p, "docs", "x.md"),
                                 "content": "hello\n"}}))
PY
bash "$GUARD" < "$EM/allow.json" >/dev/null 2>&1
_after="$(find "$EM/.ravenclaude/runs" -name hook-events.jsonl -exec cat {} \; 2>/dev/null | grep -c 'guard-premise' || true)"
[ "$_before" = "$_after" ] && _pass "an allowed write emits nothing" \
                           || _fail "an allowed write emitted an event ($_before -> $_after)"

echo
[ "$FAILED" -eq 0 ] && echo "  probe-verdict-classes: PASS" || echo "  probe-verdict-classes: FAIL"
exit "$FAILED"
