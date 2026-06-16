#!/usr/bin/env bash
# flag-devrel-anti-patterns.sh
# PostToolUse hook for Edit | Write | MultiEdit on DevRel-conventional files.
# Flags mechanically-detectable violations of the developer-relations team
# constitution (see plugins/developer-relations/CLAUDE.md "house opinions"):
#
#   1. A quickstart / getting-started file with NO time-to-first-success (TTFS)
#      target — the quickstart's north-star metric is undeclared (opinion #4).
#   2. Vanity metrics (followers, impressions, stars, member/registration count)
#      presented as a success/goal/KPI in a metrics/strategy/dashboard file —
#      vanity inputs are reach, never success criteria (opinion #2).
#   3. A talk abstract with no single declared takeaway (the content discipline
#      "one takeaway per talk").
#
# Advisory by default: prints warnings to stderr so Claude and the user both see
# them, but exits 0 so the edit is not blocked. To make this hook BLOCK on
# violation, change the final `exit 0` to `exit 1`.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only run on DevRel-conventional files. Conservative — unrelated edits aren't flagged.
case "$file" in
  */developer-relations/*) ;;
  *quickstart*.md|*getting-started*.md|*get-started*.md) ;;
  *devrel*.md|*metrics*.md|*funnel*.md|*community*.md|*talk*.md|*abstract*.md) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: quickstart with no time-to-first-success target ---
case "$file" in
  *quickstart*.md|*getting-started*.md|*get-started*.md)
    # Skip the shipped template itself (it intentionally carries placeholders).
    case "$file" in
      *templates/quickstart-template.md) ;;
      *)
        if ! grep -Eiq 'time[- ]to[- ]first[- ]success|first success|in (about )?[0-9]+ ?(min|minute)' "$file"; then
          violations+=("  [no-ttfs-target] $file: a quickstart should declare a time-to-first-success target (e.g. 'working in under 10 minutes').")
        fi
        ;;
    esac
    ;;
esac

# --- Check 2: vanity metrics presented as success criteria ---
case "$file" in
  *metrics*.md|*funnel*.md|*devrel*.md|*dashboard*.md|*strategy*.md)
    # Look for a line that ties a vanity term to goal/success/kpi/north-star/target.
    # Skip the devrel-metrics skill + dashboard template (they discuss the ban itself).
    case "$file" in
      *skills/devrel-metrics/SKILL.md|*templates/community-health-dashboard.md|*knowledge/*) ;;
      *)
        if grep -Eni '(follower|impression|stars?|member count|registration|sign-?up count).{0,40}(goal|success|kpi|north[- ]star|target|objective)' "$file" >/dev/null 2>&1; then
          while IFS= read -r line; do
            violations+=("  [vanity-metric-as-goal] $file: $line")
          done < <(grep -Eni '(follower|impression|stars?|member count|registration|sign-?up count).{0,40}(goal|success|kpi|north[- ]star|target|objective)' "$file" | head -3)
        fi
        ;;
    esac
    ;;
esac

# --- Check 3: talk abstract with no single takeaway ---
case "$file" in
  *talk*.md|*abstract*.md)
    case "$file" in
      *templates/talk-abstract-template.md) ;;
      *)
        if ! grep -Eiq 'one takeaway|single takeaway|key takeaway|one thing' "$file"; then
          violations+=("  [no-single-takeaway] $file: a talk should declare its one takeaway — the single thing the audience should remember.")
        fi
        ;;
    esac
    ;;
esac

if [[ ${#violations[@]} -gt 0 ]]; then
  {
    echo "developer-relations: advisory — DevRel anti-pattern(s) detected:"
    for v in "${violations[@]}"; do echo "$v"; done
    echo "(Advisory only — edit not blocked. See plugins/developer-relations/CLAUDE.md house opinions.)"
  } >&2
fi

exit 0
