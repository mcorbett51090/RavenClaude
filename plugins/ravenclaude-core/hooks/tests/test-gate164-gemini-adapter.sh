#!/usr/bin/env bash
# Gate 164 — the Gemini shim normalises tool names and passes exit 2 through
# untouched (multi-host audit MH-30).
#
# WHY TOOL-NAME NORMALISATION GETS THE MOST COVERAGE HERE
#
# Gemini's hook contract is nearly Claude's: identical stdin field names, and
# `exit 2` + stderr is already its block mechanism. The ONE real translation is the
# tool-name vocabulary — Gemini sends `run_shell_command`, `read_file`,
# `write_file`, `replace`; the guardrails dispatch on Claude's PascalCase and fall
# through to `*) exit 0` ("no decision, proceed") on anything unrecognised.
#
# That exact mismatch is MH-01: under Copilot the command-review tribunal and the
# web guard were fully wired and reviewed NOTHING, silently, because `bash` is not
# `Bash`. Shipping this lane unnormalised would reproduce that on a third host, and
# it would look wired the whole time. So the mapping is asserted name by name.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AD="$HERE/../gemini-hook-adapter.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }

[ -f "$AD" ] || { printf 'FATAL: adapter not found at %s\n' "$AD" >&2; exit 1; }

cat >"$TMP/stub.sh" <<'STUB'
#!/usr/bin/env bash
{ cat; } >"$RC_OUT/stdin.json" 2>/dev/null
{ printf 'PROJECT_DIR=%s\n' "${CLAUDE_PROJECT_DIR:-}"
  printf 'SESSION_ID=%s\n'  "${CLAUDE_SESSION_ID:-}"
  printf 'THING_HOST=%s\n'  "${THING_HOST:-}"
  printf 'HOOK_EVENT=%s\n'  "${CLAUDE_HOOK_EVENT:-}"; } >"$RC_OUT/env.txt"
exit "${RC_RC:-0}"
STUB
chmod +x "$TMP/stub.sh"

payload() {
  python3 -c '
import json, sys
print(json.dumps({"session_id": "sess-9", "cwd": "/ws/p", "hook_event_name": "BeforeTool",
                  "tool_name": sys.argv[1], "tool_input": {"command": "echo hi"}}))
' "$1"
}

# Unset ambient Claude session vars — cloud-agent / nested harnesses export them
# and would mask payload-derived CLAUDE_PROJECT_DIR / SESSION_ID / HOOK_EVENT.
_run_ad() {
  env -u CLAUDE_PROJECT_DIR -u CLAUDE_SESSION_ID -u CLAUDE_HOOK_EVENT "$@"
}

run() { RC_OUT="$TMP" RC_RC="${2:-0}" _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload "$1")" >/dev/null 2>&1; }
seen_tool() { python3 -c 'import json;print(json.load(open("'"$TMP"'/stdin.json")).get("tool_name"))' 2>/dev/null; }

printf -- '── Gate 164: Gemini shim ──\n'

# ── tool-name vocabulary: the MH-01 lesson, asserted per name ───────────────
for pair in "run_shell_command:Bash" "read_file:Read" "write_file:Write" "replace:Edit" \
            "web_fetch:WebFetch" "google_web_search:WebSearch"; do
  g="${pair%%:*}"; c="${pair##*:}"
  run "$g"
  [ "$(seen_tool)" = "$c" ] && ok "normalises $g -> $c" \
    || bad "$g became '$(seen_tool)', expected $c"
done

# MCP: Gemini uses mcp_<server>_<tool>; Claude expects mcp__<server>__<tool> prefix.
run "mcp_github_create_issue"
case "$(seen_tool)" in
  mcp__*) ok "MCP names carry Claude's mcp__ prefix" ;;
  *) bad "MCP name became '$(seen_tool)'" ;;
esac

# An UNKNOWN tool must pass through VERBATIM — never defaulted. A wrong default is
# how MH-01 reviewed an absent name as Bash while skipping a present one.
run "some_future_tool"
[ "$(seen_tool)" = "some_future_tool" ] \
  && ok "an unmapped tool name passes through verbatim (no guessed default)" \
  || bad "unmapped name became '$(seen_tool)' — a default was invented"

# ── blocking: exit 2 is ALREADY Gemini's contract, so it must pass untouched ─
RC_OUT="$TMP" RC_RC=2 _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
[ "$?" -eq 2 ] && ok "exit 2 (block) passes through untouched" || bad "exit 2 did not propagate"

RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
[ "$?" -eq 0 ] && ok "exit 0 (allow) passes through" || bad "exit 0 did not propagate"

out="$(RC_OUT="$TMP" RC_RC=2 _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" 2>/dev/null)"
[ -z "$out" ] && ok "emits NO stdout JSON — nothing to get wrong on the deny path" \
  || bad "emitted stdout on deny: ${out:0:60}"

# JSON deny at exit 0 (tribunal / SH-F1) — must become Gemini exit 2.
cat >"$TMP/json-deny.sh" <<'JDS'
#!/usr/bin/env bash
cat >/dev/null
printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"tribunal stub"}}'
exit 0
JDS
chmod +x "$TMP/json-deny.sh"
RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/json-deny.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
[ "$?" -eq 2 ] && ok "JSON permissionDecision=deny at exit 0 becomes Gemini exit 2" \
  || bad "JSON deny at exit 0 did not block (rc=$?)"

# ── env lift ────────────────────────────────────────────────────────────────
run run_shell_command
grep -q '^PROJECT_DIR=/ws/p$' "$TMP/env.txt" && ok "cwd -> CLAUDE_PROJECT_DIR" || bad "CLAUDE_PROJECT_DIR unset"
grep -q '^SESSION_ID=sess-9$' "$TMP/env.txt" && ok "session_id -> CLAUDE_SESSION_ID" || bad "CLAUDE_SESSION_ID unset"
grep -q '^THING_HOST=gemini$' "$TMP/env.txt" && ok "THING_HOST asserted as gemini" || bad "THING_HOST not gemini"

# ── fail-safe ───────────────────────────────────────────────────────────────
RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/missing.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
[ "$?" -eq 0 ] && ok "a missing hook script exits 0 (never bricks every tool call)" || bad "missing script did not exit 0"

# ── the deny REASON survives (added 2026-08-12) ─────────────────────────────
# The adapter ran the guard as `>/dev/null 2>&1` for its whole life, so a block
# reached Gemini with NO explanation — while the adapter's own comment claimed
# "stderr already carries the reason". Measured: 233 bytes direct, 0 through the
# adapter. `exit 2` alone was never enough to assert; the reason is the other
# half of Gemini's documented block contract (exit 2 + stderr).
cat >"$TMP/loud.sh" <<'LOUD'
#!/usr/bin/env bash
cat >/dev/null
printf 'DENY_REASON_SENTINEL: blocked because of a specific named rule\n' >&2
exit 2
LOUD
chmod +x "$TMP/loud.sh"

RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/loud.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/err.txt"
_rc=$?
[ "$_rc" -eq 2 ] && grep -q 'DENY_REASON_SENTINEL' "$TMP/err.txt" \
  && ok "a deny carries its reason through to stderr (exit 2 + reason, both halves)" \
  || bad "deny reason lost: exit=$_rc bytes=$(wc -c <"$TMP/err.txt" | tr -d ' ')"

# The negative control — an ALLOW must stay quiet, or the fix just becomes noise
# on every tool call.
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/err0.txt"
[ ! -s "$TMP/err0.txt" ] \
  && ok "an allow emits no stderr (the fix adds no per-call noise)" \
  || bad "allow leaked $(wc -c <"$TMP/err0.txt" | tr -d ' ') bytes of stderr"

# ── a JSON deny carries its REASON to stderr (repo-review item 1a-7) ────────
# exit 2 alone is half of Gemini's block contract; the reason channel is stderr,
# and a permissionDecisionReason left on stdout reached nobody.
RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/json-deny.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/errj.txt"
_rc=$?
[ "$_rc" -eq 2 ] && grep -q 'tribunal stub' "$TMP/errj.txt" \
  && ok "a JSON deny exits 2 WITH its permissionDecisionReason on stderr" \
  || bad "JSON deny reason lost: exit=$_rc stderr=$(head -c 120 "$TMP/errj.txt")"

# ── a tribunal EDIT is blocked, never silently dropped (item 1a-5) ──────────
# EDIT = allow + updatedInput.command (a safer rewrite). The shim has no rewrite
# translation for Gemini, so dropping the EDIT ran the ORIGINAL command.
cat >"$TMP/edit.sh" <<'EDS'
#!/usr/bin/env bash
cat >/dev/null
printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"panel EDIT","updatedInput":{"command":"echo the-revised-one"}}}'
exit 0
EDS
chmod +x "$TMP/edit.sh"
RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/edit.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/erre.txt"
_rc=$?
[ "$_rc" -eq 2 ] && grep -qi 'revised' "$TMP/erre.txt" && grep -q 'the-revised-one' "$TMP/erre.txt" \
  && ok "an EDIT verdict exits 2 with the revised command on stderr" \
  || bad "EDIT verdict not blocked: exit=$_rc stderr=$(head -c 160 "$TMP/erre.txt")"
# updatedInput WITHOUT a command (the explore-tier-pin model-pin shape) is not an
# EDIT of a shell command and must pass through unchanged.
cat >"$TMP/pin.sh" <<'PNS'
#!/usr/bin/env bash
cat >/dev/null
printf '%s' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","updatedInput":{"subagent_type":"Explore","model":"haiku"}}}'
exit 0
PNS
chmod +x "$TMP/pin.sh"
RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/pin.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/errp.txt"
_rc=$?
[ "$_rc" -eq 0 ] && [ ! -s "$TMP/errp.txt" ] \
  && ok "updatedInput without a command (model-pin shape) passes through unchanged" \
  || bad "model-pin shape changed: exit=$_rc stderr=$(head -c 120 "$TMP/errp.txt")"

# ── a payload over 128 KiB is still normalised (item 1a-3) ──────────────────
# The payload used to ride argv too; one argv element over MAX_ARG_STRLEN makes
# the exec fail (E2BIG) and the guard received snake_case, i.e. no decision.
python3 -c '
import json, sys
print(json.dumps({"session_id": "sess-big", "cwd": "/ws/p", "hook_event_name": "BeforeTool",
                  "tool_name": "run_shell_command",
                  "tool_input": {"command": "echo " + "A" * 140000}}))
' >"$TMP/big.json"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" pretool "$TMP/stub.sh" <"$TMP/big.json" >/dev/null 2>&1
[ "$(seen_tool)" = "Bash" ] \
  && ok "a $(wc -c <"$TMP/big.json" | tr -d ' ')-byte payload is normalised (guard sees Bash)" \
  || bad "large payload reached the guard as '$(seen_tool)', expected Bash"
cat >"$TMP/bash-deny.sh" <<'BDS'
#!/usr/bin/env bash
t="$(jq -r '.tool_name // empty' 2>/dev/null)"
[ "$t" = "Bash" ] && { printf 'denied a Bash call\n' >&2; exit 2; }
exit 0
BDS
chmod +x "$TMP/bash-deny.sh"
RC_OUT="$TMP" _run_ad bash "$AD" pretool "$TMP/bash-deny.sh" <"$TMP/big.json" >/dev/null 2>&1
_rc=$?
[ "$_rc" -eq 2 ] && ok "a large payload a Bash guard denies still returns exit 2" \
  || bad "large-payload deny lost: exit=$_rc"

# ── a normalisation FAILURE fails closed in pretool (item 1a-3) ─────────────
# Forced with a python3 that exits 1 ahead of the real one on PATH (jq stays real,
# so field reads still work and only the normaliser breaks).
mkdir -p "$TMP/badpy"
printf '#!/bin/sh\ncat >/dev/null\nexit 1\n' >"$TMP/badpy/python3"
chmod +x "$TMP/badpy/python3"
RC_OUT="$TMP" RC_RC=0 PATH="$TMP/badpy:$PATH" _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/errn.txt"
_rc=$?
[ "$_rc" -eq 2 ] && grep -q 'normalised' "$TMP/errn.txt" \
  && ok "a normalisation failure in pretool exits 2 with a reason (fail-closed)" \
  || bad "normalisation failure did not fail closed: exit=$_rc stderr=$(head -c 120 "$TMP/errn.txt")"

# ── MCP server boundary comes from .gemini/settings.json (item 1a-6) ────────
# mcp_github_create_issue used to become mcp__github_create_issue, so the
# tribunal read the SERVER as github_create_issue and an allow-listed github
# write was pre-denied as an unverified server.
MCPP="$TMP/mcpproj"; MCPH="$TMP/mcphome"
mkdir -p "$MCPP/.gemini" "$MCPP/.ravenclaude" "$MCPH"
printf '{"mcpServers":{"github":{"command":"x"},"my":{"command":"x"},"my_server":{"command":"x"}}}\n' >"$MCPP/.gemini/settings.json"
mcp_payload() {
  python3 -c '
import json, sys
print(json.dumps({"session_id": "s-mcp", "cwd": sys.argv[2], "hook_event_name": "BeforeTool",
                  "tool_name": sys.argv[1], "tool_input": {}}))
' "$1" "$2"
}
mcp_run() { # <raw-name> <project> -> the tool_name the guard saw
  RC_OUT="$TMP" RC_RC=0 HOME="$MCPH" _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(mcp_payload "$1" "$2")" >/dev/null 2>&1
  seen_tool
}
[ "$(mcp_run mcp_github_create_issue "$MCPP")" = "mcp__github__create_issue" ] \
  && ok "mcp_github_create_issue -> mcp__github__create_issue (server from settings)" \
  || bad "MCP name became '$(seen_tool)', expected mcp__github__create_issue"
[ "$(mcp_run mcp_my_server_do_thing "$MCPP")" = "mcp__my_server__do_thing" ] \
  && ok "longest matching server wins (my_server over my)" \
  || bad "longest-prefix MCP split wrong: '$(seen_tool)'"
mkdir -p "$TMP/nosettings"
[ "$(mcp_run mcp_github_create_issue "$TMP/nosettings")" = "mcp__github__create_issue" ] \
  && ok "no readable server list -> first-underscore split" \
  || bad "fallback MCP split wrong: '$(seen_tool)'"
# The consequence end to end: with mcp.allowed_servers: [github] the tribunal's
# deterministic screen must NOT pre-deny the normalised github write.
DECP="$HERE/../../scripts/thing-decision.py"
printf 'schema_version: 5\ncategories:\n  mcp_tools:\n    thing: on\n' >"$MCPP/.ravenclaude/comfort-posture.yaml"
printf 'mcp:\n  allowed_servers: [github]\n' >"$MCPP/.ravenclaude/thing.yaml"
cat >"$TMP/classify.sh" <<'CLS'
#!/usr/bin/env bash
python3 "$RC_DECP" --root "$CLAUDE_PROJECT_DIR" classify-payload 2>/dev/null \
  | jq -r '.pre_llm_deny' >"$RC_OUT/pld.txt" 2>/dev/null
exit 0
CLS
chmod +x "$TMP/classify.sh"
rm -f "$TMP/pld.txt"
RC_OUT="$TMP" RC_DECP="$DECP" HOME="$MCPH" _run_ad bash "$AD" pretool "$TMP/classify.sh" \
  <<<"$(mcp_payload mcp_github_create_issue "$MCPP")" >/dev/null 2>&1
if [ -f "$DECP" ] && [ -s "$TMP/pld.txt" ]; then
  [ "$(cat "$TMP/pld.txt")" != "true" ] \
    && ok "an allow-listed server write is NOT pre-denied after normalisation" \
    || bad "allow-listed github write was pre-denied (pre_llm_deny=true)"
  # positive control on the same screen: a NON-listed write IS pre-denied.
  RC_OUT="$TMP" RC_DECP="$DECP" HOME="$MCPH" _run_ad bash "$AD" pretool "$TMP/classify.sh" \
    <<<"$(mcp_payload mcp_slackbot_post_message "$MCPP")" >/dev/null 2>&1
  [ "$(cat "$TMP/pld.txt")" = "true" ] \
    && ok "control: a non-listed server write IS pre-denied on the same screen" \
    || bad "control failed: non-listed write not pre-denied ($(cat "$TMP/pld.txt"))"
else
  bad "could not run the tribunal classify-payload screen ($DECP)"
fi

# ── TEETH ───────────────────────────────────────────────────────────────────
MUT="$TMP/mutant.sh"
# Strip the normalisation: the guard then sees snake_case and MH-01 returns.
# ⛔ Anchored to the adapter's exact pretool capture line
# (`out="$(printf '%s' "$norm" | bash …)"`). If you change that line, update this
# pattern IN THE SAME COMMIT — when it stops matching, the gate FAILS LOUD
# ("adapter shape changed?") rather than silently skipping its teeth.
sed 's/^    out="$(printf .%s. "$norm" | bash "$real" "$@")"$/    out="$(printf %s "$payload" | bash "$real" "$@")"/' "$AD" >"$MUT"

# Teeth for the reason-preservation assertion: fold stderr into the capture
# (`2>&1`) so the sentinel vanishes from the adapter's stderr. Without this,
# "bytes arrived" proves nothing about whether the adapter is what let them through.
MUT2="$TMP/mutant-quiet.sh"
sed 's/^    out="$(printf \(.%s.\) "$norm" | bash "$real" "$@")"$/    out="$(printf \1 "$norm" | bash "$real" "$@" 2>\&1)"/' "$AD" >"$MUT2"
if grep -q '"$norm" | bash "$real" "$@" 2>&1' "$MUT2"; then
  RC_OUT="$TMP" bash "$MUT2" pretool "$TMP/loud.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/err2.txt"
  grep -q 'DENY_REASON_SENTINEL' "$TMP/err2.txt" \
    && bad "teeth: the 2>&1 mutant STILL carried the reason — the assertion is vacuous" \
    || ok "teeth: restoring 2>&1 loses the reason (the assertion measures the redirect)"
else
  bad "teeth: could not build the reason-discarding mutant (adapter shape changed?)"
fi
if grep -q 'printf %s "$payload" | bash' "$MUT"; then
  RC_OUT="$TMP" RC_RC=0 bash "$MUT" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
  [ "$(seen_tool)" = "run_shell_command" ] \
    && ok "teeth: without normalisation the guard sees run_shell_command (MH-01 returns)" \
    || bad "teeth: mutant still normalised — the assertions may be vacuous"
else
  bad "teeth: could not build the no-normalisation mutant (adapter shape changed?)"
fi

# Teeth for SH-F1 JSON-deny: strip the permissionDecision==deny → exit 2 branch.
MUT3="$TMP/mutant-json.sh"
sed 's/^      if \[ "$dec" = "deny" \]; then$/      if false; then/' "$AD" >"$MUT3"
if grep -q '^      if false; then$' "$MUT3"; then
  RC_OUT="$TMP" bash "$MUT3" pretool "$TMP/json-deny.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
  [ "$?" -ne 2 ] && ok "teeth: removing JSON-deny branch stops the exit-2 translation" \
    || bad "teeth: JSON-deny mutant still blocked — assertion may be vacuous"
else
  bad "teeth: could not build the no-JSON-deny mutant (adapter shape changed?)"
fi

# Teeth for the EDIT block (1a-5): with the updatedInput.command branch disabled
# the EDIT stub must be allowed again (the original defect, on demand).
MUT4="$TMP/mutant-edit.sh"
sed 's/^      if \[ -n "$rev" \]; then$/      if false; then/' "$AD" >"$MUT4"
if grep -q '^      if false; then$' "$MUT4"; then
  RC_OUT="$TMP" bash "$MUT4" pretool "$TMP/edit.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
  [ "$?" -eq 0 ] && ok "teeth: without the EDIT branch the rewrite is dropped again (rc 0)" \
    || bad "teeth: EDIT mutant still blocked — assertion may be vacuous"
else
  bad "teeth: could not build the no-EDIT mutant (adapter shape changed?)"
fi

# Teeth for fail-closed normalisation (1a-3): disable the guard and the forced
# python3 failure must proceed instead of blocking.
MUT5="$TMP/mutant-failopen.sh"
sed 's/^    if \[ "$nrc" -ne 0 \] || .*; then$/    if false; then/' "$AD" >"$MUT5"
if grep -q '^    if false; then$' "$MUT5"; then
  RC_OUT="$TMP" RC_RC=0 PATH="$TMP/badpy:$PATH" bash "$MUT5" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
  [ "$?" -ne 2 ] && ok "teeth: without the fail-closed guard a normalisation failure proceeds" \
    || bad "teeth: fail-open mutant still blocked — assertion may be vacuous"
else
  bad "teeth: could not build the fail-open mutant (adapter shape changed?)"
fi

# ── v0.7 observe-lane forwarding (spectate-emit needs stdin + CLAUDE_HOOK_EVENT) ─
SS_PAYLOAD='{"session_id":"sess-ss","cwd":"/ws/p","hook_event_name":"SessionStart"}'
rm -f "$TMP/stdin.json" "$TMP/env.txt"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" sessionstart "$TMP/stub.sh" <<<"$SS_PAYLOAD" >/dev/null 2>&1
if [ -s "$TMP/stdin.json" ] && grep -q 'HOOK_EVENT=SessionStart' "$TMP/env.txt"; then
  ok "sessionstart forwards payload stdin + CLAUDE_HOOK_EVENT=SessionStart"
else
  bad "sessionstart did not forward payload/event"
fi

POST_PAYLOAD='{"session_id":"sess-post","cwd":"/ws/p","hook_event_name":"AfterTool","tool_name":"write_file","tool_input":{"file_path":"/ws/p/a.txt"},"file_path":"/ws/p/a.txt"}'
rm -f "$TMP/stdin.json" "$TMP/env.txt"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" posttool "$TMP/stub.sh" <<<"$POST_PAYLOAD" >/dev/null 2>&1
if [ -s "$TMP/stdin.json" ] && grep -q 'HOOK_EVENT=PostToolUse' "$TMP/env.txt"; then
  # posttool must also normalise tool_name for observe hooks
  post_tool="$(python3 -c 'import json;print(json.load(open("'"$TMP"'/stdin.json")).get("tool_name"))' 2>/dev/null)"
  [ "$post_tool" = "Write" ] \
    && ok "posttool forwards normalised stdin + CLAUDE_HOOK_EVENT=PostToolUse" \
    || bad "posttool stdin tool_name=$post_tool (want Write)"
else
  bad "posttool did not forward payload/event"
fi

# v0.8: camelCase toolUseId → tool_use_id (do not mint when absent)
POST_ID='{"session_id":"sess-id","cwd":"/ws/p","hook_event_name":"AfterTool","tool_name":"replace","tool_input":{"file_path":"/ws/p/b.txt"},"file_path":"/ws/p/b.txt","toolUseId":"tu-gem-1"}'
rm -f "$TMP/stdin.json"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" posttool "$TMP/stub.sh" <<<"$POST_ID" >/dev/null 2>&1
if python3 -c '
import json
d=json.load(open("'"$TMP"'/stdin.json"))
assert d.get("tool_use_id")=="tu-gem-1", d
assert d.get("tool_name")=="Edit", d
' 2>/dev/null; then
  ok "posttool normalises toolUseId → tool_use_id"
else
  bad "posttool tool_use_id normalise failed: $(cat "$TMP/stdin.json" 2>/dev/null | head -c 200)"
fi

PRE_NO_ID='{"session_id":"sess-noid","cwd":"/ws/p","hook_event_name":"BeforeTool","tool_name":"run_shell_command","tool_input":{"command":"true"}}'
rm -f "$TMP/stdin.json"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$PRE_NO_ID" >/dev/null 2>&1
if python3 -c '
import json
d=json.load(open("'"$TMP"'/stdin.json"))
assert "tool_use_id" not in d, d
' 2>/dev/null; then
  ok "pretool does not mint tool_use_id when host omits it"
else
  bad "pretool invented tool_use_id: $(cat "$TMP/stdin.json" 2>/dev/null | head -c 200)"
fi

rm -f "$TMP/env.txt"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
grep -q 'HOOK_EVENT=PreToolUse' "$TMP/env.txt" \
  && ok "pretool sets CLAUDE_HOOK_EVENT=PreToolUse" \
  || bad "pretool missing CLAUDE_HOOK_EVENT=PreToolUse"

# ── v0.14 lifecycle observe lanes (SessionEnd / PreCompress / BeforeAgent / AfterAgent) ─
SE_PAYLOAD='{"session_id":"sess-se","cwd":"/ws/p","hook_event_name":"SessionEnd","reason":"exit"}'
rm -f "$TMP/stdin.json" "$TMP/env.txt"
se_out="$(RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" sessionend "$TMP/stub.sh" <<<"$SE_PAYLOAD" 2>/dev/null)"
if [ -s "$TMP/stdin.json" ] && grep -q 'HOOK_EVENT=SessionEnd' "$TMP/env.txt" && [ -z "$se_out" ]; then
  ok "sessionend forwards payload stdin + CLAUDE_HOOK_EVENT=SessionEnd; empty stdout"
else
  bad "sessionend wrong (out=$se_out env=$(cat "$TMP/env.txt" 2>/dev/null))"
fi

PC_PAYLOAD='{"session_id":"sess-pc","cwd":"/ws/p","hook_event_name":"PreCompress","trigger":"auto"}'
rm -f "$TMP/stdin.json" "$TMP/env.txt"
pc_out="$(RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" precompact "$TMP/stub.sh" <<<"$PC_PAYLOAD" 2>/dev/null)"
if [ -s "$TMP/stdin.json" ] && grep -q 'HOOK_EVENT=PreCompact' "$TMP/env.txt" && [ -z "$pc_out" ]; then
  ok "precompact forwards payload stdin + CLAUDE_HOOK_EVENT=PreCompact; empty stdout"
else
  bad "precompact wrong (out=$pc_out env=$(cat "$TMP/env.txt" 2>/dev/null))"
fi

BA_PAYLOAD='{"session_id":"sess-ba","cwd":"/ws/p","hook_event_name":"BeforeAgent","prompt":"hello"}'
rm -f "$TMP/stdin.json" "$TMP/env.txt"
RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" beforeagent "$TMP/stub.sh" <<<"$BA_PAYLOAD" >/dev/null 2>&1
if [ -s "$TMP/stdin.json" ] && grep -q 'HOOK_EVENT=UserPromptSubmit' "$TMP/env.txt"; then
  ok "beforeagent forwards payload stdin + CLAUDE_HOOK_EVENT=UserPromptSubmit"
else
  bad "beforeagent did not forward payload/event"
fi

# beforeagent must surface additionalContext only — never a decision:deny JSON
cat >"$TMP/ctx-stub.sh" <<'STUB'
#!/usr/bin/env bash
cat >"${RC_OUT}/stdin.json"
printf '%s\n' '{"hookSpecificOutput":{"additionalContext":"ctx-ok"},"decision":"deny"}'
exit 0
STUB
chmod +x "$TMP/ctx-stub.sh"
ba_out="$(RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" beforeagent "$TMP/ctx-stub.sh" <<<"$BA_PAYLOAD" 2>/dev/null)"
printf '%s' "$ba_out" | grep -q 'ctx-ok' && ! printf '%s' "$ba_out" | grep -q 'decision' \
  && ok "beforeagent surfaces additionalContext only (strips decision)" \
  || bad "beforeagent stdout leak: $ba_out"

AA_PAYLOAD='{"session_id":"sess-aa","cwd":"/ws/p","hook_event_name":"AfterAgent","prompt":"p","prompt_response":"r"}'
rm -f "$TMP/stdin.json" "$TMP/env.txt"
cat >"$TMP/deny-stub.sh" <<'STUB'
#!/usr/bin/env bash
cat >"${RC_OUT}/stdin.json"
printf 'HOOK_EVENT=%s\n' "${CLAUDE_HOOK_EVENT:-}" >"${RC_OUT}/env.txt"
printf '%s\n' '{"decision":"deny","reason":"retry-me"}'
exit 0
STUB
chmod +x "$TMP/deny-stub.sh"
aa_out="$(RC_OUT="$TMP" RC_RC=0 _run_ad bash "$AD" afteragent "$TMP/deny-stub.sh" <<<"$AA_PAYLOAD" 2>/dev/null)"
if [ -s "$TMP/stdin.json" ] && grep -q 'HOOK_EVENT=Stop' "$TMP/env.txt" && [ -z "$aa_out" ]; then
  ok "afteragent forwards stdin + CLAUDE_HOOK_EVENT=Stop; discards decision stdout"
else
  bad "afteragent wrong (out=$aa_out env=$(cat "$TMP/env.txt" 2>/dev/null))"
fi

printf '\n  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
