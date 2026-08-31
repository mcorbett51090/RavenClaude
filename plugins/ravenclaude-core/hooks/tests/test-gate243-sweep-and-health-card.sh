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

# ⛔ DO NOT PIN THE COUNT. This assertion used to read `[ "$hooks" = "47" ]`, and it
# went red the moment PR #1003 added one hook — a gate failing on a correct tree, which
# is how a gate gets deleted rather than fixed. The number was never the claim: claim 5
# was about the RULE (depth-1 `*.sh`, EXCLUDING `hooks/tests/**` and `hooks.json`,
# INCLUDING `_`-prefixed helpers, because they ship, execute and can break). The count
# is downstream of the rule and moves every time a hook is added.
#
# So assert the rule's three DISCRIMINATING properties, and cross-check the total against
# an enumeration written HERE in shell — a different implementation from the census's
# Python, so agreement means something rather than comparing the census to itself.
hooks="$(python3 "$ROOT/scripts/inventory-census.py" --json 2>/dev/null \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["counts"]["hook"])' 2>/dev/null)"
paths="$(python3 "$ROOT/scripts/inventory-census.py" --json 2>/dev/null \
  | python3 -c 'import json,sys; print("\n".join(json.load(sys.stdin)["paths"]["hook"]))' 2>/dev/null)"

# Independent enumeration: git-tracked, depth-1 .sh under hooks/, tests/ excluded.
# ⛔ git pathspec `*` is NOT a shell glob -- it matches ACROSS `/`, so the bare pattern
# also sweeps in hooks/tests/ (112 vs 48, measured). The grep is load-bearing, not tidying.
indep="$(cd "$ROOT" && git ls-files 'plugins/ravenclaude-core/hooks/*.sh' 2>/dev/null \
  | grep -v '/tests/' | wc -l | tr -d ' ')"

n_underscore="$(printf '%s\n' "$paths" | grep -c '/_[^/]*\.sh$' || true)"
n_tests="$(printf '%s\n' "$paths" | grep -c '/tests/' || true)"
n_json="$(printf '%s\n' "$paths" | grep -c '\.json$' || true)"

if [ -n "$hooks" ] && [ "$hooks" -gt 0 ] 2>/dev/null && [ "$hooks" = "$indep" ] \
   && [ "$n_underscore" -gt 0 ] && [ "$n_tests" -eq 0 ] && [ "$n_json" -eq 0 ]; then
  ok "claim 5: the RULE holds ($hooks hooks; includes ${n_underscore} _-prefixed, excludes tests/ and .json), and an independent enumeration agrees"
else
  bad "claim 5 rule" "census=$hooks independent=$indep _-prefixed=$n_underscore tests=$n_tests json=$n_json"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
