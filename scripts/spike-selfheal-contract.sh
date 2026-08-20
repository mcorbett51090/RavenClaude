#!/usr/bin/env bash
#
# spike-selfheal-contract.sh — P1 / S3, and the standing regression for P2.
#
# ⛔ WHAT IS BEING MEASURED. regenerate-artifacts.yml decides whether a failing
# `concepts.py --check` is survivable by grepping the check output for a LITERAL
# SENTENCE. On a match it warns and continues; on NO match it runs exit "$_crc",
# which kills every later self-heal step — concept SVGs, decision-tree SVGs,
# dashboard.html, index.html, BI reports, the Copilot package, the feedback
# report. The workflow comment at that site records the incident this re-arms:
# main left UN-HEALED across many merges.
#
# The plan derived that from READING. This measures it: the workflow conditional
# is EXTRACTED FROM THE WORKFLOW FILE and replayed against each output class, so
# the probe cannot drift away from the thing it claims to measure. Rewording the
# workflow changes this probe result; rewording this probe does not.
#
# ⛔ NO APOSTROPHES. See spike-tprose-canary.sh for why.
#
# Usage:
#   spike-selfheal-contract.sh              # report the contract, exit 0
#   spike-selfheal-contract.sh --check      # gate: every class must be survivable
#   spike-selfheal-contract.sh --must-fail  # teeth: a class the grep misses must
#                                           # be reported FATAL, or this probe is
#                                           # blind. Declared teeth exit: 0.
#   spike-selfheal-contract.sh --must-fail-convention
#
# ⛔ THE TEETH-BIT EXIT IS 0, NOT 2. Measured divergence in this repo:
# premise-gate.py uses exit 0 as its teeth bit, sync-plugin-versions.py uses 2.
# A shared assumption is wrong by construction, so the convention is DECLARED.

set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
WF="$HERE/.github/workflows/regenerate-artifacts.yml"

if [ "${1:-}" = "--must-fail-convention" ]; then
  printf 'must-fail-teeth-exit: 0\n'
  exit 0
fi

[ -f "$WF" ] || { echo "spike-selfheal-contract: workflow absent at $WF" >&2; exit 2; }

# ── Extract the SURVIVABILITY PATTERNS the workflow actually greps for. ──────
# Read out of the workflow rather than restated here, so the probe measures the
# shipped contract. Any `grep -q '<pat>'` inside the concepts self-heal step.
_patterns() {
  awk '
    /concepts\.json stale — regenerating/ {inblock=1}
    inblock && /grep -q/ {
      line=$0
      while (match(line, /grep -q[^\047]*\047[^\047]+\047/)) {
        seg=substr(line, RSTART, RLENGTH)
        if (match(seg, /\047[^\047]+\047/)) print substr(seg, RSTART+1, RLENGTH-2)
        line=substr(line, RSTART+RLENGTH)
      }
    }
    inblock && /^ *# 2\./ {inblock=0}
  ' "$WF"
}

# ⛔ bash 3.2 (the macOS system bash) has no mapfile, and under `set -u` an empty
# array expansion is itself an error. Both are load-bearing: the first version of
# this probe crashed on mapfile and exited 1, which the caller read as "the defect
# is present" — a manufactured verdict. Portable read loop + an explicit count.
PATS=()
while IFS= read -r _p; do
  [ -n "$_p" ] && PATS[${#PATS[@]}]="$_p"
done < <(_patterns)
NPAT=${#PATS[@]}

# ── The output classes `concepts.py --check` can emit. ──────────────────────
# Taken from the printed strings in scripts/concepts.py, plus the classes this
# plan ADDS. survivable=1 means a human must act and the self-heal must continue;
# fatal=0 means a real generator failure that SHOULD abort.
#            id                       | must-survive | representative first line
CLASSES=(
  "platform-fact-staleness|1|Concept staleness gate FAILED — refresh last_verified after re-checking the source:"
  "schema-validation|0|Concept schema validation FAILED:"
  "registry-missing|0|concepts.json missing at plugins/ravenclaude-core/concepts.json — run: scripts/concepts.py"
  "registry-stale|0|concepts.json is STALE — regenerate with: scripts/concepts.py"
  "covers-digest-drift|1|covers_digest is STALE for 3 entr(ies) — a covered artifact changed after the entry was stamped"
  "inventory-staleness|1|Inventory staleness gate FAILED — last_verified is ABSENT on 2 entr(ies)"
)

_survives() { # text -> 0 if a survivability pattern matches
  local text="$1" i=0
  while [ "$i" -lt "$NPAT" ]; do
    printf '%s' "$text" | grep -q "${PATS[$i]}" && return 0
    i=$((i+1))
  done
  return 1
}

MODE="${1:-}"
rc=0
FATALS=""
NFATAL=0

echo "── P1/S3: post-merge self-heal contract ──"
echo "  workflow : .github/workflows/regenerate-artifacts.yml"
if [ "$NPAT" -eq 0 ]; then
  printf '  greps    : <none extracted — probe is blind>\n'
else
  printf '  greps    : %s\n' "${PATS[*]}"
fi
if [ "$NPAT" -eq 0 ]; then
  echo "  ✗ extracted zero survivability patterns. A probe that finds nothing is not"
  echo "    evidence of nothing: this is a broken extractor, not a clean contract."
  exit 2
fi
echo

printf '  %-24s  %-12s  %s\n' "FAILURE CLASS" "MUST-SURVIVE" "MEASURED"
for row in "${CLASSES[@]}"; do
  IFS='|' read -r id want text <<< "$row"
  if _survives "$text"; then got="CONTINUE"; else got="FATAL — self-heal aborts"; fi
  printf '  %-24s  %-12s  %s\n' "$id" "$([ "$want" = 1 ] && echo yes || echo no)" "$got"
  if [ "$want" = "1" ] && [ "$got" != "CONTINUE" ]; then
    FATALS="$FATALS $id"; NFATAL=$((NFATAL+1)); rc=1
  fi
done
echo

if [ "$NFATAL" -gt 0 ]; then
  echo "  ⛔ $NFATAL content-freshness class(es) abort the self-heal:$FATALS"
  echo "     Each one reproduces the recorded incident: main carries a stale dashboard,"
  echo "     index, SVGs and BI reports across every later merge, behind a green run."
fi

case "$MODE" in
  --must-fail)
    # TEETH. A class the grep provably misses MUST be reported FATAL. If this
    # probe reports every class survivable, it is not measuring the grep at all.
    if _survives "covers_digest is STALE for 3 entr(ies) — a covered artifact changed"; then
      echo "  ✗ must-fail: a class outside the grep was reported survivable — probe is blind."
      exit 1
    fi
    echo "  ✓ must-fail: a class outside the grep is correctly reported FATAL."
    exit 0
    ;;
  --check)
    [ "$rc" -eq 0 ] && echo "  ✓ every content-freshness class survives the self-heal."
    exit "$rc"
    ;;
  *)
    exit 0
    ;;
esac
