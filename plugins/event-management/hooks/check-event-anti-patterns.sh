#!/usr/bin/env bash
# check-event-anti-patterns.sh — advisory PreToolUse hook for the event-management plugin.
# Flags mechanically-detectable event-planning anti-patterns on Edit/Write/MultiEdit of .md
# files. Advisory by default (exit 0, prints a notice); set EVENT_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect markdown files (plans, run-of-shows, reports).
case "$file" in
  *.md) ;;
  *) exit 0 ;;
esac

findings=()

# 1. A budget doc with no contingency/buffer line.
if grep -nEi 'budget' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'contingency|buffer' "$file" >/dev/null 2>&1; then
    findings+=("This looks like a budget doc with no 'contingency'/'buffer' line — every event budget carries a named buffer (commonly 10-20%).")
  fi
fi

# 2. A run-of-show with no owner/role column.
if grep -nEi 'run.?of.?show|show.?flow' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'owner|role|responsible' "$file" >/dev/null 2>&1; then
    findings+=("This run-of-show has no owner/role column — every segment row needs a named owner, or it is just an agenda.")
  fi
fi

# 3. A plan with no go/no-go or success-metric mention.
if grep -nEi 'event plan|event budget|plan & budget|plan and budget' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'go.?no.?go|success metric|kpi|break.?even' "$file" >/dev/null 2>&1; then
    findings+=("This event plan names no go/no-go gate or success metric/KPI — decide the goal you'll measure and the dated go/no-go threshold before spend ramps.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── event-management advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${EVENT_STRICT:-0}" = "1" ]; then
  echo "(blocking: EVENT_STRICT=1)" >&2
  exit 2
fi
exit 0
