#!/usr/bin/env bash
# check-field-service-management-anti-patterns.sh — advisory PreToolUse hook for the
# field-service-management plugin. Flags mechanically-detectable FSM anti-patterns on
# Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set FSM_STRICT=1 to make it blocking (exit 2).
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

# 1. SLA commitment with no dispatch or skill basis.
# Fires when an SLA response time is mentioned but the file has no reference to dispatch
# priority, skill match, or skill requirement.
if grep -nEi "\b(sla|response.?time|[0-9]+.?hour.?response|4.?hour|8.?hour|same.?day.?response)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(dispatch|priority|skill.?(match|require|level)|technician.?(cert|qual|auth))\b" "$file" >/dev/null 2>&1; then
    findings+=("SLA response-time commitment with no dispatch-priority or skill-match basis — an SLA is only as good as the dispatch rule and technician qualification that back it. Add the dispatch priority level and skill requirement.")
  fi
fi

# 2. Route or schedule recommendation with no geo/density note.
# Fires when routing or territory language appears but no geographic/density qualifier is present.
if grep -nEi "\b(rout(e|ing)|territor(y|ies)|schedule|dispatch.?board)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(geo(graph)?|densit(y|ies)|drive.?time|jobs.?per|zone|cluster|territory.?design)\b" "$file" >/dev/null 2>&1; then
    findings+=("Route or schedule recommendation with no geographic/density note — routing without territory-density data is guesswork. Reference geo clustering, drive-time targets, or jobs-per-drive-hour.")
  fi
fi

# 3. Truck-stock or parts decision with no service-level or first-time-fix note.
# Fires when truck stock / parts stocking language appears without a fill-rate or service-level anchor.
if grep -nEi "\b(truck.?stock|stock.?the.?part|parts?.?(level|inventory|carry|add|remov)|reorder.?point)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(fill.?rate|service.?level|first.?time.?fix|ftf|sla.?(tier|target)|stockout)\b" "$file" >/dev/null 2>&1; then
    findings+=("Truck-stock or parts-level decision with no service-level or first-time-fix note — every add/remove from truck stock must state the fill-rate target it is designed to meet. Add the service-level or first-time-fix basis.")
  fi
fi

# 4. Hard-coded labor rate with no date.
# Fires when a specific dollar-per-hour labor rate appears without a year or date qualifier.
if grep -nEi "\\\$[0-9]+(\.[0-9]+)?.?(per.?hour|/hr|hourly.?rate|labor.?rate|tech.?rate)" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(20[0-9]{2}|as.?of|effective|dated?|rate.?date)\b" "$file" >/dev/null 2>&1; then
    findings+=("Hard-coded labor rate with no date — labor rates change; a rate without a date becomes stale and misleading. Add the effective date or year, and mark it [verify-at-use].")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── field-service-management advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${FSM_STRICT:-0}" = "1" ]; then
  echo "(blocking: FSM_STRICT=1)" >&2
  exit 2
fi
exit 0
