#!/usr/bin/env bash
# Gate 105 — Heimdall authored-content carve-out for file_edit_project.
#
# Regression guard for the false-positive fix (2026-06-23): the Heimdall injection
# seat denied benign Markdown doc edits because it read normal document structure
# (<details>/<summary>/</details>) as a "forged closing delimiter" and a status-word
# diff (DONE→IN PROGRESS) as "task-state manipulation". The fix adds a static,
# trusted resolved-fact line to the seat prompt for file_edit_project ONLY, telling
# the seat the payload is the agent's own authored edit to a trusted file.
#
# This test is deterministic (NO live model call): it reconstructs the seat prompt
# for several categories and asserts the carve-out is present for file_edit_project,
# absent for every other shape, and that the deterministic concern screen never
# flagged the two triggers (so the fix targets the LLM-seat layer, not the regex).
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
SEAT="plugins/ravenclaude-core/scripts/thing-seat.sh"
CONC="plugins/ravenclaude-core/scripts/thing-concerns.py"
RC=0
pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; RC=1; }

# Extract the authored_note + user_prompt construction block from the real seat.
SNIP="$(awk '/^authored_note=""/{f=1} f{print} f && /^<\/untrusted/{exit}' "$SEAT")"
[ -n "$SNIP" ] || { echo "FATAL: could not extract user_prompt block from $SEAT"; exit 1; }

build_prompt() { # $1 = category → echoes the constructed user_prompt
  local category="$1" shape="Write" safe_project_dir="/repo" nonce="NONCE" safe_cmd="docs/x.md"
  eval "$SNIP"
  printf '%s' "$user_prompt"
}

# 1. file_edit_project carries the carve-out, naming both reported false-positive shapes.
P="$(build_prompt file_edit_project)"
echo "$P" | grep -q "OWN authored edit"        && pass "file_edit_project carries the authored-content carve-out" || fail "carve-out missing for file_edit_project"
echo "$P" | grep -q "<details>"                && pass "carve-out names <details> structural tags"                || fail "carve-out omits <details>"
echo "$P" | grep -q "task-state manipulation"  && pass "carve-out names the status-word (DONE→IN PROGRESS) shape"  || fail "carve-out omits the status-word shape"

# 2. Scoping teeth: NO other shape gets the carve-out (it must not weaken the injection screen elsewhere).
for c in shell_readonly file_edit_global network_write mcp_tools file_read_global; do
  if build_prompt "$c" | grep -q "OWN authored edit"; then
    fail "carve-out LEAKED into $c (must be file_edit_project-only)"
  else
    pass "$c keeps the full injection screen (no carve-out)"
  fi
done

# 3. Deterministic screen stays clean on the two triggers (proves cause was the LLM seat, fix is at the right layer).
ncount() { python3 "$CONC" evaluate --category file_edit_project "$1" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);c=d.get('concerns',[]);print(len(c) if isinstance(c,list) else 1)"; }
[ "$(ncount $'docs/a.md\n<details><summary>x</summary>\n</details>')" = "0" ] \
  && pass "deterministic screen clean on <details> content" || fail "deterministic screen flagged <details> (cause is NOT the regex layer)"
[ "$(ncount $'docs/a.md\nStatus: DONE\nStatus: IN PROGRESS')" = "0" ] \
  && pass "deterministic screen clean on DONE→IN PROGRESS diff" || fail "deterministic screen flagged the status diff"

# 4. must-fail (teeth): with the file_edit_project guard forced off, the carve-out
#    vanishes — proving assertion #1 above genuinely detects a regressed fix.
SNIP_BROKEN="$(printf '%s' "$SNIP" | sed 's/if \[ "\$category" = "file_edit_project" \]; then/if false; then/')"
build_broken() { local category="file_edit_project" shape="Write" safe_project_dir="/repo" nonce="N" safe_cmd="x"; eval "$SNIP_BROKEN"; printf '%s' "$user_prompt"; }
if build_broken | grep -q "OWN authored edit"; then
  fail "[teeth] stripped carve-out still present — gate would not catch a regression"
else
  pass "[teeth] stripped carve-out is absent — assertion #1 has teeth"
fi

if [ "$RC" -eq 0 ]; then echo "Gate 105: PASS"; else echo "Gate 105: FAIL"; fi
exit "$RC"
