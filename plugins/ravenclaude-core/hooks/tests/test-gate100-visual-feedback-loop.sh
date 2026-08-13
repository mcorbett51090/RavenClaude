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

# ── P4: design-schema structural floor — offline "declares the same design system?" ──
# (NOT fidelity — a sanity check that the candidate declares the same design system.)
expect "design-schema match (floor pass -> LOUD capture-ssim, exit 0)" 0 "$F/good-config-design-schema-match.json"
expect "design-schema diverge -> fail exit 1"                          1 "$F/bad-config-design-schema-diverge.json"
expect "design-schema missing file -> not_captured exit 0"             0 "$F/design-schema-missing-file.json"
expect "design-schema candidate traversal rejected -> exit 2"          2 "$F/bad-config-design-schema-traversal.json"
# ── P4: ssim visual-fidelity gate — agent-captured browser evidence ──
expect "ssim 0.94 >= tau -> pass exit 0"                               0 "$F/good-config-ssim-pass.json"
expect "ssim 0.40 < tau -> fail exit 1"                                1 "$F/bad-config-ssim-fail.json"
expect "ssim absent -> not_captured exit 0"                            0 "$F/ssim-absent-config.json"
# domain clamp: a page-controllable value out of [0,1] or non-finite is NEVER a pass
expect "ssim out-of-range 5.0 -> error exit 1 (clamp)"                 1 "$F/bad-config-ssim-out-of-range.json"
expect "ssim non-finite 1e999->inf -> error exit 1 (clamp)"           1 "$F/bad-config-ssim-non-finite.json"

# behavioral: the diverge diff must LOCALIZE the divergent dimension (not just "fail").
ds_out="$($D "$F/bad-config-design-schema-diverge.json" 2>/dev/null || true)"
if printf '%s' "$ds_out" | grep -q 'spacing-base-unit'; then
  echo "  ✓ design-schema diff localizes the divergent dimension (spacing-base-unit)"
else
  echo "  ✗ design-schema diff did not name the divergent dimension"
  rc_total=1
fi
# behavioral: LOUD degradation — a structural pass with no ssim must NOT read as a bare ship.
loud_out="$($D "$F/good-config-design-schema-match.json" 2>/dev/null || true)"
if printf '%s' "$loud_out" | grep -q 'capture-ssim-evidence' \
  && printf '%s' "$loud_out" | grep -q 'visual fidelity not verified'; then
  echo "  ✓ LOUD degradation: structural pass + no ssim -> capture-ssim-evidence + fidelity-unverified note"
else
  echo "  ✗ LOUD degradation not emitted on structural-pass-without-ssim"
  rc_total=1
fi

# parity: the delegated linter rejects the same '..' shape (exit 2)
rc=0; $LINT "../../etc/passwd" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 2 ]]; then
  echo "  ✓ path-guard parity (driver + linter both reject '..' → exit 2)"
else
  echo "  ✗ path-guard parity — linter did not reject '..' with exit 2 (got $rc)"
  rc_total=1
fi

# teeth: a mutant that always reports passed=true must make a known-bad pass.
# PORTABILITY (2026-07-15) — TWO separate macOS defects lived in these four lines:
#  1. `mktemp --suffix=` is a GNU long option; BSD/macOS mktemp rejects it outright
#     ("usage: mktemp ..."), so the mutant was never even created.
#  2. The mutant MUST sit in driver.py's OWN directory. driver.py:81 computes repo root as
# "four directories up from __file__" — so the mutant only agrees with the real driver
# at the SAME DEPTH. In $TMPDIR (or even a subdir here) it computes a different root and
# rejects the repo's own fixtures with exit 2. On Linux /tmp/x.py -> 4-up -> '/', which
# contains everything, so this passed by ACCIDENT; macOS's deep $TMPDIR exposed it.
MUT="plugins/ravenclaude-core/skills/visual-feedback-loop/.mut-$$.py"
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
MUTP="plugins/ravenclaude-core/skills/visual-feedback-loop/.mutp-$$.py"
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

# ── P4 teeth: one must-fail mutant per new gate + the NaN clamp case ──────────
# Mutant files sit in driver.py's OWN dir (same repo-root depth — see the note above).
# NaN is invalid JSON (a committed fixture would fail prettier --check), so the NaN
# case is synthesized at runtime under the in-repo fixtures dir (Python's json.load
# accepts NaN). All temp files are cleaned by the trap below (which supersedes the
# earlier trap and still lists MUT/MUTP so they are cleaned too).
MUTDS="plugins/ravenclaude-core/skills/visual-feedback-loop/.mutds-$$.py"
MUTSSIM="plugins/ravenclaude-core/skills/visual-feedback-loop/.mutssim-$$.py"
MUTCLAMP="plugins/ravenclaude-core/skills/visual-feedback-loop/.mutclamp-$$.py"
NANEV="$F/.nan-ssim-$$.json"
NANCFG="$F/.nan-cfg-$$.json"
trap 'rm -f "$MUT" "$MUTP" "$MUTDS" "$MUTSSIM" "$MUTCLAMP" "$NANEV" "$NANCFG"' EXIT

# teeth 1: design-schema gate neutered to always-"pass" lets the diverging fixture through.
sed 's/record\["status"\] = "fail" if diffs else "pass"/record["status"] = "pass"/' \
  plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py >"$MUTDS"
rc=0; python3 "$MUTDS" "$F/bad-config-design-schema-diverge.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant (design-schema always-pass) lets divergent schema through → real fail is the diff"
else
  echo "  ✗ teeth: design-schema mutant did NOT pass the divergent fixture (got $rc) — teeth broken"
  rc_total=1
fi

# teeth 2: ssim gate neutered to always-"pass" lets the below-threshold fixture through.
sed 's/record\["status"\] = "pass" if float(score) >= threshold else "fail"/record["status"] = "pass"/' \
  plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py >"$MUTSSIM"
rc=0; python3 "$MUTSSIM" "$F/bad-config-ssim-fail.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant (ssim always-pass) lets 0.40 < τ through → real fail is the threshold"
else
  echo "  ✗ teeth: ssim mutant did NOT pass the below-threshold fixture (got $rc) — teeth broken"
  rc_total=1
fi

# teeth 3: ssim DOMAIN CLAMP stripped — a page-controllable 5.0 wrongly becomes a pass.
sed 's/return math.isfinite(x) and 0.0 <= float(x) <= 1.0/return True/' \
  plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py >"$MUTCLAMP"
rc=0; python3 "$MUTCLAMP" "$F/bad-config-ssim-out-of-range.json" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "  ✓ teeth: mutant (clamp stripped) lets ssim 5.0 pass → the [0,1] clamp is real, not luck"
else
  echo "  ✗ teeth: clamp mutant did NOT pass the out-of-domain fixture (got $rc) — teeth broken"
  rc_total=1
fi

# NaN case (synthesized at runtime — invalid JSON can't be committed): non-finite → error.
printf '{"ssim_score": NaN}\n' >"$NANEV"
printf '{"surface":"web","ssim":"%s"}\n' "$NANEV" >"$NANCFG"
rc=0; $D "$NANCFG" >/dev/null 2>&1 || rc=$?
if [[ "$rc" -eq 1 ]]; then
  echo "  ✓ ssim NaN → determinate error (not a pass, not a silent not_captured) — exit 1"
else
  echo "  ✗ ssim NaN did not resolve to a determinate error (got $rc)"
  rc_total=1
fi

if [[ "$rc_total" -eq 0 ]]; then
  echo "  Gate 100: PASS"
else
  echo "  Gate 100: FAIL"
fi
exit "$rc_total"
