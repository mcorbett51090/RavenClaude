#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the process-improvement plugin.
# Flags common Lean Six Sigma anti-patterns in generated deliverables
# (a capability index with no stability/spec context | a sigma level with no
# shift convention | solution-jumping language | a fix with no control plan).
# Advisory by default — set PROCESS_IMPROVEMENT_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${PROCESS_IMPROVEMENT_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "process-improvement" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scans — case-insensitive, advisory only. Each is a reminder to
# check the deliverable against the §3 house opinions, not a hard verdict.

# Cpk/Ppk mentioned without "control"/"stable"/"spec" nearby — the §2 rule that
# capability is meaningless on an out-of-control process and needs its spec limits.
if grep -Eiq '\bc?pk\b' "$FILE" && ! grep -Eiq 'in[ -]control|stable|stability|spec' "$FILE"; then
  note "A capability index (Cpk/Ppk) appears without a control/stability or spec-limit context — confirm the process is in statistical control and state the spec limits + sample window (§2)."
fi

# Sigma level mentioned without the 1.5-shift convention stated.
if grep -Eiq 'sigma level|[0-9]\.?[0-9]? ?sigma|dpmo' "$FILE" && ! grep -Eiq '1\.5|shift|short[ -]term|long[ -]term' "$FILE"; then
  note "A sigma level / DPMO appears without the 1.5σ-shift convention stated (short-term vs long-term) — omitting it makes the number unauditable (§3 anti-pattern)."
fi

# Solution-jumping language — a fix asserted near "root cause" without "proven"/"data".
if grep -Eiq 'root cause' "$FILE" && ! grep -Eiq 'proven|confirm|data|hypothesis test|p-value|significan' "$FILE"; then
  note "Root cause is referenced without 'proven'/'confirmed with data' — a countermeasure on an unproven cause is solution-jumping (§3 #4); route the confirmatory test to applied-statistics."
fi

# A declared improvement/fix with no control-plan language.
if grep -Eiq 'improvement|the fix|countermeasure|rolled out' "$FILE" && ! grep -Eiq 'control plan|control chart|reaction plan|standard work|sustain' "$FILE"; then
  note "An improvement/fix appears without a control-plan element (control chart / reaction plan / standard work / owner) — the gain will revert without one (§3 #6)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "process-improvement: $findings advisory finding(s); PROCESS_IMPROVEMENT_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
