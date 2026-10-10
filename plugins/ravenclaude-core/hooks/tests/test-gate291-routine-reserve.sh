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
#   G guard: asks before autonomous work only in an attended interactive session on a live
#     reading; one ask for parallel calls; consent only after the asked call ran; a new week
#     asks again; headless / SDK / subagent / estimated -> warn, never ask. Teeth: an
#     always-interactive mutant must ask headless.
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
# The same raw files re-indented, as a format-on-write hook leaves a saved .json:
# `{` and the first key end up on different lines, and every record must still parse.
RAW2="$TMP/raw-pretty"
mkdir -p "$RAW2/sessions"
cp "$RAW/env.json" "$RAW2/env.json"
python3 -c 'import json,sys; json.dump(json.load(open(sys.argv[1])), open(sys.argv[2], "w"), indent=2)' \
  "$RAW/triggers.json" "$RAW2/triggers.json"
{
  echo '<other-session nonce="x" untrusted="true">'
  sed -n 2p "$RAW/sessions/session_abc.json" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin), indent=4))'
  echo '</other-session nonce="x">'
} >"$RAW2/sessions/session_abc.json"
sample2="$(python3 "$ENGINE" meter-append --raw "$RAW2" --out "$TMP/samples-pretty" 2>&1)"
if [ -f "$sample2" ] && grep -q '"kind": "trigger"' "$sample2" && grep -q '"kind": "run"' "$sample2" \
  && grep -q '"cost_usd": 0.5' "$sample2"; then
  pass "pretty-printed raw files parse to the same trigger, run and cost records"
else
  fail "pretty-printed raw files lost records: $(cat "$sample2" 2>/dev/null | head -c 400)"
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
# A failed atomic write after validation must not report success (dashboard 200 /
# CLI exit 0 with no override.json). Trigger: mkstemp OSError (ENOSPC/EACCES).
engine = mod._reserve_engine(proj)
real_mkstemp = engine.tempfile.mkstemp
def boom(*_a, **_k):
    raise OSError(28, "No space left on device")
engine.tempfile.mkstemp = boom
try:
    code, body = mod._write_reserve_override(proj, {"action": "set", "pct": 40})
    assert code == 409 and body.get("ok") is False, (code, body)
    assert not (state / "override.json").exists(), "failed write still created override.json"
finally:
    engine.tempfile.mkstemp = real_mkstemp
code, body = mod._write_reserve_override(proj, {"action": "set", "pct": 40})
assert code == 200 and body["ok"] and (state / "override.json").exists(), (code, body)
code, body = mod._write_reserve_override(proj, {"action": "clear"})
assert code == 200 and not (state / "override.json").exists(), (code, body)
print("ok")
PY
)"; then
  pass "read-only GET, 400 on bool/out-of-range/string pct and unknown action, set + clear round-trip, write-failure is 409"
else
  fail "server helper check failed:"
  printf '%s\n' "$out" | tail -5 | sed 's/^/      /'
fi

echo "── G: guard mode — asks only where a person can answer; one ask; consent only after the asked call ran"
guard_payload() { # $1=session $2=tool $3=tool_use_id [$4=tool_input json] [$5=extra top-level fields]
  # Not "${4:-{\}}": bash 3.2 (stock macOS) keeps the backslash and yields `{\}`, which is
  # invalid JSON, so every guarded call reads as junk stdin and the asks silently vanish.
  local input="${4:-}"
  [ -n "$input" ] || input='{}'
  printf '{"session_id":"%s","hook_event_name":"PreToolUse","tool_name":"%s","tool_use_id":"%s","tool_input":%s%s}' \
    "$1" "$2" "$3" "$input" "${5:-}"
}
run_guard() { # stdin payload; env ATTENDED / ENTRY override the session's attendance + entrypoint
  CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_CODE_SESSION_ATTENDED="${ATTENDED:-1}" CLAUDE_CODE_ENTRYPOINT="${ENTRY:-cli}" \
    bash "$HOOK" --event guard
}
run_consent() { CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" --event consent; }
decision() { # hook stdout -> none | ask | deny | allow | warn
  python3 -c 'import json, sys
t = sys.stdin.read().strip()
if not t:
    print("none"); sys.exit()
h = json.loads(t).get("hookSpecificOutput", {})
print(h.get("permissionDecision") or ("warn" if h.get("additionalContext") else "other"))'
}
write_guard_reserve() { # $1=state $2=current_source [$3=reset_at]
  printf '{"mode":"guard","state":"%s","current_source":"%s","reading_stale":false,"current_pct":82,"line_pct":75,"reserve_pct_effective":25,"routines":[{"remaining_firings":3}],"reset_at":"%s"}\n' \
    "$1" "$2" "${3:-2026-10-05T00:00:00Z}" >"$RAVENCLAUDE_USAGE_DIR/reserve.json"
}
write_guard_reserve over statusline
d="$(guard_payload g1 Workflow t1 | run_guard | decision)"
[ "$d" = "none" ] && pass "guard lane silent under advise (it needs routine_reserve: guard)" || fail "guard lane spoke under advise: $d"
printf 'schema_version: 5\nroutine_reserve: guard\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"
d="$(guard_payload g1 Bash t0 | run_guard | decision)"
[ "$d" = "none" ] && pass "an ordinary tool is not guarded" || fail "guarded Bash: $d"
d="$(guard_payload g1 Agent t0 '{"run_in_background":false}' | run_guard | decision)"
[ "$d" = "none" ] && pass "a foreground Agent (run_in_background=false) is not guarded" || fail "guarded a foreground Agent: $d"
d="$(guard_payload g1 Workflow t1 | run_guard | decision)"
[ "$d" = "ask" ] && pass "asks before a Workflow past the line (attended, interactive, live reading)" || fail "no ask: $d"
d="$(guard_payload g1 Agent t2 | run_guard | decision)"
[ "$d" = "deny" ] && pass "a parallel call while the ask is pending is denied, not asked again" || fail "second call got: $d"
guard_payload g1 Agent t9 | run_consent
d="$(guard_payload g1 CronCreate t3 | run_guard | decision)"
[ "$d" = "deny" ] && pass "a different call running does not count as consent to the one asked about" || fail "foreign tool_use_id granted consent: $d"
# Empty/missing tool_use_id must NOT match a concrete pending id (pre-fix: `asked and
# ran and asked != ran` treated empty ran as success and granted session-wide consent).
printf '{"session_id":"g1","hook_event_name":"PostToolUse","tool_name":"CronCreate","tool_input":{}}' | run_consent
d="$(guard_payload g1 CronCreate t3b | run_guard | decision)"
[ "$d" = "deny" ] && pass "a PostToolUse with no tool_use_id does not satisfy a concrete pending ask" \
  || fail "empty tool_use_id granted consent: $d"
out="$(guard_payload g1 Workflow t1 | run_consent)"
[ -z "$out" ] && pass "the consent lane prints nothing" || fail "consent lane printed: $out"
d="$(guard_payload g1 ScheduleWakeup t4 | run_guard | decision)"
[ "$d" = "none" ] && pass "after the asked call ran, the session is allowed for the rest of the week" || fail "consent not honoured: $d"
write_guard_reserve over statusline 2026-10-12T00:00:00Z
d="$(guard_payload g1 Workflow t5 | run_guard | decision)"
[ "$d" = "ask" ] && pass "a new week asks again" || fail "consent carried into a new week: $d"
d="$(guard_payload g2 Workflow t1 | ATTENDED=0 run_guard | decision)"
[ "$d" = "warn" ] && pass "headless (attended=0) warns, never asks" || fail "headless got: $d"
d="$(guard_payload g2 Workflow t2 | ATTENDED=0 run_guard | decision)"
[ "$d" = "none" ] && pass "the headless warning is once per band" || fail "headless warning repeated: $d"
d="$(guard_payload g3 Workflow t1 | ENTRY=sdk-cli run_guard | decision)"
[ "$d" = "warn" ] && pass "an SDK entrypoint warns, never asks" || fail "sdk entrypoint got: $d"
d="$(guard_payload g4 Agent t1 '{}' ',"agent_id":"sub-1"' | run_guard | decision)"
[ "$d" = "warn" ] && pass "a subagent's own call warns, never asks" || fail "subagent got: $d"
d="$(guard_payload g5 mcp__Claude_Code_Remote__fire_trigger t1 | run_guard | decision)"
[ "$d" = "ask" ] && pass "a Remote fire_trigger call is guarded" || fail "Remote call not guarded: $d"
d="$(guard_payload g5b mcp__notes__create_session t1 | run_guard | decision)"
[ "$d" = "none" ] && pass "another server's create_session is not guarded" || fail "guarded a non-Remote server: $d"
write_guard_reserve over estimate
d="$(guard_payload g6 Workflow t1 | run_guard | decision)"
[ "$d" = "warn" ] && pass "an estimated reading (no live statusline) warns, never asks" || fail "estimated reading got: $d"
write_guard_reserve ok statusline
d="$(guard_payload g7 Workflow t1 | run_guard | decision)"
[ "$d" = "none" ] && pass "silent when ok" || fail "spoke while ok: $d"
out="$(printf 'not json' | run_guard)"
rc=$?
[ -z "$out" ] && [ "$rc" -eq 0 ] && pass "junk stdin: silent, exit 0" || fail "junk stdin (rc=$rc): $out"
# Teeth: the headless assertions above must depend on the interactivity check. An engine
# whose check always passes has to ASK in exactly the case the real engine only warns.
write_guard_reserve over statusline
sed 's/and live and _interactive(payload, env):/and live and True:/' "$ENGINE" >"$TMP/rr-mutant.py"
if cmp -s "$ENGINE" "$TMP/rr-mutant.py"; then
  fail "teeth: the mutant is identical to the engine (the sed no longer matches)"
else
  d="$(guard_payload g8 Workflow t1 | CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_CODE_SESSION_ATTENDED=0 \
    python3 "$TMP/rr-mutant.py" hook-guard | decision)"
  [ "$d" = "ask" ] && pass "teeth: an always-interactive mutant asks headless (so the warn-only result is load-bearing)" \
    || fail "teeth: the mutant did not ask headless ($d) — the headless check proves nothing"
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 291 PASS — routine token reserve: fixtures match, DOW mutant rejected, samples allow-listed, advise hook opt-in + once-per-band, statusline pass-through, guard asks only where a person can answer."
  exit 0
else
  echo "Gate 291 FAIL — $fails subtest(s) failed."
  exit 1
fi
