#!/usr/bin/env bash
#
# spike-selfheal-contract.sh — P1 / S3, and the standing regression for P2.
#
# ⛔ WHAT IS BEING MEASURED — BOTH HALVES OF ONE CONTRACT.
#
#   half A: `concepts.py --check` must EMIT a stable class marker for each
#           failure class (RC-CONCEPTS-CLASS: human-reverify-required for
#           anything regeneration cannot fix; generator-failure otherwise).
#   half B: `regenerate-artifacts.yml` must ACCEPT that marker as survivable.
#
# Measuring only half B is how the first version of this probe reported a false
# clean: the workflow grep was correct while the emitter said nothing. Both ends
# are therefore READ FROM THEIR OWN SOURCE FILE — the marker constants out of
# concepts.py, the grep patterns out of the workflow — so rewording either end
# changes this result, and rewording this probe does not.
#
# Why it matters: on no match the workflow runs exit "$_crc", killing every later
# self-heal step — concept SVGs, decision-tree SVGs, dashboard.html, index.html,
# BI reports, the Copilot package, the feedback report. The workflow comment at
# that site records the incident it re-arms: main left UN-HEALED across many
# merges.
#
# ⛔ NO APOSTROPHES. ⛔ The scratch dir is cleaned with a helper, not an inline
# recursive delete — guard-destructive matches the command text in the FILE.
# Both notes are recorded at the head of spike-tprose-canary.sh.
#
# Usage:
#   spike-selfheal-contract.sh              # report
#   spike-selfheal-contract.sh --check      # gate: every content class survives
#   spike-selfheal-contract.sh --must-fail  # teeth. Declared teeth exit: 0.
#   spike-selfheal-contract.sh --must-fail-convention
#
# ⛔ THE TEETH-BIT EXIT IS 0, NOT 2. premise-gate.py uses 0, sync-plugin-versions.py
# uses 2. A shared assumption is wrong by construction, so it is DECLARED.

set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
WF="$HERE/.github/workflows/regenerate-artifacts.yml"
CP="$HERE/scripts/concepts.py"

if [ "${1:-}" = "--must-fail-convention" ]; then
  printf 'must-fail-teeth-exit: 0\n'
  exit 0
fi

[ -f "$WF" ] || { echo "spike-selfheal-contract: workflow absent at $WF" >&2; exit 2; }
[ -f "$CP" ] || { echo "spike-selfheal-contract: concepts.py absent at $CP" >&2; exit 2; }

# ── HALF A. The marker constants, read out of concepts.py. ──────────────────
_const() { # python const name -> its string literal value
  sed -n "s/^$1 *= *\"\([^\"]*\)\".*/\1/p" "$CP" | head -1
}
MARKER="$(_const MARKER)"
CLASS_HUMAN="$(_const CLASS_HUMAN)"
CLASS_GENERATOR="$(_const CLASS_GENERATOR)"

if [ -z "$MARKER" ] || [ -z "$CLASS_HUMAN" ] || [ -z "$CLASS_GENERATOR" ]; then
  echo "  ✗ could not read the class constants out of scripts/concepts.py."
  echo "    That is a broken extractor, not a clean contract. Refusing to report."
  exit 2
fi

# ── HALF B. Every pattern the workflow greps for, including each -e term. ────
# ⛔ The first version missed the SECOND -e term because it matched `grep -q`
# once per line. Scan for every single-quoted literal on a grep -q line instead.
_patterns() {
  awk '
    /concepts\.json stale — regenerating/ {inblock=1}
    inblock && /grep -q/ {
      # ⛔ Scan only the text AFTER `grep -q`. Scanning the whole line also
      # harvested the format string out of the printf that FEEDS the grep, so
      # "%s" was registered as a survivability pattern — a pattern that matches
      # nothing real, but one more term nobody put there.
      line=$0
      gi=index(line, "grep -q")
      if (gi == 0) next
      line=substr(line, gi + 7)
      while (match(line, /\047[^\047]+\047/)) {
        print substr(line, RSTART+1, RLENGTH-2)
        line=substr(line, RSTART+RLENGTH)
      }
    }
    inblock && /^ *# 2\./ {inblock=0}
  ' "$WF"
}

PATS=()
while IFS= read -r _p; do
  [ -n "$_p" ] && PATS[${#PATS[@]}]="$_p"
done < <(_patterns)
NPAT=${#PATS[@]}

# ── The failure classes, and which marker concepts.py emits for each. ────────
# must-survive=1 means a human must act and the self-heal MUST continue.
#      id                     | must-survive | class-const | human-readable first line
CLASSES=(
  "platform-fact-staleness|1|HUMAN|Concept staleness gate FAILED — refresh last_verified after re-checking the source:"
  "inventory-staleness|1|HUMAN|  ✗ x: last_verified is ABSENT — unverified is not fresh"
  "covers-digest-drift|1|HUMAN|  ✗ x: covers_digest drift — a covered artifact changed after the entry was stamped"
  "schema-validation|0|GENERATOR|Concept schema validation FAILED:"
  "registry-missing|0|GENERATOR|  ✗ concepts.json missing — run: scripts/concepts.py"
  "registry-stale|0|GENERATOR|  ✗ concepts.json is STALE — regenerate with: scripts/concepts.py"
)

_survives() { # full multi-line output -> 0 if a survivability pattern matches
  local text="$1" i=0
  while [ "$i" -lt "$NPAT" ]; do
    printf '%s' "$text" | grep -q "${PATS[$i]}" && return 0
    i=$((i+1))
  done
  return 1
}

_output_for() { # human-line class-const -> the full shape concepts.py emits
  local human="$1" cls="$2" val
  case "$cls" in
    HUMAN) val="$CLASS_HUMAN" ;;
    *)     val="$CLASS_GENERATOR" ;;
  esac
  printf '%s\n%s%s\n' "$human" "$MARKER" "$val"
}

MODE="${1:-}"
rc=0
FATALS=""
NFATAL=0
LEAKS=""
NLEAK=0

echo "── S3: post-merge self-heal contract (both halves) ──"
echo "  emitter  : scripts/concepts.py"
printf '  marker   : %s{%s|%s}\n' "$MARKER" "$CLASS_HUMAN" "$CLASS_GENERATOR"
echo "  consumer : .github/workflows/regenerate-artifacts.yml"
if [ "$NPAT" -eq 0 ]; then
  echo "  ✗ extracted zero survivability patterns. A probe that finds nothing is not"
  echo "    evidence of nothing: this is a broken extractor, not a clean contract."
  exit 2
fi
printf '  greps    : %s\n' "${PATS[*]}"
echo

printf '  %-24s  %-12s  %s\n' "FAILURE CLASS" "MUST-SURVIVE" "MEASURED"
for row in "${CLASSES[@]}"; do
  IFS='|' read -r id want cls human <<< "$row"
  text="$(_output_for "$human" "$cls")"
  if _survives "$text"; then got="CONTINUE"; else got="FATAL — self-heal aborts"; fi
  printf '  %-24s  %-12s  %s\n' "$id" "$([ "$want" = 1 ] && echo yes || echo no)" "$got"
  if [ "$want" = "1" ] && [ "$got" != "CONTINUE" ]; then
    FATALS="$FATALS $id"; NFATAL=$((NFATAL+1)); rc=1
  fi
  # ⛔ THE OTHER DIRECTION. A generator failure that the grep treats as
  # survivable is just as wrong: the self-heal would continue past a broken
  # generator and commit whatever half-built artifacts it produced.
  if [ "$want" = "0" ] && [ "$got" = "CONTINUE" ]; then
    LEAKS="$LEAKS $id"; NLEAK=$((NLEAK+1)); rc=1
  fi
done
echo

if [ "$NFATAL" -gt 0 ]; then
  echo "  ⛔ $NFATAL content-freshness class(es) abort the self-heal:$FATALS"
  echo "     Each reproduces the recorded incident: main carries a stale dashboard,"
  echo "     index, SVGs and BI reports across every later merge, behind a green run."
fi
if [ "$NLEAK" -gt 0 ]; then
  echo "  ⛔ $NLEAK generator-failure class(es) are treated as survivable:$LEAKS"
  echo "     The self-heal would continue past a broken generator."
fi

case "$MODE" in
  --must-fail)
    # TEETH, both directions.
    # 1. An output carrying NO marker at all must be reported FATAL. This is the
    #    pre-fix world, and the thing the marker exists to end.
    if _survives "some new failure nobody taught the workflow about"; then
      echo "  ✗ must-fail: an unmarked output was reported survivable — probe is blind."
      exit 1
    fi
    # 2. The generator marker must NOT be survivable. If it were, the two classes
    #    would be indistinguishable and the marker would buy nothing.
    if _survives "$(_output_for 'x' GENERATOR)"; then
      echo "  ✗ must-fail: the generator-failure marker was reported survivable —"
      echo "    the two classes are not actually separated."
      exit 1
    fi
    # 3. Positive control: the human marker MUST be survivable, or checks 1 and 2
    #    would pass for a probe whose grep matches nothing at all.
    if ! _survives "$(_output_for 'x' HUMAN)"; then
      echo "  ✗ must-fail: the human-reverify marker was NOT survivable. The two"
      echo "    negatives above are therefore vacuous — this probe matches nothing."
      exit 1
    fi
    echo "  ✓ must-fail: unmarked and generator outputs are FATAL, the human marker"
    echo "    is survivable (positive control). Teeth exit 0 declared."
    exit 0
    ;;
  --check)
    [ "$rc" -eq 0 ] && echo "  ✓ every content-freshness class survives the self-heal, and every"
    [ "$rc" -eq 0 ] && echo "    generator failure still aborts it."
    exit "$rc"
    ;;
  *)
    exit 0
    ;;
esac
