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
  printf 'THING_HOST=%s\n'  "${THING_HOST:-}"; } >"$RC_OUT/env.txt"
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

run() { RC_OUT="$TMP" RC_RC="${2:-0}" bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload "$1")" >/dev/null 2>&1; }
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
RC_OUT="$TMP" RC_RC=2 bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
[ "$?" -eq 2 ] && ok "exit 2 (block) passes through untouched" || bad "exit 2 did not propagate"

RC_OUT="$TMP" RC_RC=0 bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
[ "$?" -eq 0 ] && ok "exit 0 (allow) passes through" || bad "exit 0 did not propagate"

out="$(RC_OUT="$TMP" RC_RC=2 bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" 2>/dev/null)"
[ -z "$out" ] && ok "emits NO stdout JSON — nothing to get wrong on the deny path" \
  || bad "emitted stdout on deny: ${out:0:60}"

# ── env lift ────────────────────────────────────────────────────────────────
run run_shell_command
grep -q '^PROJECT_DIR=/ws/p$' "$TMP/env.txt" && ok "cwd -> CLAUDE_PROJECT_DIR" || bad "CLAUDE_PROJECT_DIR unset"
grep -q '^SESSION_ID=sess-9$' "$TMP/env.txt" && ok "session_id -> CLAUDE_SESSION_ID" || bad "CLAUDE_SESSION_ID unset"
grep -q '^THING_HOST=gemini$' "$TMP/env.txt" && ok "THING_HOST asserted as gemini" || bad "THING_HOST not gemini"

# ── fail-safe ───────────────────────────────────────────────────────────────
RC_OUT="$TMP" bash "$AD" pretool "$TMP/missing.sh" <<<"$(payload run_shell_command)" >/dev/null 2>&1
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

RC_OUT="$TMP" bash "$AD" pretool "$TMP/loud.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/err.txt"
_rc=$?
[ "$_rc" -eq 2 ] && grep -q 'DENY_REASON_SENTINEL' "$TMP/err.txt" \
  && ok "a deny carries its reason through to stderr (exit 2 + reason, both halves)" \
  || bad "deny reason lost: exit=$_rc bytes=$(wc -c <"$TMP/err.txt" | tr -d ' ')"

# The negative control — an ALLOW must stay quiet, or the fix just becomes noise
# on every tool call.
RC_OUT="$TMP" RC_RC=0 bash "$AD" pretool "$TMP/stub.sh" <<<"$(payload run_shell_command)" >/dev/null 2>"$TMP/err0.txt"
[ ! -s "$TMP/err0.txt" ] \
  && ok "an allow emits no stderr (the fix adds no per-call noise)" \
  || bad "allow leaked $(wc -c <"$TMP/err0.txt" | tr -d ' ') bytes of stderr"

# ── TEETH ───────────────────────────────────────────────────────────────────
MUT="$TMP/mutant.sh"
# Strip the normalisation: the guard then sees snake_case and MH-01 returns.
# ⛔ This sed is anchored to the adapter's exact pretool line. If you change that
# line, update this pattern IN THE SAME COMMIT — when it stops matching, the gate
# FAILS LOUD ("adapter shape changed?") rather than silently skipping its teeth.
# That is by design and it fired correctly on 2026-08-12 when the `2>&1` was
# removed; do not "fix" it by loosening the anchor to a substring match.
sed 's/^    _normalise | bash "$real" "$@" >\/dev\/null$/    printf %s "$payload" | bash "$real" "$@" >\/dev\/null/' "$AD" >"$MUT"

# Teeth for the reason-preservation assertion: restore the `2>&1` and the
# sentinel must vanish. Without this, "233 bytes arrived" proves nothing about
# whether the adapter is what let them through.
MUT2="$TMP/mutant-quiet.sh"
sed 's/^    _normalise | bash "$real" "$@" >\/dev\/null$/    _normalise | bash "$real" "$@" >\/dev\/null 2>\&1/' "$AD" >"$MUT2"
if grep -q '_normalise | bash "$real" "$@" >/dev/null 2>&1' "$MUT2"; then
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

printf '\n  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
