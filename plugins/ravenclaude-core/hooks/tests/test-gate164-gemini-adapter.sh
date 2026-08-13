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

# ── TEETH ───────────────────────────────────────────────────────────────────
MUT="$TMP/mutant.sh"
# Strip the normalisation: the guard then sees snake_case and MH-01 returns.
sed 's/^    _normalise | bash "$real" "$@" >\/dev\/null 2>&1$/    printf %s "$payload" | bash "$real" "$@" >\/dev\/null 2>\&1/' "$AD" >"$MUT"
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
