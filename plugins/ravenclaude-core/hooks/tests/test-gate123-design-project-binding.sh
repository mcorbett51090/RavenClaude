#!/usr/bin/env bash
# Gate 123 — design-project binding surfacing in the capability banner.
# Drives the REAL capability-orientation.py against temp project roots:
#   A bound: .ravenclaude/design-project.json with a project_id -> banner shows the
#     "LINKED DESIGN PROJECT … You CAN read it as context and edit it" line.
#   B present-no-id: a binding file with empty project_id -> banner shows the
#     "no project_id yet … /design-link" guidance.
#   C absent: no binding file -> the banner omits the LINKED DESIGN PROJECT line.
#   D leak-safe: the project_id UUID VALUE never appears in the banner (pointer only).
#   E teeth (must-fail half): a copy of the script with the design block neutered
#     (`if False`) no longer shows the line for the bound case.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$(cd "$HERE/../.." && pwd)/scripts/capability-orientation.py"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

PID="aaaabbbb-cccc-dddd-eeee-ffff00001111"
banner() { # $1=script $2=root -> the additionalContext string
  python3 "$1" --root "$2" 2>/dev/null \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['hookSpecificOutput']['additionalContext'])" 2>/dev/null
}

TMP="$(mktemp -d)"

# A — bound (project_id set)
A="$TMP/bound"; mkdir -p "$A/.ravenclaude"
printf '{"project_id":"%s","name":"Acme DS","mirror_dir":"design/"}\n' "$PID" >"$A/.ravenclaude/design-project.json"
outA="$(banner "$SCRIPT" "$A")"
printf '%s' "$outA" | grep -q "LINKED DESIGN PROJECT" && printf '%s' "$outA" | grep -q "You CAN read it as context" \
  && pass "A: bound project surfaces the LINKED DESIGN PROJECT line" || fail "A: bound line missing"

# D — leak-safe: the UUID value must NOT be in the banner
printf '%s' "$outA" | grep -q "$PID" && fail "D: project_id VALUE leaked into the banner" \
  || pass "D: leak-safe — project_id value not in the banner (pointer only)"

# B — present but no id
B="$TMP/noid"; mkdir -p "$B/.ravenclaude"
printf '{"project_id":"","name":"Half-set DS","mirror_dir":""}\n' >"$B/.ravenclaude/design-project.json"
outB="$(banner "$SCRIPT" "$B")"
printf '%s' "$outB" | grep -q "no project_id yet" && printf '%s' "$outB" | grep -q "/design-link" \
  && pass "B: present-no-id surfaces the /design-link guidance" || fail "B: no-id guidance missing"

# C — absent
C="$TMP/none"; mkdir -p "$C/.ravenclaude"
printf 'schema_version: 5\n' >"$C/.ravenclaude/comfort-posture.yaml"
outC="$(banner "$SCRIPT" "$C")"
printf '%s' "$outC" | grep -q "LINKED DESIGN PROJECT" && fail "C: absent binding still showed the line" \
  || pass "C: no binding file -> line omitted (graceful)"

# E — teeth: neuter the design banner block; the bound case must stop showing the line
MUT="$TMP/mut-capability-orientation.py"
sed 's/if design and design.get("present"):/if False:/' "$SCRIPT" >"$MUT"
if ! grep -q "if False:" "$MUT"; then
  fail "E: could not neuter the design block (sed no-op — fixture stale)"
else
  outE="$(banner "$MUT" "$A")"
  printf '%s' "$outE" | grep -q "LINKED DESIGN PROJECT" \
    && fail "E: must-fail — neutered script STILL showed the line (no teeth)" \
    || pass "E: must-fail half — neutered design block omits the line (surfacing is load-bearing)"
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 123 PASS — design-project binding: surfaces when bound, guides when half-set, silent when absent, leak-safe, has teeth."
  exit 0
else
  echo "Gate 123 FAIL — $fails subtest(s) failed."
  exit 1
fi
