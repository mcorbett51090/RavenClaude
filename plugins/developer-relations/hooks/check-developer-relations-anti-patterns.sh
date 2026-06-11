#!/usr/bin/env bash
# check-developer-relations-anti-patterns.sh — advisory PreToolUse hook for the
# developer-relations plugin. Flags mechanically-detectable DevRel anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set DEVREL_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text/config/doc files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.py | *.sh) ;;
*) exit 0 ;;
esac

findings=()

# 1. Vanity metric reported with no activation/adoption metric present.
# Fires when a vanity input is mentioned but no outcome metric appears alongside it.
if grep -nEi "\b(github ?stars?|followers?|impressions?|attendees?|registrants?|page ?views?)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(activation|adopt(ion|ed)?|time.?to.?first.?value|ttfv|conversion|first.?success|production.?(use|adoption))\b" "$file" >/dev/null 2>&1; then
    findings+=("Vanity metric cited with no activation/adoption metric — stars/followers/impressions/attendees are inputs, not outcomes. Pair each with the activation or adoption number it is meant to drive, or cut it (best-practices/measure-activation-not-vanity.md).")
  fi
fi

# 2. Content/program plan with no journey stage.
# Fires when content/program language appears but no journey stage is named.
if grep -nEi "\b(content ?plan|blog ?post|talk|demo|campaign|program|advocacy)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(awareness|evaluation|activation|adoption|expansion|journey ?stage|onboarding)\b" "$file" >/dev/null 2>&1; then
    findings+=("Content/program work with no developer-journey stage named — tag each piece to a stage (awareness/evaluation/activation/adoption/expansion) and a goal, not a topic wishlist (skills/developer-content-and-advocacy).")
  fi
fi

# 3. Community claim with no funnel stage / conversion.
# Fires when community/Discord/forum language appears but no funnel concept is present.
if grep -nEi "\b(community|discord|forum|slack ?community|ambassador)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(funnel|conversion|answer.?rate|contributor|active ?ratio|lurker|champion|response ?coverage)\b" "$file" >/dev/null 2>&1; then
    findings+=("Community work with no funnel stage or conversion — community is a funnel (lurker→asker→answerer→contributor→champion), not a megaphone. Name the stage and its conversion (best-practices/community-is-a-funnel-not-a-megaphone.md).")
  fi
fi

[ ${#findings[@]} -eq 0 ] && exit 0

{
  echo "developer-relations advisory — ${#findings[@]} possible anti-pattern(s) in $file:"
  for f in "${findings[@]}"; do
    echo "  • $f"
  done
} >&2

if [ "${DEVREL_STRICT:-0}" = "1" ]; then
  exit 2
fi
exit 0
