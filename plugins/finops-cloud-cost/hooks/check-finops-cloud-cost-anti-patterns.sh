#!/usr/bin/env bash
# check-finops-cloud-cost-anti-patterns.sh — advisory PreToolUse hook for the
# finops-cloud-cost plugin. Flags mechanically-detectable FinOps anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set FINOPS_CLOUD_COST_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text/config/IaC files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.tf | *.tfvars | *.hcl | *.py | *.sh | *.txt) ;;
*) exit 0 ;;
esac

findings=()

# 1. Resource or IaC block with no tags/owner.
# Detect terraform resource blocks without a tags or labels block inside.
if grep -nEi "^\s*resource\s+\"" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\btags\b\s*=|\blabels\b\s*=|\bowner\b\s*=" "$file" >/dev/null 2>&1; then
    findings+=("IaC resource block with no tags/labels/owner — tag at birth or you cannot allocate. Add mandatory tags (environment, team, project, application, managed-by).")
  fi
fi

# 2. ":latest" image tag or on-demand keyword with no commitment note.
# A ":latest" tag in a cost/infra doc is often a placeholder — flag it with a commitment note check.
if grep -nEi '":latest"' "$file" >/dev/null 2>&1 && ! grep -nEi "(savings.?plan|reserved.?instance|committed.?use|commitment|on.?demand.?note|RI\b|CUD\b)" "$file" >/dev/null 2>&1; then
  findings+=('"\":latest\"" image reference with no commitment or on-demand note — confirm whether this workload has a rightsizing and commitment plan, or document that it runs on-demand intentionally.')
fi

# Also flag explicit on-demand reference in cost/finops context without a commitment mention.
if grep -nEi "\bon.?demand\b" "$file" >/dev/null 2>&1 && ! grep -nEi "(savings.?plan|reserved.?instance|committed.?use|commitment|RI\b|CUD\b|intentionally on.?demand|no commitment|baseline)" "$file" >/dev/null 2>&1; then
  findings+=("'on-demand' referenced with no commitment strategy or note — if this is steady-state baseline usage, document whether a commitment (RI/SP/CUD) was considered and the outcome.")
fi

# 3. Hard-coded dollar/cost figure with no date.
# Match patterns like $1,234 or $1234 or 1234.56 USD or cost: 450 with no nearby date (YYYY or YYYY-MM-DD).
if grep -nEi '(\$[0-9]+([,\.][0-9]+)*|[0-9]+(\.[0-9]+)?\s*(USD|usd|\$/month|\$/hr|\$/hour|per month|per hour))' "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(20[0-9]{2}-[0-9]{2}|20[0-9]{2}|verify.?at.?use|retrieved|as of|pricing as)" "$file" >/dev/null 2>&1; then
    findings+=("Hard-coded dollar/cost figure with no retrieval date — cloud pricing changes frequently. Add a date and [verify-at-use] to every cost figure so stale prices are visible.")
  fi
fi

# 4. "Reserved Instance" or "Savings Plan" purchase mentioned with no break-even or coverage analysis.
if grep -nEi "(reserved.?instance|savings.?plan|committed.?use.?discount)\s.{0,30}(purchase|buy|bought|commit)" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "(break.?even|coverage|break_even|commitment_coverage|months.?to.?payback|payback.?period|utilization.?%)" "$file" >/dev/null 2>&1; then
    findings+=("Reserved Instance / Savings Plan purchase mentioned with no break-even or coverage analysis — rightsize first, calculate the steady-state baseline, and run finops_calc.py break_even() before committing.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── finops-cloud-cost advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${FINOPS_CLOUD_COST_STRICT:-0}" = "1" ]; then
  echo "(blocking: FINOPS_CLOUD_COST_STRICT=1)" >&2
  exit 2
fi
exit 0
