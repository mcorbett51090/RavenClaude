#!/usr/bin/env bash
# check-revenue-operations-anti-patterns.sh — advisory PreToolUse hook for the
# revenue-operations plugin. Flags mechanically-detectable RevOps anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set REVENUE_OPERATIONS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text/config/doc files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.csv | *.py) ;;
*) exit 0 ;;
esac

findings=()

# 1. Pipeline stage defined with no exit criteria.
# Detects: a heading or label that looks like a stage name followed by content
# but no exit criterion language ("exit" / "criteria" / "must be" / "required").
# Conservative: only fires on files that appear to be stage-definition or pipeline docs.
case "$file" in
*stage* | *pipeline* | *opportunity*)
  if grep -nEi "^\s*#+\s*.*(stage|phase|step)\b" "$file" >/dev/null 2>&1; then
    if ! grep -nEi "(exit criteria|exit criterion|must be|required to|verifiable|objective condition)" "$file" >/dev/null 2>&1; then
      findings+=("Stage definition file with no exit-criteria language — every stage must have documented, objective, binary exit criteria. See best-practices/stages-are-exit-criteria-not-vibes.md.")
    fi
  fi
  ;;
esac

# 2. Hard-coded commission or quota figure with no date or source.
# Pattern: a dollar figure or percentage labeled as quota/commission/OTE/rate with no
# nearby source or date marker. Only fires on comp/quota/territory files.
case "$file" in
*comp* | *quota* | *territory* | *commission* | *ote* | *incentive* | *plan*)
  if grep -nEi "\\\$[0-9,]+[kKmM]?\s*(quota|ote|on.?target|commission|target|rate)" "$file" >/dev/null 2>&1 ||
    grep -nEi "(quota|commission rate|ote)\s*[:=]\s*\\\$?[0-9]" "$file" >/dev/null 2>&1; then
    if ! grep -nEi "(source|cite|benchmark|verify.at.use|as of [0-9]{4}|[0-9]{4}-[0-9]{2})" "$file" >/dev/null 2>&1; then
      findings+=("Hard-coded quota or commission figure with no source or date — every quota/rate/OTE figure must carry its methodology and source (year, vendor, internal data). See best-practices/the-comp-plan-is-the-strategy-design-it-deliberately.md.")
    fi
  fi
  ;;
esac

# 3. PII: SSN-shaped number, email list pattern, or full name + salary in plaintext.
# SSN pattern: NNN-NN-NNNN
if grep -nE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
  findings+=("SSN-shaped number detected (NNN-NN-NNNN pattern) — do not store SSNs or TINs in plaintext in any RevOps document. Route through ravenclaude-core/security-reviewer.")
fi

# Email list pattern: multiple email addresses on consecutive lines (bulk list indicator)
email_count=$(grep -cE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" "$file" 2>/dev/null || true)
if [ "${email_count:-0}" -gt 10 ]; then
  findings+=("More than 10 email addresses detected — this may be an employee or customer email list in plaintext. Route through ravenclaude-core/security-reviewer before storing or sharing.")
fi

# 4. "Forecast" asserted with no methodology named.
# Fires on files that use the word "forecast" or "commit" without naming a method.
case "$file" in
*forecast* | *pipeline* | *commit* | *projection*)
  if grep -nEi "\b(forecast|our forecast|q[1-4] forecast|annual forecast)\b" "$file" >/dev/null 2>&1; then
    if ! grep -nEi "(weighted|commit.category|category.forecast|ai.assisted|clari|gong forecast|einstein|methodology|method:)" "$file" >/dev/null 2>&1; then
      findings+=("'Forecast' used without a named methodology — every forecast must name its method (weighted probability / commit-category / AI-assisted). See best-practices/a-forecast-is-a-commitment-not-a-hope.md.")
    fi
  fi
  ;;
esac

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── revenue-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${REVENUE_OPERATIONS_STRICT:-0}" = "1" ]; then
  echo "(blocking: REVENUE_OPERATIONS_STRICT=1)" >&2
  exit 2
fi
exit 0
