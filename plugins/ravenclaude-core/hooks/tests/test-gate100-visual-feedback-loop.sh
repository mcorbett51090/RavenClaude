#!/usr/bin/env bash
# Gate 100 — visual-feedback-loop driver, bidirectional + path-parity + teeth.
#
# Proves the referee (driver.py) is a real gate, not a rubber stamp:
#   • must_pass: clean layout-only (BI structural-first), full clean evidence,
#     and an empty web config (passed:null = needs-more, NOT a failure) → exit 0.
#   • must_fail: a layout violation, console errors, and a sub-threshold
#     Lighthouse score each → exit 1.
#   • path safety: a "../" traversal config is rejected → exit 2, AND the
#     delegated linter rejects the same shape (parity — the two guards can't
#     silently diverge).
#   • teeth: a mutant driver that hardcodes passed=true makes a known-bad
#     fixture pass — proving the real fail verdict is the logic, not luck.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
D="python3 plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py"
LINT="python3 plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py"
F="tests/fixtures/visual-feedback-loop"
rc_total=0

expect() { # desc, want_rc, file
  local rc=0
  $D "$3" >/dev/null 2>&1 || rc=$?
  if [[ "$rc" -eq "$2" ]]; then
    echo "  ✓ $1 (exit $rc)"
  else
    echo "  ✗ $1 — wanted exit $2, got $rc"
    rc_total=1
  fi
}

echo "── Gate 100: visual-feedback-loop driver ─────────────────────────────────"
# must_pass
expect "good layout-only (BI structural-first → ship)" 0 "$F/good-config-layout-only.json"
expect "good full evidence (web → ship)"               0 "$F/good-config-full-evidence.json"
expect "empty web (passed:null = needs-more, not fail)" 0 "$F/empty-config-web.json"
# must_fail
expect "bad layout (overlap → fix-layout)"             1 "$F/bad-config-layout-fail.json"
expect "console errors → fix-console-errors"           1 "$F/bad-config-console-errors.json"
expect "lighthouse below threshold → improve"          1 "$F/bad-config-lighthouse-low.json"
# parity: structural diff vs. a known-good exemplar (asymmetric render-risk: fail on MISSING, pass benign additions)
expect "parity match (same skeleton → ship)"           0 "$F/good-config-parity-match.json"
expect "parity non-comparable type (not_captured)"     0 "$F/parity-config-noncomparable.json"
# must-FAIL — the candidate is missing something the exemplar carries
expect "parity dropped object key (calloutValue) fails" 1 "$F/bad-config-parity-calloutvalue.json"
expect "parity missing query role fails"               1 "$F/bad-config-parity-wrongrole.json"
expect "parity missing \$id fails"                     1 "$F/bad-config-parity-idmissing.json"
expect "parity pure-drop (no substitute) fails"        1 "$F/bad-config-parity-puredrop.json"
expect "parity no query role on candidate fails"       1 "$F/bad-config-parity-noquery.json"
expect "parity partial-\$id (one item missing) fails"  1 "$F/bad-config-parity-partialid.json"
# must-PASS — benign additions are NOT render-risk (false-positive regression locks)
expect "parity superset object key (benign wordWrap → ship)" 0 "$F/good-config-parity-superset-key.json"
expect "parity superset role (Values+Tooltips → ship)" 0 "$F/good-config-parity-superset-role.json"
# not_captured (exit 0) — exemplar validation: a bad/degenerate/self reference can't launder a ship
expect "parity degenerate reference (no role) not_captured" 0 "$F/parity-config-bad-reference.json"
expect "parity self-reference not_captured"            0 "$F/parity-config-selfref.json"
# path rejection — both the layout AND the parity.candidate path are guarded
expect "traversal config rejected"                     2 "$F/bad-config-traversal.json"
expect "parity candidate traversal rejected"           2 "$F/bad-config-parity-traversal.json"

# parity: the delegated linter rejects the same '..' shape (exit 2)
rc=0; $LINT "../../etc/passwd" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 2 ]]; then
  echo "  ✓ path-guard parity (driver + linter both reject '..' → exit 2)"
else
  echo "  ✗ path-guard parity — linter did not reject '..' with exit 2 (got $rc)"
  rc_total=1
fi

# teeth: a mutant that always reports passed=true must make a known-bad pass.
MUT="$(mktemp --suffix=.py)"
trap 'rm -f "$MUT"' EXIT
sed 's/"passed": verdict\["passed"\]/"passed": True/' \
  plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py >"$MUT"
rc=0; python3 "$MUT" "$F/bad-config-layout-fail.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant (always-pass) lets bad-layout through → real fail is logic, not luck"
else
  echo "  ✗ teeth: mutant did NOT pass the bad fixture (got $rc) — teeth assertion is broken"
  rc_total=1
fi

# parity teeth: a mutant that neuters the skeleton-divergence detection (always
# reports the parity gate "pass") must let a known-divergent fixture through —
# proving the parity fail is the diff logic, not luck.
MUTP="$(mktemp --suffix=.py)"
trap 'rm -f "$MUT" "$MUTP"' EXIT
sed 's/record\["status"\] = "fail" if deltas else "pass"/record["status"] = "pass"/' \
  plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py >"$MUTP"
rc=0; python3 "$MUTP" "$F/bad-config-parity-calloutvalue.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant (parity always-pass) lets divergent visual through → real fail is the diff"
else
  echo "  ✗ teeth: parity mutant did NOT pass the divergent fixture (got $rc) — teeth assertion broken"
  rc_total=1
fi

if [[ "$rc_total" -eq 0 ]]; then
  echo "  Gate 100: PASS"
else
  echo "  Gate 100: FAIL"
fi
exit "$rc_total"
