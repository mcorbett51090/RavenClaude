#!/usr/bin/env bash
# Gate 122 — delegation-nudge.sh (Capability Grounding consult-your-access-inventory,
# written-artifact surface). Bidirectional:
#   A fires-on-bad: a "open the portal and check the run history" line in a knowledge/
#     file (under a comfort-posture project) emits the nudge.
#   B silent-on-good: a hand-back-with-reason line, a line citing the held route, a
#     `delegation-nudge-ok` line, a non-knowledge file, and a no-posture project are
#     all silent.
#   C teeth (must-fail half): a copy of the hook with the suppression greps neutered
#     fires on the hand-back-with-reason line that the real hook suppresses.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$(cd "$HERE/.." && pwd)/delegation-nudge.sh"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

TMP="$(mktemp -d)"
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude" "$PROJ/plugins/x/knowledge" "$PROJ/src"
printf 'schema_version: 5\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"

# fires? = the hook printed the nudge marker to stderr (it always exits 0 — advisory).
# Capture stderr to a var first: piping the hook into `grep -q` lets grep close the
# pipe early (SIGPIPE 141), and pipefail would then misreport a real fire as a miss.
fires() { # $1=hook $2=file
  local out
  out="$("$1" "$2" 2>&1 1>/dev/null)"
  printf '%s' "$out" | grep -q "Delegation nudge"
}

KN="$PROJ/plugins/x/knowledge"

# A — bad: portal-delegation line in a knowledge file
printf '# Flow runs\n\nTo see if it failed, open the Power Automate portal and check the run history.\n' >"$KN/bad.md"
fires "$HOOK" "$KN/bad.md" && pass "A: portal-delegation line in knowledge/ fires the nudge" \
  || fail "A: bad line did NOT fire"

# B1 — good: hand-back WITH a reason (CGP Rule 4) -> suppressed
printf '# Flow runs\n\nUnless you hold the SPN, you should manually check the run history in the portal.\n' >"$KN/reason.md"
fires "$HOOK" "$KN/reason.md" && fail "B1: hand-back-with-reason should be suppressed" \
  || pass "B1: hand-back-with-reason suppressed"

# B2 — good: line cites the held route -> suppressed
printf '# Flow runs\n\nCheck the run history yourself: GET /api/data/v9.2/flowruns with the SPN.\n' >"$KN/route.md"
fires "$HOOK" "$KN/route.md" && fail "B2: route-citing line should be suppressed" \
  || pass "B2: line citing the held route suppressed"

# B3 — good: escape comment -> suppressed
printf '# Flow runs\n\nopen the portal and check the run history. <!-- delegation-nudge-ok -->\n' >"$KN/escape.md"
fires "$HOOK" "$KN/escape.md" && fail "B3: delegation-nudge-ok should suppress" \
  || pass "B3: delegation-nudge-ok escape suppresses"

# B4 — good: non-knowledge/docs file -> no-op
printf 'open the portal and check the run history\n' >"$PROJ/src/notes.md"
fires "$HOOK" "$PROJ/src/notes.md" && fail "B4: non-knowledge/docs file should be a no-op" \
  || pass "B4: non-knowledge/docs file is a no-op"

# B5 — good: no comfort-posture -> no-op
NOPOSTURE="$TMP/noposture/knowledge"
mkdir -p "$NOPOSTURE"
printf '# x\n\nopen the portal and check the run history.\n' >"$NOPOSTURE/x.md"
fires "$HOOK" "$NOPOSTURE/x.md" && fail "B5: no comfort-posture should be a no-op" \
  || pass "B5: opt-in — no comfort-posture is a no-op"

# C — teeth: neuter the suppression greps; the reason line must then fire
MUT="$TMP/mut-delegation-nudge.sh"
sed -e 's/grep -qiE "\$reason" && continue/grep -qiE "\$reason" \&\& :/' \
    -e 's/grep -qE "\$route" && continue/grep -qE "\$route" \&\& :/' \
    "$HOOK" >"$MUT"
chmod +x "$MUT"
if ! grep -q '&& :' "$MUT"; then
  fail "C: could not neuter the suppression (sed no-op — fixture stale)"
else
  fires "$MUT" "$KN/reason.md" \
    && pass "C: must-fail half — neutered suppression fires on the reason line (suppression is load-bearing)" \
    || fail "C: must-fail — neutered hook STILL suppressed the reason line (no teeth)"
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 122 PASS — delegation-nudge fires on delegation prose, stays silent on reason/route/escape/scope/opt-out, has teeth."
  exit 0
else
  echo "Gate 122 FAIL — $fails subtest(s) failed."
  exit 1
fi
