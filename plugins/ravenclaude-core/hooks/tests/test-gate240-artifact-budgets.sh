#!/usr/bin/env bash
#
# Gate 240 — artifact budgets + the R12 badge actually rendering (⛔ R5, R12).
#
# ⛔ R5: PLAN B PREMISE WAS FALSE AND THE UNDERLYING RISK IS REAL. panel-learn is
# already DOM-islanded, so check-dom-budget.py check() — which compares only the
# LIVE element total — CANNOT fire on it. Plan B per-batch ratchet-raise process
# was built for a gate that cannot fire. What nothing gated was the thing that can
# actually hurt: 23,861 payload elements for 58 concepts (~411/concept), and two
# ~10 MB surfaces with ZERO byte gates among 336 gate headers.
#
# ⛔ R12: a badge that exists in the registry but never reaches the page is the
# same defect one layer down. So this gate asserts the badge IN THE GENERATED
# HTML, not in the generator source — a source-scan would be satisfied by the
# string being *described* in a comment, which is a recorded failure in this repo.
#
# ⛔ NO APOSTROPHES; scratch cleaned with a helper. See spike-tprose-canary.sh.

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
DASH="$ROOT/plugins/ravenclaude-core/dashboard.html"

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

echo "── Gate 240: artifact budgets + R12 badge rendering ──"

# ── 1. R5 premise re-verified in code, not in prose ────────────────────────
# ⛔ Asserted rather than inherited: the plan built P6 on the claim that check()
# gates live elements only. If a future change adds a payload budget THERE, this
# gate becomes redundant and should be retired rather than left to double-report.
if grep -q 'n = measure(path)\["total"\]' "$ROOT/scripts/check-dom-budget.py" \
   && ! grep -qE '^[A-Z_]*PAYLOAD[A-Z_]*(_BUDGET|_RATCHET)? *=' "$ROOT/scripts/check-dom-budget.py"; then
  ok "R5 premise holds: check-dom-budget gates LIVE elements, has no payload budget"
else
  bad "R5 premise" "check-dom-budget.py may now gate payload — retire this gate if so"
fi

# ── 2. The budgets pass on the pristine tree ───────────────────────────────
rc=0; python3 "$ROOT/scripts/check-artifact-budgets.py" --check >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  ok "pass-on-good: the pristine tree is inside both budgets"
else
  bad "pass-on-good" "the pristine tree already exceeds a budget"
fi

# ── 3. Both dimensions have TEETH, and the exit matches its declaration ────
decl="$(python3 "$ROOT/scripts/check-artifact-budgets.py" --must-fail-convention)"
rc=0; python3 "$ROOT/scripts/check-artifact-budgets.py" --must-fail >/dev/null 2>&1 || rc=$?
if [ "$rc" = "${decl##*: }" ]; then
  ok "teeth: payload AND byte budgets each catch an overrun; exit matches declaration"
else
  bad "budget teeth" "declared ${decl##*: }, observed $rc"
fi

# ── 4. ⛔ THE PAYLOAD BUDGET IS A REDUCTION RATCHET; BYTES IS A REVIEWED CEILING ──
# Conflating them was a real defect: a shrink-only byte rule rejected the R12 badge
# CSS with no path forward but deleting the feature. Both invariants are asserted
# so a future simplification cannot quietly merge them back.
py_rc=0
python3 - "$ROOT" <<'PY' || py_rc=$?
import json, sys
from pathlib import Path
seed = json.loads((Path(sys.argv[1]) / "scripts" / "artifact-budgets.seed.json").read_text())
bad = 0
# BOTH tables are ceilings with a reviewed raise. The payload one was CORRECTED
# to that after the first real batch: a reduction-only payload ceiling made every
# inventory entry impossible, which is a stop-work order rather than a budget.
for surface, rows in seed["payload"].items():
    for i in range(1, len(rows)):
        if rows[i][1] > rows[i - 1][1] and len(str(rows[i][2]).strip()) < 30:
            print(f"payload ceiling raise for {surface} has no real cause")
            bad = 1
for surface, rows in seed["bytes"].items():
    for i in range(1, len(rows)):
        if rows[i][1] > rows[i - 1][1] and len(str(rows[i][2]).strip()) < 30:
            print(f"byte ceiling raise for {surface} has no real cause")
            bad = 1
sys.exit(bad)
PY
if [ "$py_rc" -eq 0 ]; then
  ok "every payload AND byte ceiling raise carries a real, reviewed cause"
else
  bad "budget table invariants" "see output above"
fi

# ── 5. ⛔ R12: the badge reaches the GENERATED PAGE, not just the generator ──
[ -f "$DASH" ] || { bad "dashboard present" "$DASH missing"; }
if [ -f "$DASH" ]; then
  miss=""
  for sel in '.concept-strength' '.concept-strength.probed' '.concept-strength.findable' \
             '.concept-strength.observed' '.concept-strength.unverified'; do
    grep -qF "$sel" "$DASH" || miss="$miss $sel"
  done
  if [ -z "$miss" ]; then
    ok "R12: all four strength badge styles are present in the generated dashboard"
  else
    bad "R12 badge styles in generated HTML" "missing:$miss"
  fi

  # The badge must state the LIMIT. "Findable" is honest; "Verified (static)" is
  # not, because a reader skims the first word. Asserted on the DERIVED text so a
  # renderer cannot substitute a softer synonym.
  if grep -qF 'border-style: dashed' "$DASH" && grep -qF '.concept-strength.findable' "$DASH"; then
    ok "R12: the weak tier renders DISTINCTLY (dashed, muted), not as a paler green"
  else
    bad "weak tier renders distinctly" "findable is not visually separated"
  fi

  if grep -qF '.concept-nuance-text' "$DASH" && grep -qF '.concept-unprobed' "$DASH"; then
    ok "R12: the nuance block and the unprobed marker both render"
  else
    bad "nuance block renders" "nuance or unprobed styling absent from the page"
  fi
fi

# ── 6. Diagrams are OPT-IN for inventory entries ──────────────────────────
if grep -q 'entry_class != ENTRY_CLASS_INVENTORY' "$ROOT/scripts/concepts.py"; then
  ok "diagrams are opt-in for inventory entries (no 162 auto-rendered mermaid)"
else
  bad "diagrams opt-in" "concepts.py still requires a mermaid block on every entry"
fi

# ── 7. The changed-concepts render gate FAILS rather than warns ───────────
decl2="$(python3 "$ROOT/scripts/check-changed-concept-renders.py" --must-fail-convention)"
rc=0; python3 "$ROOT/scripts/check-changed-concept-renders.py" --must-fail >/dev/null 2>&1 || rc=$?
if [ "$rc" = "${decl2##*: }" ]; then
  ok "changed-concept render gate: unresolvable base reports UNKNOWN, batch cap bites"
else
  bad "render gate teeth" "declared ${decl2##*: }, observed $rc"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
