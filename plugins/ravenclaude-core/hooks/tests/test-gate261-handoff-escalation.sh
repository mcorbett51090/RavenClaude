#!/usr/bin/env bash
# Gate 261 — precompact-handoff-convergence P7.
#
# Covers P3 (skills/session-handoff/SKILL.md): the two retracted strings are
# absent (with a positive control that another known-unmodified string still
# matches), the two replacement texts are present with their required
# qualifiers, step 5.5 is present as a CONDITIONAL gating the former
# unconditional step-6 spawn, and the literal probe `git status --porcelain`
# is present in step 5.5. One must-fail half.
#
# ⛔ HONEST LIMIT (state this verbatim in spirit, per plan.md): this pins
# TEXT, not behaviour — no hook sees whether the agent actually stops or
# runs the probe. It is a drift guard, not a behavioral proof. Compare with
# Gate 260, which drives the real engines end-to-end; this gate cannot,
# because SKILL.md is read by a model, not executed by an interpreter.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$HERE/../skills/session-handoff/SKILL.md"
mode="${1:-normal}"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

RETRACTED_1="- **Never a PreCompact persist hook.** Compaction is append-only."
RETRACTED_2="- Touching \`hooks/compact-anchor.sh\` or \`scripts/compact-anchor.py\`."
POSITIVE_CONTROL="Same \`task-id\`."
REPLACEMENT_1_QUALIFIER="archival"
REPLACEMENT_1_ACK="This repo does ship a PreCompact hook"
REPLACEMENT_2_QUALIFIER="already shipped"
STEP55_CONDITIONAL="Only if one of the three escalation cases from step 5.5 holds"
STEP55_PROBE="git status --porcelain"

_count() {
  # file needle -> occurrence count (fixed-string match, no regex surprises)
  python3 -c '
import sys
text = open(sys.argv[1], encoding="utf-8").read()
print(text.count(sys.argv[2]))
' "$1" "$2"
}

_assert_zero() {
  local label="$1" n="$2"
  if [ "$n" -eq 0 ]; then
    printf '  ok   %s (count=0)\n' "$label"
  else
    printf '  FAIL %s (expected 0, got %s)\n' "$label" "$n"
    fails=$((fails + 1))
  fi
}

_assert_nonzero() {
  local label="$1" n="$2"
  if [ "$n" -ge 1 ]; then
    printf '  ok   %s (count=%s)\n' "$label" "$n"
  else
    printf '  FAIL %s (expected >=1, got 0)\n' "$label" "$n"
    fails=$((fails + 1))
  fi
}

# --------------------------------------------------------------------------
# Build the mutant: reintroduce both retracted strings and de-conditionalize
# step 6 (removing step 5.5 entirely). One must-fail half; several assertions
# are expected to flip together, and that is observed below, not assumed.
# --------------------------------------------------------------------------
_build_mutant() {
  local dest="$1"
  python3 - "$SKILL" "$dest" <<'PY'
from pathlib import Path
import sys

src_path, dest_path = sys.argv[1], sys.argv[2]
text = Path(src_path).read_text(encoding="utf-8")

# 1) revert the Contradiction-1 fix (the whole corrected paragraph -> the
#    single retracted line it replaced).
old_1 = (
    "- **Never a PreCompact *persist* hook** — one that tries to carry the model's live plan *through*\n"
    "  compaction. That is the v0.244.1 retraction and it stands: compaction appends, so there is nothing\n"
    "  to rescue. ⛔ **This repo does ship a PreCompact hook, and it is a different thing:**\n"
    "  `hooks/precompact-digest.sh` is **archival** — it writes a file to disk before the compaction\n"
    "  boundary and makes **no** claim that anything survives compaction. Its own first line says so\n"
    "  (`# precompact-digest.sh — PreCompact hook (archival only).`). It is also **opt-in**, gated on\n"
    "  `cheap_lane.mode`, and it is **not** the mechanism this skill relies on: the durable brief is\n"
    "  written by the *live agent* via `context-handoff.py write`, in a turn, with real judgment content —\n"
    "  which is precisely what an archival extractor cannot produce."
)
new_1 = "- **Never a PreCompact persist hook.** Compaction is append-only."
if old_1 not in text:
    raise SystemExit("SKILL.md drifted -- update Gate 261 mutant (contradiction-1 block not found)")
text = text.replace(old_1, new_1, 1)

# 2) revert the Contradiction-2 fix.
old_2 = (
    "- Re-designing `compact-anchor`'s **transcript-pointer contract** or its session-id matching (the\n"
    "  triple-synced writer/reader agreement at `hooks/precompact-digest.sh:127-131` vs\n"
    "  `scripts/compact-anchor.py:66-67,154-163`) or its silent-degrade-on-no-digest behaviour\n"
    "  (`compact-anchor.py:210-214`). ⛔ Do **not** read this line as \"compact-anchor is frozen\": its\n"
    "  **digest-pointer** extension (`compact-anchor.py:166-185`, v0.309.0) already shipped."
)
new_2 = "- Touching `hooks/compact-anchor.sh` or `scripts/compact-anchor.py`."
if old_2 not in text:
    raise SystemExit("SKILL.md drifted -- update Gate 261 mutant (contradiction-2 block not found)")
text = text.replace(old_2, new_2, 1)

# 3) de-conditionalize step 6: strip step 5.5 entirely (the escalation gate)
#    and revert step 6's opening clause to the OLD unconditional spawn.
start_marker = "5.5 **Evaluate the three escalation conditions"
end_marker = "6. **Only if one of the three escalation cases from step 5.5 holds**, spawn:"
start_idx = text.find(start_marker)
end_idx = text.find(end_marker)
if start_idx == -1 or end_idx == -1:
    raise SystemExit("SKILL.md drifted -- update Gate 261 mutant (step 5.5/6 markers not found)")
old_new6_prefix = "6. **Only if one of the three escalation cases from step 5.5 holds**, spawn:"
new_new6_prefix = "6. spawn:"
tail = text[end_idx:].replace(old_new6_prefix, new_new6_prefix, 1)
text = text[:start_idx] + tail

Path(dest_path).write_text(text, encoding="utf-8")
PY
}

if [ "$mode" = "--must-fail" ]; then
  mutant="$T/SKILL-mutant.md"
  _build_mutant "$mutant"

  r1="$(_count "$mutant" "$RETRACTED_1")"
  r2="$(_count "$mutant" "$RETRACTED_2")"
  pc="$(_count "$mutant" "$POSITIVE_CONTROL")"
  cond="$(_count "$mutant" "$STEP55_CONDITIONAL")"
  probe="$(_count "$mutant" "$STEP55_PROBE")"

  mfails=0
  if [ "$r1" -ge 1 ]; then
    echo "  ok (mutant)  retracted string 1 IS present again (count=$r1)"
  else
    echo "  TEETH GAP: retracted string 1 still absent in the mutant"
    mfails=$((mfails + 1))
  fi
  if [ "$r2" -ge 1 ]; then
    echo "  ok (mutant)  retracted string 2 IS present again (count=$r2)"
  else
    echo "  TEETH GAP: retracted string 2 still absent in the mutant"
    mfails=$((mfails + 1))
  fi
  if [ "$cond" -eq 0 ]; then
    echo "  ok (mutant)  step 5.5's conditional gate on step 6 is GONE (count=$cond)"
  else
    echo "  TEETH GAP: the conditional gate text is still present in the mutant"
    mfails=$((mfails + 1))
  fi
  if [ "$probe" -eq 0 ]; then
    echo "  ok (mutant)  the git status --porcelain probe is GONE with step 5.5 removed (count=$probe)"
  else
    echo "  TEETH GAP: the probe text is still present in the mutant"
    mfails=$((mfails + 1))
  fi
  # The positive control must NOT have been touched by this mutation -- a
  # mutant that also destroys the positive control would be a false tooth
  # (MED-6: a must-fail half that goes green/red for the wrong reason).
  if [ "$pc" -ge 1 ]; then
    echo "  ok (mutant)  positive control (\"$POSITIVE_CONTROL\") is UNTOUCHED (count=$pc) -- the mutation is scoped, not a wholesale file wipe"
  else
    echo "  TEETH GAP: the positive control was destroyed by the mutation too -- this is not a scoped teeth check"
    mfails=$((mfails + 1))
  fi

  if [ "$mfails" -eq 0 ]; then
    echo "mutant correctly reddens the retracted-strings-absent, step-5.5-conditional, and probe-present assertions -- teeth ok"
    exit 1
  else
    echo "TEETH FAILED: $mfails expectation(s) about the mutant did not hold"
    exit 0
  fi
fi

# ==========================================================================
# Normal run — positive-path assertions against the REAL SKILL.md.
# ==========================================================================

echo "── Retracted strings absent (with a positive control) ──"
r1="$(_count "$SKILL" "$RETRACTED_1")"
_assert_zero "retracted string 1 (\"Never a PreCompact persist hook. Compaction is append-only.\") is absent" "$r1"
r2="$(_count "$SKILL" "$RETRACTED_2")"
_assert_zero "retracted string 2 (the compact-anchor.sh/.py out-of-scope bullet) is absent" "$r2"
pc="$(_count "$SKILL" "$POSITIVE_CONTROL")"
_assert_nonzero "positive control: a known-unmodified string (\"$POSITIVE_CONTROL\") still matches" "$pc"

echo "── Replacement texts present, with their required qualifiers ──"
q1="$(_count "$SKILL" "$REPLACEMENT_1_QUALIFIER")"
_assert_nonzero "replacement 1 contains its qualifier (\"$REPLACEMENT_1_QUALIFIER\")" "$q1"
ack1="$(_count "$SKILL" "$REPLACEMENT_1_ACK")"
_assert_nonzero "replacement 1 explicitly acknowledges a PreCompact hook IS shipped" "$ack1"
q2="$(_count "$SKILL" "$REPLACEMENT_2_QUALIFIER")"
_assert_nonzero "replacement 2 contains its qualifier (\"$REPLACEMENT_2_QUALIFIER\")" "$q2"

echo "── Step 5.5 present as a conditional gating the former step-6 spawn ──"
cond="$(_count "$SKILL" "$STEP55_CONDITIONAL")"
if [ "$cond" -eq 1 ]; then
  printf '  ok   step 6 is gated by step 5.5''s conditional (exactly 1 occurrence)\n'
else
  printf '  FAIL %s (got %s, expected 1)\n' "step 6's conditional-gate text" "$cond"
  fails=$((fails + 1))
fi
probe="$(_count "$SKILL" "$STEP55_PROBE")"
if [ "$probe" -eq 1 ]; then
  printf '  ok   literal `git status --porcelain` probe is present in step 5.5 (exactly 1 occurrence)\n'
else
  printf '  FAIL %s (got %s, expected 1)\n' "the git status --porcelain probe" "$probe"
  fails=$((fails + 1))
fi
# Ordering sanity: step 5.5's block must appear BEFORE step 6's spawn line
# in the file -- "gating" only means something if the gate precedes the
# gated action.
order="$(python3 -c '
import sys
text = open(sys.argv[1], encoding="utf-8").read()
i55 = text.find("5.5 **Evaluate the three escalation conditions")
i6 = text.find("Only if one of the three escalation cases from step 5.5 holds")
print("ok" if (i55 != -1 and i6 != -1 and i55 < i6) else "bad")
' "$SKILL")"
if [ "$order" = "ok" ]; then
  printf '  ok   step 5.5 textually precedes the gated step 6 spawn line\n'
else
  printf '  FAIL %s\n' "step 5.5 does not precede step 6 in the file"
  fails=$((fails + 1))
fi

if [ "$fails" -eq 0 ]; then
  echo "Gate 261 PASS"
  exit 0
fi
echo "Gate 261 FAIL ($fails)"
exit 1
