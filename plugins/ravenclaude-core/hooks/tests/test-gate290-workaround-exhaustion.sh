#!/usr/bin/env bash
# Gate 290 — workaround-exhaustion.sh (the blocked-exhaustion gate). Bidirectional:
#   A silent-when-inert: no posture / mode off / no deny this session / a question
#     that is not a hand-back / a Stop payload without last_assistant_message.
#   B fires-on-bad: after a guard deny, a hand-back question with fewer than
#     `floor` executed distinct channels warns (additionalContext) or, in block
#     mode, denies the AskUserQuestion; a hand-back turn end blocks the Stop,
#     bounded by max_blocks (force-allow on the last attempt).
#   C the ledger arithmetic: tried=no does not count, a duplicate channel counts
#     once, rows before the deny do not count, the CLI refuses a yes-row with no
#     result / a channel outside the enum / a blocked-ok with no reason, and a
#     blocked-ok since the deny releases the gate AND leaves a warn event.
#   D teeth (must-fail half): a mutant whose floor comparison is neutered stops
#     firing on the 0-row case; the fixture must catch it.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$(cd "$HERE/.." && pwd)/workaround-exhaustion.sh"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}
command -v jq >/dev/null 2>&1 || { echo "  ✗ jq is required for this gate"; exit 1; }

TMP="$(mktemp -d)"
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
POST="$PROJ/.ravenclaude/comfort-posture.yaml"

posture() { # $1=mode
  printf 'schema_version: 5\nworkaround_exhaustion: %s\nworkaround_exhaustion_floor: 3\nworkaround_exhaustion_max_blocks: 3\n' "$1" >"$POST"
}
deny_event() { # $1=session $2=ts — a guard deny line in the substrate's real shape
  mkdir -p "$PROJ/.ravenclaude/runs/$1"
  printf '{"schema_version":1,"ts":"%s","hook":"thing-orchestrator.sh","verdict":"deny","tool":"Edit","path":"","rule":"self-disable","session_id":"%s","exit_code":2}\n' "$2" "$1" >>"$PROJ/.ravenclaude/runs/$1/hook-events.jsonl"
}
ask_payload() { # $1=session $2=question
  jq -cn --arg s "$1" --arg c "$PROJ" --arg q "$2" '{session_id:$s,cwd:$c,hook_event_name:"PreToolUse",tool_name:"AskUserQuestion",tool_input:{questions:[{question:$q,header:"Next",multiSelect:false,options:[{label:"Option A",description:"a"},{label:"Option B",description:"b"}]}]}}'
}
stop_payload() { # $1=session $2=last message ("" -> field absent)
  if [ -n "$2" ]; then
    jq -cn --arg s "$1" --arg c "$PROJ" --arg m "$2" '{session_id:$s,cwd:$c,hook_event_name:"Stop",stop_hook_active:false,last_assistant_message:$m}'
  else
    jq -cn --arg s "$1" --arg c "$PROJ" '{session_id:$s,cwd:$c,hook_event_name:"Stop",stop_hook_active:false}'
  fi
}
# run_hook <hook> <lane> <payload> -> stdout in $OUT, stderr in $ERR, exit in $RC
run_hook() {
  OUT="$(printf '%s' "$3" | CLAUDE_PROJECT_DIR="$PROJ" bash "$1" "$2" 2>"$TMP/err")"; RC=$?
  ERR="$(cat "$TMP/err" 2>/dev/null || true)"
}
cli() { CLAUDE_PROJECT_DIR="$PROJ" bash "$HOOK" "$@"; }
events_of() { cat "$PROJ/.ravenclaude/runs/$1/hook-events.jsonl" 2>/dev/null || true; }

BLOCKED_Q="The substrate guard denied the edit. Which option do you want — apply the diff manually, or should I hand this back?"
PLAIN_Q="Which accent colour do you prefer for the dashboard theme?"
BLOCKED_MSG="I can't push from this session; you'll need to apply the diff by hand."
PLAIN_MSG="Done — CI is green on the new head and the PR is ready for review."

# ── A: silent when inert ──────────────────────────────────────────────────────
S1="s1"; deny_event "$S1" "2020-01-01T00:00:00Z"
rm -f "$POST"
run_hook "$HOOK" ask "$(ask_payload "$S1" "$BLOCKED_Q")"
[ -z "$OUT" ] && [ "$RC" -eq 0 ] && pass "A1: no comfort-posture -> silent" || fail "A1: fired without a posture (out=${OUT:0:60})"

posture off
run_hook "$HOOK" ask "$(ask_payload "$S1" "$BLOCKED_Q")"
[ -z "$OUT" ] && pass "A2: mode off -> silent" || fail "A2: fired with mode off"

posture warn
run_hook "$HOOK" ask "$(ask_payload "no-deny-session" "$BLOCKED_Q")"
[ -z "$OUT" ] && pass "A3: no deny this session -> silent" || fail "A3: fired with no deny on record"

run_hook "$HOOK" ask "$(ask_payload "$S1" "$PLAIN_Q")"
[ -z "$OUT" ] && pass "A4: question that is not a hand-back -> silent" || fail "A4: fired on a plain question"

run_hook "$HOOK" stop "$(stop_payload "$S1" "")"
[ -z "$OUT" ] && pass "A5: Stop payload without last_assistant_message -> silent (host limit, by construction)" || fail "A5: Stop lane fired without the field"

# ── B: fires on a hand-back after a deny ──────────────────────────────────────
run_hook "$HOOK" ask "$(ask_payload "$S1" "$BLOCKED_Q")"
if printf '%s' "$OUT" | jq -e '.hookSpecificOutput.additionalContext' >/dev/null 2>&1 \
   && printf '%s' "$OUT" | grep -q '0 of 3' && printf '%s' "$OUT" | grep -q 'RavenClaude guard notice' \
   && ! printf '%s' "$OUT" | grep -q 'permissionDecision'; then
  pass "B1: warn + hand-back question + 0 rows -> additionalContext '0 of 3', no permissionDecision"
else
  fail "B1: warn lane did not deliver the nudge (out=${OUT:0:120})"
fi
printf '%s' "$OUT" | grep -q -- "--session $S1" && pass "B2: the nudge prints the exact --session id to use" || fail "B2: nudge lacks --session"
events_of "$S1" | grep -q '"hook":"workaround-exhaustion.sh","verdict":"warn"' && pass "B3: warn verdict emitted to hook-events (derived values)" || fail "B3: no warn event emitted"

# ── C: ledger arithmetic + CLI refusals ───────────────────────────────────────
cli tried --session "$S1" --channel mcp-api --result "pushed via contents API; mode bit dropped to 100644" --bypass-test "a commit on the PR branch" >/dev/null 2>&1 \
  && pass "C1: CLI records a tried=yes row with result + bypass-test" || fail "C1: CLI refused a valid row"
cli tried --session "$S1" --channel mcp-api --result "second push, same channel" --bypass-test "a commit on the PR branch" >/dev/null 2>&1
cli tried --session "$S1" --channel ci-runner --tried no --bypass-test "would be a CI run log" >/dev/null 2>&1 \
  && pass "C2: a tried=no row is accepted (an honest 'considered')" || fail "C2: tried=no row refused"
if cli tried --session "$S1" --channel local-bash --bypass-test "n/a" >/dev/null 2>&1; then
  fail "C3: a tried=yes row with NO result was accepted"
else
  pass "C3: a tried=yes row with no result is refused ('considered' is not a result)"
fi
if cli tried --session "$S1" --channel telepathy --result "x" --bypass-test "y" >/dev/null 2>&1; then
  fail "C4: a channel outside the enum was accepted"
else
  pass "C4: a channel outside the enum is refused"
fi
if cli blocked-ok --session "$S1" >/dev/null 2>&1; then
  fail "C5: blocked-ok with no reason was accepted"
else
  pass "C5: blocked-ok with no reason is refused"
fi
run_hook "$HOOK" ask "$(ask_payload "$S1" "$BLOCKED_Q")"
if printf '%s' "$OUT" | grep -q '1 of 3'; then
  pass "C6: duplicate channel counts once and tried=no does not count -> '1 of 3'"
else
  fail "C6: expected '1 of 3' after 2x mcp-api + 1x tried=no ci-runner (out=${OUT:0:120})"
fi
cli tried --session "$S1" --channel ci-runner --result "workflow_dispatch run 35211957197 succeeded; mode restored" --bypass-test "a CI run log + a bot commit on the branch" >/dev/null 2>&1
cli tried --session "$S1" --channel local-bash --result "chmod denied: xc.tribunal-self-disable" --bypass-test "n/a — the deny is the artifact" >/dev/null 2>&1
run_hook "$HOOK" ask "$(ask_payload "$S1" "$BLOCKED_Q")"
[ -z "$OUT" ] && pass "C7: 3 distinct executed channels -> the gate releases (silent)" || fail "C7: still firing with 3 distinct executed channels (out=${OUT:0:120})"

# A fresh session: rows never written, block mode.
S2="s2"; deny_event "$S2" "2020-01-01T00:00:00Z"; posture block
run_hook "$HOOK" ask "$(ask_payload "$S2" "$BLOCKED_Q")"
if printf '%s' "$OUT" | jq -e '.hookSpecificOutput.permissionDecision == "deny"' >/dev/null 2>&1 && printf '%s' "$OUT" | grep -q '0 of 3'; then
  pass "B4: block + hand-back question + 0 rows -> permissionDecision deny"
else
  fail "B4: block lane did not deny (out=${OUT:0:120})"
fi
events_of "$S2" | grep -q '"hook":"workaround-exhaustion.sh","verdict":"deny"' && pass "B5: deny verdict emitted to hook-events" || fail "B5: no deny event emitted"
# The gate's own deny must not re-anchor the window: the ledger still measures from the ORIGINAL deny.
cli tried --session "$S2" --channel mcp-api --result "ok" --bypass-test "a PR commit" >/dev/null 2>&1
run_hook "$HOOK" ask "$(ask_payload "$S2" "$BLOCKED_Q")"
printf '%s' "$OUT" | grep -q '1 of 3' && pass "B6: our own deny event does not re-anchor the window ('1 of 3' still counts the row)" || fail "B6: window re-anchored by the gate's own deny (out=${OUT:0:120})"

# blocked-ok releases and is logged.
cli blocked-ok --session "$S2" "the maintainer exemption needs a live gh GraphQL call this proxy does not serve" >/dev/null 2>&1
run_hook "$HOOK" ask "$(ask_payload "$S2" "$BLOCKED_Q")"
[ -z "$OUT" ] && pass "C8: a blocked-ok row since the deny releases the gate" || fail "C8: gate still fired after blocked-ok (out=${OUT:0:120})"
events_of "$S2" | grep -q 'workaround-blocked-ok' && pass "C9: the escape is logged as a warn event (never silent)" || fail "C9: blocked-ok left no event"

# Stop lane, block mode, max_blocks 3.
S3="s3"; deny_event "$S3" "2020-01-01T00:00:00Z"
run_hook "$HOOK" stop "$(stop_payload "$S3" "$PLAIN_MSG")"
[ -z "$OUT" ] && pass "A6: Stop with a non-hand-back message -> silent" || fail "A6: Stop fired on ordinary prose"
run_hook "$HOOK" stop "$(stop_payload "$S3" "$BLOCKED_MSG")"
if printf '%s' "$OUT" | jq -e '.decision == "block"' >/dev/null 2>&1 && printf '%s' "$OUT" | grep -q 'stop blocked 1/3'; then
  pass "B7: block + hand-back turn end + 0 rows -> decision:block (1/3)"
else
  fail "B7: Stop lane did not block (out=${OUT:0:120})"
fi
run_hook "$HOOK" stop "$(stop_payload "$S3" "$BLOCKED_MSG")"
printf '%s' "$OUT" | grep -q 'stop blocked 2/3' && pass "B8: second hand-back stop -> blocked 2/3" || fail "B8: block counter did not advance (out=${OUT:0:120})"
run_hook "$HOOK" stop "$(stop_payload "$S3" "$BLOCKED_MSG")"
if [ -z "$OUT" ] && printf '%s' "$ERR" | grep -q 'releasing the Stop gate' && [ ! -f "$PROJ/.ravenclaude/runs/$S3/workaround-exhaustion.blocks" ]; then
  pass "B9: max_blocks reached -> force-allow with a loud notice, counter cleared (no deadlock)"
else
  fail "B9: force-allow did not happen at max_blocks (out=${OUT:0:80} err=${ERR:0:80})"
fi
events_of "$S3" | grep -q 'workaround-force-allow' && pass "B10: force-allow is logged as a warn event" || fail "B10: force-allow left no event"

# Warn mode on the Stop lane delivers additionalContext without a decision.
posture warn
S4="s4"; deny_event "$S4" "2020-01-01T00:00:00Z"
run_hook "$HOOK" stop "$(stop_payload "$S4" "$BLOCKED_MSG")"
if printf '%s' "$OUT" | jq -e '.hookSpecificOutput.hookEventName == "Stop" and (.hookSpecificOutput.additionalContext|length) > 0 and (.decision == null)' >/dev/null 2>&1; then
  pass "B11: warn + hand-back turn end -> Stop additionalContext, no decision"
else
  fail "B11: warn Stop lane wrong shape (out=${OUT:0:120})"
fi

# ── D: teeth — a neutered floor comparison must be caught ────────────────────
MUT="$TMP/mut-workaround-exhaustion.sh"
sed -e 's/if \[ "\$n" -ge "\$floor" \]; then/if [ "$n" -ge 0 ]; then/' "$HOOK" >"$MUT"
if ! grep -q '"\$n" -ge 0' "$MUT"; then
  fail "D1: could not neuter the floor comparison (sed no-op — fixture stale)"
else
  S5="s5"; deny_event "$S5" "2020-01-01T00:00:00Z"
  run_hook "$MUT" ask "$(ask_payload "$S5" "$BLOCKED_Q")"
  if [ -z "$OUT" ]; then
    pass "D1: must-fail half — with the floor neutered the 0-row hand-back is waved through (the comparison is load-bearing)"
  else
    fail "D1: must-fail — neutered hook STILL fired on the 0-row case (no teeth)"
  fi
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 290 PASS — workaround-exhaustion: inert without posture/deny/hand-back, fires on a hand-back after a deny, ledger arithmetic + CLI refusals + blocked-ok escape hold, Stop lane bounded by max_blocks, teeth."
  exit 0
else
  echo "Gate 290 FAIL — $fails subtest(s) failed."
  exit 1
fi
