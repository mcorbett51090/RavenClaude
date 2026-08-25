#!/usr/bin/env bash
# Gate 224 — the two assumption layers.
#
#   LAYER 1  claim-grounding-lint.sh check 3 (inference-as-observation): a CAUSAL
#            claim about an outcome, written into a knowledge/ or docs/ markdown
#            file with no cited this-session check, emits a nudge.
#   LAYER 2  scripts/ask-on-ambiguity.sh: an under-specified prompt SHAPE emits an
#            advisory additionalContext and never blocks or persists anything.
#
# Bidirectional by construction — a fires-on-bad half alone would pass for a hook
# that fires on everything, which is the failure mode both layers are tuned
# against (the first cut of check 3 fired on 38% of the live tree).
#   A  fires-on-bad
#   B  silent-on-good, INCLUDING a doc that DESCRIBES the anti-pattern. This repo
#      has a documented, recurring failure where a source-scan gate flags the
#      prose explaining the very pattern it hunts (nine such blocks in one
#      session), and a doc teaching observation-vs-inference must write causal
#      example sentences. B2/B3 are that case, asserted explicitly.
#   C  teeth (must-fail): a mutant with the suppressions neutered MUST flag the
#      describing-doc, and a mutant with the referent conjunct neutered MUST fire
#      on a well-specified prompt. Without these, "it stayed silent" is not
#      evidence the suppression did anything.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOKS="$(cd "$HERE/.." && pwd)"
SCRIPTS="$(cd "$HERE/../../scripts" && pwd)"
LINT="$HOOKS/claim-grounding-lint.sh"
AMB="$SCRIPTS/ask-on-ambiguity.sh"

fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

for f in "$LINT" "$AMB"; do
  [ -f "$f" ] || {
    echo "Gate 224 FAIL — missing $f"
    exit 1
  }
done

TMP="$(mktemp -d)"
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude" "$PROJ/knowledge" "$PROJ/src"
printf 'schema_version: 5\n' >"$PROJ/.ravenclaude/comfort-posture.yaml"
KN="$PROJ/knowledge"

# ── Layer 1 helpers ──────────────────────────────────────────────────────────
# Capture stderr into a variable first: piping into `grep -q` lets grep close the
# pipe early (SIGPIPE), which under pipefail misreports a real fire as a miss.
lint_fires() { # $1=hook $2=file
  local out
  out="$("$1" "$2" 2>&1 1>/dev/null)"
  printf '%s' "$out" | grep -q "Inference-as-observation nudge"
}

echo "── Layer 1: inference-as-observation (claim-grounding-lint.sh check 3) ──"

# A1 — the incident's own sentence. Attribution, no cited check.
printf '# Triage\n\nThe build failure is caused by my change to the parser.\n' >"$KN/a1.md"
lint_fires "$LINT" "$KN/a1.md" &&
  pass "A1: uncited causal attribution fires" ||
  fail "A1: uncited causal attribution did NOT fire"

# A2 — a conclusion connective drawing a cause for an outcome.
printf '# Triage\n\nThe deploy went red, therefore the migration is at fault.\n' >"$KN/a2.md"
lint_fires "$LINT" "$KN/a2.md" &&
  pass "A2: uncited conclusion-connective causal claim fires" ||
  fail "A2: uncited conclusion-connective claim did NOT fire"

# B1 — the SAME claim with a this-session check cited inline -> grounded.
printf '# Triage\n\nThe build failure is caused by my change: reverting it -> 703 pass, 0 fail.\n' >"$KN/b1.md"
lint_fires "$LINT" "$KN/b1.md" &&
  fail "B1: a claim citing its this-session check should be silent" ||
  pass "B1: cited this-session check suppresses"

# B2 — a doc DESCRIBING the anti-pattern. The load-bearing false-positive case.
cat >"$KN/b2.md" <<'MD'
# Observation vs inference

An inference is not an observation. For example, "the build failure is caused by
my change" is the anti-pattern: it reads as a measurement and is not one.

Counter-example: the deploy went red, therefore the migration is at fault.
MD
lint_fires "$LINT" "$KN/b2.md" &&
  fail "B2: a doc DESCRIBING the anti-pattern must NOT be flagged" ||
  pass "B2: doc describing the anti-pattern is not flagged"

# B3 — the same specimens quoted / fenced / blockquoted / headed.
cat >"$KN/b3.md" <<'MD'
# Notes

## The build failure is caused by my change

> The build failure is caused by my change to the parser.

```text
The build failure is caused by my change to the parser.
```
MD
lint_fires "$LINT" "$KN/b3.md" &&
  fail "B3: heading/blockquote/fence specimens must NOT be flagged" ||
  pass "B3: heading, blockquote and fenced specimens are skipped"

# B4 — the inline line escape.
printf '# Triage\n\nThe failure is caused by my change to the parser. <!-- claim-lint-ok -->\n' >"$KN/b4.md"
lint_fires "$LINT" "$KN/b4.md" &&
  fail "B4: claim-lint-ok must suppress" ||
  pass "B4: claim-lint-ok line escape suppresses"

# B5 — prescriptive: a conclusion connective deriving an ACTION, not a cause.
printf '# Plan\n\nP8 must therefore rebase onto post-#959 main before the red gate is fixed.\n' >"$KN/b5.md"
lint_fires "$LINT" "$KN/b5.md" &&
  fail "B5: a prescriptive 'must therefore' should be silent" ||
  pass "B5: prescriptive conclusion is not a diagnosis"

# B6 — out of scope (not knowledge/ or docs/).
printf 'The build failure is caused by my change to the parser.\n' >"$PROJ/src/notes.md"
lint_fires "$LINT" "$PROJ/src/notes.md" &&
  fail "B6: a non-knowledge/docs file should be a no-op" ||
  pass "B6: non-knowledge/docs file is a no-op"

# B7 — opt-in: no comfort-posture -> no-op.
NOP="$TMP/noposture/knowledge"
mkdir -p "$NOP"
printf '# x\n\nThe build failure is caused by my change to the parser.\n' >"$NOP/x.md"
lint_fires "$LINT" "$NOP/x.md" &&
  fail "B7: no comfort-posture should be a no-op" ||
  pass "B7: opt-in — no comfort-posture is a no-op"

# B8 — checks 1 and 2 are undisturbed (the regression the dry run measured).
printf "# x\n\nYou can't export the solution as unmanaged.\n" >"$KN/b8.md"
out8="$("$LINT" "$KN/b8.md" 2>&1 1>/dev/null)"
printf '%s' "$out8" | grep -q "unhedged absolute" &&
  pass "B8: check 1 still fires (check 3 did not displace it)" ||
  fail "B8: check 1 regressed — adding check 3 broke it"

# C1 — teeth: neuter check 3's three suppressions by pointing each grep at a
# pattern that cannot match. The describing-doc (B2) must then flag. Without this,
# B2's silence is equally consistent with a check 3 that never runs at all.
MUT1="$TMP/mut-lint.sh"
sed -e 's/grep -qiE "\$evidence"/grep -qiE "zzzNEVERMATCHzzz"/' \
  -e 's/grep -qiE "\$meta"/grep -qiE "zzzNEVERMATCHzzz"/' \
  -e 's/grep -qiE "\$prescriptive"/grep -qiE "zzzNEVERMATCHzzz"/' \
  "$LINT" >"$MUT1"
mutcount="$(grep -c 'zzzNEVERMATCHzzz' "$MUT1" 2>/dev/null || echo 0)"
if [ "$mutcount" -lt 3 ]; then
  fail "C1: could not neuter the suppressions (sed matched $mutcount/3 — fixture stale)"
else
  # The mutant lives in $TMP, so its `../scripts` fallback cannot find the
  # classifier — point CLAUDE_PLUGIN_ROOT at the real plugin or the mutant
  # degrades to check 3's fail-safe silence and the teeth would pass for the
  # wrong reason (this cost a red run to find).
  mutout="$(CLAUDE_PLUGIN_ROOT="$(dirname "$HOOKS")" bash "$MUT1" "$KN/b2.md" 2>&1 1>/dev/null)"
  if printf '%s' "$mutout" | grep -q "Inference-as-observation nudge"; then
    pass "C1: must-fail — neutered suppressions DO flag the describing-doc (they are load-bearing)"
  else
    fail "C1: must-fail — neutered hook stayed silent; B2's silence proves nothing"
  fi
fi

echo ""
echo "── Layer 2: ask-on-ambiguity (UserPromptSubmit, advisory) ──"

APROJ="$TMP/aproj"
mkdir -p "$APROJ/.ravenclaude"
printf 'schema_version: 5\n' >"$APROJ/.ravenclaude/comfort-posture.yaml"

amb() { # $1=script $2=prompt [$3=project dir] ; echoes stdout
  local proj="${3:-$APROJ}"
  printf '{"prompt":%s,"session_id":"gate223"}' "$(printf '%s' "$2" | jq -Rs .)" |
    CLAUDE_PROJECT_DIR="$proj" bash "$1" 2>/dev/null
}

if ! command -v jq >/dev/null 2>&1; then
  echo "  ! jq absent — Layer 2 subtests SKIPPED (this is NOT a pass)"
  fails=$((fails + 1))
else
  # A3 — under-specified shape fires.
  o="$(amb "$AMB" "fix it")"
  [ -n "$o" ] && pass "A3: 'fix it' emits the ambiguity nudge" || fail "A3: 'fix it' emitted nothing"

  o="$(amb "$AMB" "clean up everything")"
  [ -n "$o" ] && pass "A4: 'clean up everything' emits the nudge" || fail "A4: emitted nothing"

  # B9 — a well-anchored short prompt stays silent (the precision conjunct).
  o="$(amb "$AMB" "refactor the auth module")"
  [ -z "$o" ] && pass "B9: named object -> silent" || fail "B9: fired on a named object"

  o="$(amb "$AMB" "update src/app.ts")"
  [ -z "$o" ] && pass "B10: path anchor -> silent" || fail "B10: fired on a path-anchored prompt"

  o="$(amb "$AMB" "add a retry to the fetch helper")"
  [ -z "$o" ] && pass "B11: concrete directive -> silent" || fail "B11: fired on a concrete directive"

  # B12 — exit code is ALWAYS 0 (it must never block a prompt).
  printf '{"prompt":"fix it"}' | CLAUDE_PROJECT_DIR="$APROJ" bash "$AMB" >/dev/null 2>&1
  rc=$?
  [ "$rc" -eq 0 ] && pass "B12: exits 0 on the firing path (never blocks)" || fail "B12: exited $rc"
  printf 'garbage-not-json' | CLAUDE_PROJECT_DIR="$APROJ" bash "$AMB" >/dev/null 2>&1
  rc=$?
  [ "$rc" -eq 0 ] && pass "B13: exits 0 on malformed input (fail-safe)" || fail "B13: exited $rc"

  # B14 — opt-out honored.
  OFFP="$TMP/offproj"
  mkdir -p "$OFFP/.ravenclaude"
  printf 'schema_version: 5\nask_on_ambiguity: off\n' >"$OFFP/.ravenclaude/comfort-posture.yaml"
  o="$(printf '{"prompt":"fix it"}' | CLAUDE_PROJECT_DIR="$OFFP" bash "$AMB" 2>/dev/null)"
  [ -z "$o" ] && pass "B14: ask_on_ambiguity: off silences it" || fail "B14: fired despite off"

  # B15 — opt-in: no posture file at all -> no-op.
  BARE="$TMP/bare"
  mkdir -p "$BARE"
  o="$(printf '{"prompt":"fix it"}' | CLAUDE_PROJECT_DIR="$BARE" bash "$AMB" 2>/dev/null)"
  [ -z "$o" ] && pass "B15: no comfort-posture -> no-op" || fail "B15: fired with no posture"

  # B16 — NO-EGRESS. The prompt must reach neither disk nor the emitted context.
  # The sentinel is checked with a POSITIVE CONTROL first: a probe that cannot
  # find the sentinel when it IS present would report "no leak" for free.
  # DIGIT-FREE on purpose: any digit is a concrete anchor, so a sentinel like
  # "GATE223SENTINEL" silences the hook and the leak check passes vacuously.
  # Caught by the setup assertion below, which is why it is there.
  SENT="zqxjsentinelvwk"
  if ! printf 'x %s y' "$SENT" | grep -q "$SENT"; then
    fail "B16: positive control FAILED — the leak probe cannot detect the sentinel"
  else
    ESPROJ="$TMP/esproj"
    mkdir -p "$ESPROJ/.ravenclaude"
    printf 'schema_version: 5\n' >"$ESPROJ/.ravenclaude/comfort-posture.yaml"
    before="$(find "$ESPROJ" -type f | sort)"
    o="$(amb "$AMB" "fix it and clean up $SENT things" "$ESPROJ")"
    [ -n "$o" ] || fail "B16: setup — the sentinel prompt did not fire, so the leak check is vacuous"
    if printf '%s' "$o" | grep -q "$SENT"; then
      fail "B16: EGRESS — the prompt text reached the emitted context"
    else
      pass "B16: no-egress — emitted context carries no prompt text (probe positively controlled)"
    fi
    after="$(find "$ESPROJ" -type f | sort)"
    if [ "$before" = "$after" ] && ! grep -rq "$SENT" "$ESPROJ" 2>/dev/null; then
      pass "B17: no-egress — the hook wrote no file and the prompt never reached disk"
    else
      fail "B17: EGRESS — the hook wrote to disk"
    fi
  fi

  # C2 — teeth: neuter the referent/scope conjunct; a well-specified prompt must
  # then fire. Without this, every B-half silence could be a hook that never runs.
  MUT2="$TMP/mut-amb.sh"
  sed -e 's/^.*grep -Eqi "\$scope"; then$/  false; then/' "$AMB" >"$MUT2"
  if ! grep -q '^  false; then$' "$MUT2"; then
    fail "C2: could not neuter the referent conjunct (sed no-op — fixture stale)"
  else
    o="$(amb "$MUT2" "refactor the auth module")"
    [ -n "$o" ] &&
      pass "C2: must-fail — neutered referent conjunct fires on a named object (the conjunct is load-bearing)" ||
      fail "C2: must-fail — neutered hook still silent; the B-half silences prove nothing"
  fi
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 224 PASS — inference-as-observation fires on uncited causal claims and stays silent on cited/described/escaped/prescriptive/out-of-scope; ask-on-ambiguity fires on the under-specified shape only, never blocks, and never egresses the prompt. Both teeth halves confirmed."
  exit 0
else
  echo "Gate 224 FAIL — $fails subtest(s) failed."
  exit 1
fi
