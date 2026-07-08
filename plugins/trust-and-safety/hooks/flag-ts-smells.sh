#!/usr/bin/env bash
# flag-ts-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on Trust & Safety policy / detection
# files (.md/.py/.yaml/.yml/.json). Flags two mechanically-detectable violations of
# the trust-and-safety team constitution (see plugins/trust-and-safety/CLAUDE.md
# §3 and §4):
#
#   1. An enforcement ACTION (remove / suspend / ban / limit / takedown) is described
#      with NO appeal / contest / due-process path mentioned anywhere in the file
#      (house opinion #2 — appeals are due process, not optional).
#   2. A classifier THRESHOLD / cutoff / score-band is set with NO precision or recall
#      noted anywhere in the file (house opinion #4 / abuse-detection-engineer —
#      every threshold is tied to precision/recall).
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set TS_STRICT=1 to make violations
# blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to the
# agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect policy / detection-shaped files.
case "$base_lc" in
  *.md | *.py | *.yaml | *.yml | *.json) ;;
  *) exit 0 ;;
esac

violations=()

# Patterns reused below.
action_re='\bremove\b|\bremoval\b|\bsuspend\b|\bsuspension\b|\bban\b|\bbanned\b|\btakedown\b|take[ _-]?down|\bblock\b|enforce|enforcement[ _-]?action|deplatform'
appeal_re='appeal|contest|due[ _-]?process|dispute|notice[ _-]?and[ _-]?reason|right to (a )?review|overturn|redress'
threshold_re='threshold|cut[ _-]?off|score[ _-]?band|operating[ _-]?point|\bdecision boundary\b|>=\s*0?\.[0-9]|<=\s*0?\.[0-9]|confidence[ _-]?score'
prcl_re='precision|recall|\bpr[ _-]?curve\b|\bf1\b|true[ _-]?positive|false[ _-]?positive|false[ _-]?negative|tpr|fpr'

# ---------------------------------------------------------------------------
# Check 1: enforcement action with no appeal / due-process path
# ---------------------------------------------------------------------------
if grep -niEq "$action_re" "$file" 2>/dev/null; then
  if ! grep -niEq "$appeal_re" "$file" 2>/dev/null; then
    violations+=("An enforcement action (remove / suspend / ban / limit) is described but no appeal / contest / due-process path is in the file. Every action carries an appeal. (house opinion #2)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: classifier threshold with no precision / recall noted
# ---------------------------------------------------------------------------
if grep -niEq "$threshold_re" "$file" 2>/dev/null; then
  if ! grep -niEq "$prcl_re" "$file" 2>/dev/null; then
    violations+=("A classifier threshold / score cutoff is set but no precision or recall is noted. Tie every threshold to its precision/recall at that operating point. (house opinion #4)")
  fi
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[trust-and-safety-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set TS_STRICT=1 to make them blocking." >&2
echo "  See plugins/trust-and-safety/knowledge/ for the fixes." >&2
echo "" >&2

if [[ "${TS_STRICT:-0}" == "1" ]]; then
  # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is non-blocking
  # and would silently allow the edit despite the warning.
  exit 2
fi
exit 0
