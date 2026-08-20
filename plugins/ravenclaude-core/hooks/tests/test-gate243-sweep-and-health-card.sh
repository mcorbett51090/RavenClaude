#!/usr/bin/env bash
#
# Gate 243 — the scheduled sweep contract and the operator health card (P10, P11).
#
# ⛔ A SCHEDULED WORKFLOW MUST NEVER BE A REQUIRED STATUS CHECK. It reports
# NOTHING on a pull request, and a required check that reports nothing leaves the
# PR Pending forever — the same mechanism that makes a paths: filter on a required
# check fatal. So the sweep workflow is asserted to carry no pull_request trigger,
# STRUCTURALLY, by parsing its YAML rather than grepping its text.
#
# ⛔ THE HEALTH CARD IS ASSERTED IN THE GENERATED PAGE, never in the generator
# source. A source scan is satisfied by the string being DESCRIBED in a comment,
# which is a recorded failure class in this repo.
#
# ⛔ THE CENSUS COUNTING RULE MUST BE STATED, not inherited. claims-table row 5
# said 48 hooks; two independent measures returned 47. That is a counting-rule
# difference, and the fix is a rule written where it cannot drift.
#
# ⛔ NO APOSTROPHES. See scripts/spike-tprose-canary.sh.

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

echo "── Gate 243: scheduled sweep contract + operator health card ──"

WF="$ROOT/.github/workflows/inventory-sweep.yml"
if [ -f "$WF" ]; then
  ok "the scheduled sweep workflow exists"
  py_rc=0
  python3 - "$WF" <<'PY' || py_rc=$?
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
trig = d.get("on", d.get(True))
if not isinstance(trig, dict):
    print("no parseable on: mapping"); sys.exit(1)
if "pull_request" in trig:
    print("carries a pull_request trigger, so it could become a gating check"); sys.exit(1)
if "schedule" not in trig or "workflow_dispatch" not in trig:
    print("missing schedule or workflow_dispatch"); sys.exit(1)
cron = str(trig["schedule"][0]["cron"]).split()[0]
if cron == "0":
    print("scheduled on the hour; scheduler spikes add latency that reads as a hang")
    sys.exit(1)
PY
  if [ "$py_rc" -eq 0 ]; then
    ok "sweep triggers are schedule + workflow_dispatch ONLY, and off the hour"
  else
    bad "sweep trigger contract" "see output above"
  fi

  # ⛔ CONTROL. The assertion must be capable of failing: a fixture WITH a
  # pull_request trigger must be rejected, or the pass above is vacuous.
  TMPWF="$(mktemp)"
  printf 'on:\n  pull_request:\n  schedule:\n    - cron: "23 5 * * *"\n  workflow_dispatch:\njobs:\n  a:\n' > "$TMPWF"
  ctl=0
  python3 - "$TMPWF" >/dev/null 2>&1 <<'PY' || ctl=$?
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
trig = d.get("on", d.get(True))
sys.exit(1 if "pull_request" in trig else 0)
PY
  command rm -f "$TMPWF"
  if [ "$ctl" -ne 0 ]; then
    ok "CONTROL: a fixture WITH a pull_request trigger is rejected"
  else
    bad "trigger assertion has teeth" "a pull_request fixture was accepted"
  fi
else
  bad "sweep workflow exists" "$WF missing"
fi

# ── The health card, in the GENERATED page ─────────────────────────────────
DASH="$ROOT/plugins/ravenclaude-core/dashboard.html"
if [ -f "$DASH" ]; then
  miss=""
  for sel in 'operator-health-card' 'ohc-grid' 'ohc-foot' 'artifacts covered'; do
    grep -qF "$sel" "$DASH" || miss="$miss $sel"
  done
  if [ -z "$miss" ]; then
    ok "the operator health card renders in the generated dashboard"
  else
    bad "health card in generated HTML" "missing:$miss"
  fi
else
  bad "dashboard present" "$DASH missing"
fi

# ── The census counting rule is STATED ────────────────────────────────────
rule="$(python3 "$ROOT/scripts/inventory-census.py" --explain 2>/dev/null)"
if printf '%s' "$rule" | grep -q 'underscore-prefixed' \
   && printf '%s' "$rule" | grep -q '47-vs-48'; then
  ok "the census counting rule is written down, including the 47-vs-48 divergence"
else
  bad "census rule stated" "--explain does not name the counting rule"
fi

hooks="$(python3 "$ROOT/scripts/inventory-census.py" --json 2>/dev/null \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["counts"]["hook"])' 2>/dev/null)"
if [ "$hooks" = "47" ]; then
  ok "claim 5 re-measured under the stated rule: 47 hooks, not 48"
else
  bad "claim 5 re-measure" "census reports $hooks hooks"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
