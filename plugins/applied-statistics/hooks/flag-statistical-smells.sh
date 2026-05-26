#!/usr/bin/env bash
# flag-statistical-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on analysis files (.py/.ipynb/.R/
# .Rmd/.qmd/.md/.sql). Flags four mechanically-detectable violations of the
# applied-statistics team constitution (see plugins/applied-statistics/CLAUDE.md
# §3, §4, and knowledge/statistical-pitfalls.md):
#
#   1. A p-value reported with NO effect size / confidence interval nearby
#      (pitfall #6 — significance ≠ effect size)
#   2. Three or more hypothesis-test calls in one file with NO multiple-comparison
#      correction (pitfall #2 — multiple comparisons)
#   3. A parametric test (t-test / ANOVA / OLS) with NO assumption check mentioned
#      (pitfall #7 — assumption violations)
#   4. Correlation language paired with causal verbs in an analysis doc
#      (pitfall — correlation ≠ causation; needs a causal design)
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set APPLIED_STATS_STRICT=1 to
# make violations blocking (exit 1).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect analysis-shaped files.
case "$base_lc" in
  *.py | *.ipynb | *.r | *.rmd | *.qmd | *.md | *.sql) ;;
  *) exit 0 ;;
esac

violations=()

# Patterns reused below.
pval_re='p[-_ ]?value|p\s*[<=>]\s*0?\.[0-9]|pvalue|\bp\s*[<=]\s*\.[0-9]'
effect_re='confidence interval|conf[._ ]?int|\bci\b|95%|effect[ _-]?size|cohen|effsize|odds[ _-]?ratio|\bcompute_effsize\b'
test_call_re='\bttest_ind\b|\bttest_rel\b|\bttest_1samp\b|\bf_oneway\b|\bmannwhitneyu\b|\bwilcoxon\b|\bkruskal\b|\bchi2_contingency\b|\bttest\b|\.ttest\(|stats\.ttest'
correction_re='multipletests|bonferroni|\bholm\b|\bfdr\b|benjamini|hochberg|\.correct\('
parametric_re='\bttest_ind\b|\bttest_rel\b|\bf_oneway\b|smf\.ols|sm\.ols|\bols\(|aov\('
assumption_re='shapiro|levene|normaltest|d.?agostino|q-?q|qqplot|bartlett|assumption|homoscedastic|normality'
causal_verb_re='\bcauses?\b|\bcaused\b|because of|\bdrives?\b|\bdriven by\b|impact of|leads to|results in'

# ---------------------------------------------------------------------------
# Check 1: p-value with no effect size / CI nearby
# ---------------------------------------------------------------------------
if grep -niEq "$pval_re" "$file" 2>/dev/null; then
  if ! grep -niEq "$effect_re" "$file" 2>/dev/null; then
    violations+=("A p-value is reported but no effect size / confidence interval is in the file. Significance ≠ importance — report effect size + CI. (pitfall #6)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: 3+ test calls with no multiple-comparison correction
# ---------------------------------------------------------------------------
n_tests=$(grep -niEo "$test_call_re" "$file" 2>/dev/null | wc -l | tr -d ' ')
if [[ "${n_tests:-0}" -ge 3 ]]; then
  if ! grep -niEq "$correction_re" "$file" 2>/dev/null; then
    violations+=("${n_tests} hypothesis tests in one file with no multiple-comparison correction. Apply Holm/Bonferroni (confirmatory) or Benjamini-Hochberg (exploratory). (pitfall #2)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 3: parametric test with no assumption check
# ---------------------------------------------------------------------------
if grep -niEq "$parametric_re" "$file" 2>/dev/null; then
  if ! grep -niEq "$assumption_re" "$file" 2>/dev/null; then
    violations+=("A parametric test (t-test / ANOVA / OLS) with no assumption check (normality / equal variance). Check assumptions or use the nonparametric fallback. (pitfall #7)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 4: correlation language + causal verbs in an analysis doc
# ---------------------------------------------------------------------------
case "$base_lc" in
  *.md | *.rmd | *.qmd | *.ipynb)
    if grep -niEq 'correlat' "$file" 2>/dev/null && grep -niEq "$causal_verb_re" "$file" 2>/dev/null; then
      violations+=("Correlation language paired with causal verbs (causes/drives/impact). A coefficient is association, not cause, without a causal design. (correlation ≠ causation)")
    fi
    ;;
esac

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[applied-statistics-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set APPLIED_STATS_STRICT=1 to make them blocking." >&2
echo "  See plugins/applied-statistics/knowledge/statistical-pitfalls.md for the fixes." >&2
echo "" >&2

if [[ "${APPLIED_STATS_STRICT:-0}" == "1" ]]; then
  exit 1
fi
exit 0
