#!/usr/bin/env bash
# test-spectate-emit.sh — Spectate v0.2 emit hook + corr_id substrate
#
# Proves:
#   S1  SessionStart → session.start line, exit 0, empty stdout
#   S2  PreToolUse → tool.pre with corr_id from tool_use_id; no command text
#   S3  PostToolUse → tool.post asserted_status=succeeded
#   S4  UserPromptSubmit → prompt.submit with prompt_chars only (no prompt text)
#   S5  Secret-shaped prompt never reaches spectate-events.jsonl
#   S6  _emit_hook_event 7th arg writes corr_id on hook-events.jsonl
#   S7  Must-fail teeth: mutant that copies prompt into the JSONL is caught
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-spectate-emit.sh

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$HOOKS_DIR/spectate-emit.sh"
FAILED=0
pass() { printf '  ✓ %s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1"; FAILED=$((FAILED + 1)); }

SECRET='sk-ant-api03-TESTSECRETVALUE00000000000000000000'

run_hook() {
  # $1=project $2=session $3=event $4=payload-json
  local proj="$1" sid="$2" ev="$3" body="$4"
  printf '%s' "$body" \
    | CLAUDE_PROJECT_DIR="$proj" CLAUDE_SESSION_ID="$sid" CLAUDE_HOOK_EVENT="$ev" \
      CLAUDECODE=1 \
      bash "$HOOK" 2>/dev/null
}

echo "── S1: SessionStart emits session.start ──────────────────────────────────"
T1="$(mktemp -d)"
out="$(run_hook "$T1" s1 SessionStart '{"session_id":"s1","source":"startup"}')"
rc=$?
log="$T1/.ravenclaude/runs/s1/spectate-events.jsonl"
if [ "$rc" -eq 0 ] && [ -z "$out" ] && [ -f "$log" ]; then
  kind="$(jq -r '.kind' "$log")"
  src="$(jq -r '.source' "$log")"
  sch="$(jq -r '.schema' "$log")"
  if [ "$kind" = "session.start" ] && [ "$src" = "hook" ] && [ "$sch" = "rc.spectate.v1" ]; then
    pass "S1: session.start written; exit 0; empty stdout"
  else
    fail "S1: unexpected fields kind=$kind source=$src schema=$sch"
  fi
else
  fail "S1: rc=$rc out_len=${#out} log_exists=$( [ -f "$log" ] && echo y || echo n )"
fi
rm -rf "$T1"

echo "── S2: PreToolUse emits tool.pre + corr_id; no command text ──────────────"
T2="$(mktemp -d)"
payload2="$(jq -cn --arg secret "$SECRET" \
  '{session_id:"s2",tool_name:"Bash",tool_use_id:"tu-abc1",tool_input:{command:("echo " + $secret)}}')"
out="$(run_hook "$T2" s2 PreToolUse "$payload2")"
log="$T2/.ravenclaude/runs/s2/spectate-events.jsonl"
if [ -f "$log" ]; then
  kind="$(jq -r '.kind' "$log")"
  corr="$(jq -r '.corr_id // empty' "$log")"
  target="$(jq -r '.tool.target // empty' "$log")"
  blob="$(cat "$log")"
  ok=1
  [ "$kind" = "tool.pre" ] || ok=0
  [ "$corr" = "tu-abc1" ] || ok=0
  [ "$target" = "echo" ] || ok=0
  printf '%s' "$blob" | grep -Fq "$SECRET" && ok=0
  [ -z "$out" ] || ok=0
  if [ "$ok" -eq 1 ]; then
    pass "S2: tool.pre corr_id=tu-abc1 target=echo; secret absent"
  else
    fail "S2: kind=$kind corr=$corr target=$target secret_leaked=$(printf '%s' "$blob" | grep -c "$SECRET" || true)"
  fi
else
  fail "S2: no spectate-events.jsonl"
fi
rm -rf "$T2"

echo "── S3: PostToolUse emits tool.post succeeded ─────────────────────────────"
T3="$(mktemp -d)"
payload3='{"session_id":"s3","tool_name":"Read","tool_use_id":"tu-read","tool_input":{"file_path":"plugins/ravenclaude-core/CLAUDE.md"},"tool_response":{"ok":true}}'
out="$(run_hook "$T3" s3 PostToolUse "$payload3")"
log="$T3/.ravenclaude/runs/s3/spectate-events.jsonl"
if [ -f "$log" ]; then
  kind="$(jq -r '.kind' "$log")"
  st="$(jq -r '.asserted_status // empty' "$log")"
  tgt="$(jq -r '.tool.target // empty' "$log")"
  if [ "$kind" = "tool.post" ] && [ "$st" = "succeeded" ] && [ "$tgt" = "CLAUDE.md" ] && [ -z "$out" ]; then
    pass "S3: tool.post succeeded target=CLAUDE.md"
  else
    fail "S3: kind=$kind status=$st target=$tgt"
  fi
else
  fail "S3: no log"
fi
rm -rf "$T3"

echo "── S4/S5: UserPromptSubmit metrics only; secret never logged ─────────────"
T4="$(mktemp -d)"
payload4="$(jq -cn --arg secret "$SECRET" \
  '{session_id:"s4",prompt:("please use " + $secret + " to continue")}')"
out="$(run_hook "$T4" s4 UserPromptSubmit "$payload4")"
log="$T4/.ravenclaude/runs/s4/spectate-events.jsonl"
if [ -f "$log" ]; then
  kind="$(jq -r '.kind' "$log")"
  chars="$(jq -r '.metrics.prompt_chars // 0' "$log")"
  blob="$(cat "$log")"
  if [ "$kind" = "prompt.submit" ] && [ "$chars" -gt 10 ] && ! printf '%s' "$blob" | grep -Fq "$SECRET" && [ -z "$out" ]; then
    pass "S4/S5: prompt.submit prompt_chars=$chars; secret absent"
  else
    fail "S4/S5: kind=$kind chars=$chars leaked=$(printf '%s' "$blob" | grep -c "$SECRET" || true)"
  fi
else
  fail "S4/S5: no log"
fi
rm -rf "$T4"

echo "── S6: _emit_hook_event 7th arg writes corr_id ────────────────────────────"
T6="$(mktemp -d)"
# shellcheck source=/dev/null
. "$HOOKS_DIR/_emit-event.sh"
payload='{"session_id":"s6"}'
CLAUDE_PROJECT_DIR="$T6" CLAUDE_SESSION_ID="s6" \
  _emit_hook_event "spectate-emit.sh" "deny" "Bash" "rm -rf x" "test-rule" 2 "corr-join1"
hlog="$T6/.ravenclaude/runs/s6/hook-events.jsonl"
if [ -f "$hlog" ] && [ "$(jq -r '.corr_id // empty' "$hlog")" = "corr-join1" ]; then
  pass "S6: hook-events.jsonl carries corr_id=corr-join1"
else
  fail "S6: corr_id missing — $(cat "$hlog" 2>/dev/null || echo no-log)"
fi
rm -rf "$T6"

echo "── S8: Grok-build env detection override ─────────────────────────────────"
# v0.2: GROK_BUILD / GROK_SESSION_ID / GROK_HOME / GROK_HOOK_EVENT → harness=grok-build
# (even when CLAUDECODE is unset). Proves the capability-matrix probe substrate.
for env_kv in "GROK_BUILD=1" "GROK_SESSION_ID=gs1" "GROK_HOME=/tmp/gh" "GROK_HOOK_EVENT=SessionStart"; do
  T8="$(mktemp -d)"
  key="${env_kv%%=*}"
  val="${env_kv#*=}"
  out="$(
    printf '%s' '{"session_id":"s8","source":"startup"}' \
      | env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT \
        CLAUDE_PROJECT_DIR="$T8" CLAUDE_SESSION_ID="s8" CLAUDE_HOOK_EVENT=SessionStart \
        "$key=$val" \
        bash "$HOOK" 2>/dev/null
  )"
  log="$T8/.ravenclaude/runs/s8/spectate-events.jsonl"
  if [ -f "$log" ] && [ "$(jq -r '.harness // empty' "$log")" = "grok-build" ] && [ -z "$out" ]; then
    pass "S8: $key → harness=grok-build"
  else
    fail "S8: $key → harness=$(jq -r '.harness // empty' "$log" 2>/dev/null) out_len=${#out}"
  fi
  rm -rf "$T8"
done

echo "── S7: must-fail teeth — prompt leak mutant is caught ────────────────────"
T7="$(mktemp -d)"
MUT="$T7/mutant"
mkdir -p "$MUT"
# Mutant: after real emit, append a poison line containing the prompt.
cat > "$MUT/spectate-emit.sh" <<'MUT'
#!/usr/bin/env bash
set -uo pipefail
REAL_HOOK="$1"; shift || true
payload="$(cat 2>/dev/null || true)"
printf '%s' "$payload" | bash "$REAL_HOOK" "$@" || true
proj="${CLAUDE_PROJECT_DIR:-}"
sid="${CLAUDE_SESSION_ID:-unknown}"
log="$proj/.ravenclaude/runs/$sid/spectate-events.jsonl"
prompt="$(printf '%s' "$payload" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null || true)"
if [ -n "$prompt" ] && [ -f "$log" ]; then
  printf '{"leaked_prompt":%s}\n' "$(printf '%s' "$prompt" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')" >> "$log"
fi
exit 0
MUT
chmod +x "$MUT/spectate-emit.sh"
payload7="$(jq -cn --arg secret "$SECRET" '{session_id:"s7",prompt:("leak-" + $secret)}')"
printf '%s' "$payload7" \
  | CLAUDE_PROJECT_DIR="$T7" CLAUDE_SESSION_ID="s7" CLAUDE_HOOK_EVENT=UserPromptSubmit CLAUDECODE=1 \
    bash "$MUT/spectate-emit.sh" "$HOOK" >/dev/null 2>&1 || true
log7="$T7/.ravenclaude/runs/s7/spectate-events.jsonl"
if [ -f "$log7" ] && grep -Fq "$SECRET" "$log7"; then
  # Detector that CI/gate uses: secret must NOT appear. This teeth half proves
  # the detector would catch a regression that writes the prompt.
  if grep -Fq "$SECRET" "$log7"; then
    pass "S7: teeth — detector sees prompt leak in mutant log (gate would fail)"
  fi
else
  fail "S7: mutant did not leak as expected — teeth cannot prove the detector"
fi
rm -rf "$T7"

echo "── S9: THING_HOST=gemini → harness=gemini-cli (adapter short name) ─"
T9="$(mktemp -d)"
payload9='{"session_id":"s9"}'
printf '%s' "$payload9" \
  | env -u CURSOR_AGENT -u CURSOR_TRACE_ID -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT \
      CLAUDE_PROJECT_DIR="$T9" CLAUDE_SESSION_ID="s9" CLAUDE_HOOK_EVENT=SessionStart \
      THING_HOST=gemini \
      bash "$HOOK" >/dev/null 2>&1 || true
log9="$T9/.ravenclaude/runs/s9/spectate-events.jsonl"
harness9="$(python3 -c 'import json; print(json.load(open("'"$log9"'")).get("harness",""))' 2>/dev/null || true)"
if [ "$harness9" = "gemini-cli" ]; then
  pass "S9: THING_HOST=gemini → harness=gemini-cli"
else
  fail "S9: expected gemini-cli, got '$harness9'"
fi
rm -rf "$T9"

if [ "$FAILED" -ne 0 ]; then
  echo "test-spectate-emit: $FAILED failure(s)"
  exit 1
fi
echo "test-spectate-emit: all passed"
exit 0
