#!/usr/bin/env bash
# Gate 291 — routine token reserve (scripts/routine-reserve.py + routine-reserve-hook.sh).
# Bidirectional:
#   A projection: the engine reproduces hand-derived expectations for every fixture in
#     tests/fixtures/routine-reserve/ (cron incl. day-of-week and the DOM/DOW OR rule,
#     persistent-session run deltas, recent-weighted EWMA, cold-start median blend,
#     manual + calibrated k, override, unknown / infeasible / warn / over states).
#   B teeth (must-fail half): a mutant engine that ignores day-of-week must FAIL the
#     same fixtures — proving they exercise the rule rather than passing vacuously.
#   C privacy: meter-append persists only allow-listed fields — a raw trigger/session
#     carrying a prompt, a title, session_context and an environment id leaks none of it.
#   D hook: silent when the posture is absent or `off`; when `advise`, warns once per
#     state band per session (user-visible systemMessage + model additionalContext),
#     stays quiet on a repeat, speaks again on escalation; never exits non-zero.
#   E statusline: ingest-statusline records the weekly reading AND passes the wrapped
#     command's output through unchanged; junk stdin never breaks the wrapped output.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$HERE/../.." && pwd)"
REPO="$(cd "$PLUGIN/../.." && pwd)"
ENGINE="$PLUGIN/scripts/routine-reserve.py"
HOOK="$PLUGIN/scripts/routine-reserve-hook.sh"
FIX="$REPO/tests/fixtures/routine-reserve"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}
command -v python3 >/dev/null 2>&1 || { echo "  ✗ python3 is required for this gate"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -r -- "$TMP" 2>/dev/null' EXIT
export RAVENCLAUDE_USAGE_DIR="$TMP/usage"
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude" "$RAVENCLAUDE_USAGE_DIR"

echo "── A: projection matches hand-derived fixtures"
if out="$(python3 "$ENGINE" self-test --fixtures "$FIX" 2>&1)"; then
  pass "all fixtures pass ($(printf '%s\n' "$out" | grep -c '^PASS') cases)"
else
  fail "self-test failed:"
  printf '%s\n' "$out" | sed 's/^/      /'
fi

echo "── B: teeth — a day-of-week-blind engine must fail"
if ROUTINE_RESERVE_MUTANT=ignore_dow python3 "$ENGINE" self-test --fixtures "$FIX" >/dev/null 2>&1; then
  fail "mutant PASSED the fixtures — they do not exercise day-of-week"
else
  pass "mutant rejected"
fi

echo "── C: meter-append persists only allow-listed fields"
RAW="$TMP/raw"
mkdir -p "$RAW/sessions"
cat >"$RAW/triggers.json" <<'EOF'
{"data":[{"id":"trig_1","name":"Nightly","cron_expression":"0 3 * * *","enabled":true,"derived_state":{"prompt":"LEAKME-PROMPT"},"mcp_connections":[{"name":"LEAKME-CONNECTOR"}],"last_run":{"session_id":"cse_abc","fired_at":"2026-09-24T03:00:05Z","finished_at":"2026-09-24T03:10:00Z","status":"ROUTINE_RUN_STATUS_SUCCEEDED"}}],"has_more":false}
EOF
cat >"$RAW/sessions/session_abc.json" <<'EOF'
<other-session nonce="x" untrusted="true">
    {"ccr":{"id":"session_abc","title":"LEAKME-TITLE","environment_id":"env_LEAKME","session_context":{"sources":[{"git_repository":{"url":"https://github.com/LEAKME/repo"}}]},"origin":"scheduled_trigger","created_at":"2026-09-24T03:00:04Z","updated_at":"2026-09-24T03:10:00Z","external_metadata":{"last_served_model":"claude-haiku-4-5","usage":{"cost_usd":0.5,"output_tokens":900}}}}
</other-session nonce="x">
EOF
echo '{"attended":"0","entrypoint":"sdk-cli","calls":3}' >"$RAW/env.json"
sample="$(python3 "$ENGINE" meter-append --raw "$RAW" --out "$TMP/samples" 2>&1)"
if [ -f "$sample" ]; then
  if grep -q LEAKME "$sample"; then
    fail "sample leaked a forbidden field: $(grep -o 'LEAKME[A-Z_-]*' "$sample" | sort -u | tr '\n' ' ')"
  else
    pass "no prompt / title / connector / session_context / environment id persisted"
  fi
  if grep -q '"cost_usd": 0.5' "$sample" && grep -q '"session_id": "abc"' "$sample"; then
    pass "cost parsed out of the untrusted-session envelope, ids normalized"
  else
    fail "cost or normalized session id missing from sample"
  fi
else
  fail "meter-append produced no file: $sample"
fi

echo "── D: advise hook — opt-in, once per band, escalates"
prompt_payload() { printf '{"session_id":"%s","hook_event_name":"UserPromptSubmit","prompt":"hi"}' "$1"; }
run_hook() { printf '%s' "$(prompt_payload "$1")" | CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --event prompt; }
write_reserve() { # $1=state
  printf '{"mode":"advise","state":"%s","current_pct":72,"line_pct":77,"reserve_pct_effective":23,"routines":[{"remaining_firings":96}],"reset_at":"2026-09-28T12:00:00Z","estimated":false}\n' "$1" >"$RAVENCLAUDE_USAGE_DIR/reserve.json"
}
write_reserve warn
out="$(run_hook s1)"
rc=$?
[ -z "$out" ] && [ "$rc" -eq 0 ] && pass "silent with no posture file" || fail "spoke without a posture (rc=$rc): $out"
printf 'schema_version: 5\nroutine_reserve: off\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"
out="$(run_hook s1)"
[ -z "$out" ] && pass "silent with routine_reserve: off" || fail "spoke while off: $out"
printf 'schema_version: 5\nroutine_reserve: advise\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"
out="$(run_hook s1)"
if printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert "warn" in d["systemMessage"]; assert d["hookSpecificOutput"]["additionalContext"]' 2>/dev/null; then
  pass "warns (systemMessage + additionalContext) in the warn band"
else
  fail "no well-formed warning in the warn band: $out"
fi
out="$(run_hook s1)"
[ -z "$out" ] && pass "quiet on a repeat in the same band" || fail "repeated the same-band warning: $out"
write_reserve over
out="$(run_hook s1)"
printf '%s' "$out" | grep -q 'over' && pass "speaks again on escalation to over" || fail "missed the escalation: $out"
out="$(run_hook s2)"
printf '%s' "$out" | grep -q 'over' && pass "a new session gets its own warning" || fail "new session not warned: $out"
write_reserve ok
out="$(run_hook s3)"
[ -z "$out" ] && pass "silent when ok" || fail "spoke while ok: $out"

echo "── E: statusline — records the reading, passes the wrapped output through"
sl='{"model":{"display_name":"X"},"rate_limits":{"seven_day":{"used_percentage":41.2,"resets_at":1790700000},"five_hour":{"used_percentage":12,"resets_at":1790290000}}}'
out="$(printf '%s' "$sl" | python3 "$ENGINE" ingest-statusline --wrap 'echo WRAPPED-OK')"
case "$out" in WRAPPED-OK*) pass "wrapped statusline output passed through" ;; *) fail "wrapped output lost: $out" ;; esac
if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["seven_day_pct"]==41.2 and d["resets_at"]==1790700000' "$RAVENCLAUDE_USAGE_DIR/rate-limits.json" 2>/dev/null; then
  pass "weekly reading recorded"
else
  fail "rate-limits.json missing or wrong"
fi
out="$(printf 'not json at all' | python3 "$ENGINE" ingest-statusline --wrap 'echo STILL-OK')"
rc=$?
[ "$rc" -eq 0 ] && case "$out" in STILL-OK*) true ;; *) false ;; esac && pass "junk stdin never breaks the wrapped statusline" || fail "junk stdin broke the statusline (rc=$rc): $out"

echo "── F: dashboard server — /__reserve reads without writing; the override POST validates"
SERVER="$PLUGIN/scripts/serve-dashboards.py"
now_epoch="$(date +%s)"
printf '{"seven_day_pct": 40, "resets_at": %s, "captured_at": %s}\n' "$((now_epoch + 3 * 86400))" "$now_epoch" >"$RAVENCLAUDE_USAGE_DIR/rate-limits.json"
rm -f -- "$RAVENCLAUDE_USAGE_DIR/reserve.json" "$RAVENCLAUDE_USAGE_DIR/override.json"
if out="$(python3 - "$SERVER" "$PROJ" 2>&1 <<'PY'
import importlib.util, os, sys
from pathlib import Path
server, proj = sys.argv[1], Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("rc_serve_dashboards", server)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
state = Path(os.environ["RAVENCLAUDE_USAGE_DIR"])
r = mod._read_reserve(proj)
assert r.get("available") is True, r
assert r.get("current_pct") == 40.0, r
assert not (state / "reserve.json").exists(), "GET /__reserve wrote reserve.json"
for bad in ({"action": "set", "pct": True}, {"action": "set", "pct": 150}, {"action": "set", "pct": "30"}, {"action": "nuke"}, []):
    code, _ = mod._write_reserve_override(proj, bad)
    assert code == 400, (bad, code)
code, body = mod._write_reserve_override(proj, {"action": "set", "pct": 30})
assert code == 200 and body["ok"], (code, body)
assert mod._read_reserve(proj).get("override_pct") == 30.0
code, body = mod._write_reserve_override(proj, {"action": "clear"})
assert code == 200 and not (state / "override.json").exists(), (code, body)
print("ok")
PY
)"; then
  pass "read-only GET, 400 on bool/out-of-range/string pct and unknown action, set + clear round-trip"
else
  fail "server helper check failed:"
  printf '%s\n' "$out" | tail -5 | sed 's/^/      /'
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 291 PASS — routine token reserve: fixtures match, DOW mutant rejected, samples allow-listed, advise hook opt-in + once-per-band, statusline pass-through."
  exit 0
else
  echo "Gate 291 FAIL — $fails subtest(s) failed."
  exit 1
fi
