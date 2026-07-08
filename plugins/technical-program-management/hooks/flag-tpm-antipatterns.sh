#!/usr/bin/env bash
# flag-tpm-antipatterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on technical-program-management
# artifact files (.md). Flags four mechanically-detectable violations of the TPM
# team constitution (see plugins/technical-program-management/CLAUDE.md):
#
#   1. A status update that leads with activity and has no decision/ask
#      (status-leads-with-decisions-not-activity.md)
#   2. A launch / readiness / go-no-go doc with NO go/no-go or pass/fail criteria
#      (go-no-go-needs-written-criteria.md)
#   3. A program charter with NO measurable outcome and NO named sponsor
#      (program-charter skill — a program without these is a request)
#   4. A dependency doc that is really a task list (no producer/consumer/handoff
#      language) (a-program-is-dependencies-not-tasks.md)
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set TPM_STRICT=1 to make
# violations blocking (exit 2).
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

# Only inspect markdown artifacts.
case "$base_lc" in
  *.md) : ;;
  *) exit 0 ;;
esac

# Lowercased content for case-insensitive matching.
content_lc=$(tr '[:upper:]' '[:lower:]' < "$file" 2>/dev/null || true)
[[ -z "$content_lc" ]] && exit 0

warnings=()

# --- Check 1: status update that leads with activity, no decision/ask --------
if printf '%s' "$base_lc" | grep -Eq 'status'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'decision needed|decision:|the ask|ask:|escalat'; then
    warnings+=("Status content with no decision/ask — a status that leads with activity has failed its only job; lead with the change in risk/critical path, the decision needed, and the ask (status-leads-with-decisions-not-activity.md).")
  fi
fi

# --- Check 2: launch/readiness doc with no go/no-go or pass/fail criteria -----
if printf '%s' "$content_lc" | grep -Eq 'launch readiness|go/no-go|go ?/ ?no-go|readiness review|go-live'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'criteria|pass/fail|pass ?/ ?fail|go / no-go|go/no-go|threshold'; then
    warnings+=("Launch/readiness content with no go/no-go or pass-fail criteria — a launch decided on vibe is an accident waiting for a retro; define measurable, owner-assigned criteria before the review (go-no-go-needs-written-criteria.md).")
  fi
fi

# --- Check 3: program charter with no measurable outcome / named sponsor ------
if printf '%s' "$content_lc" | grep -Eq 'program charter|charter:'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'sponsor'; then
    warnings+=("Program charter with no named sponsor — a program without a single accountable sponsor is a request, not a program (program-charter skill).")
  fi
  if ! printf '%s' "$content_lc" | grep -Eq 'outcome|metric|measurable|target'; then
    warnings+=("Program charter with no measurable outcome — you can't close what you can't measure; state the outcome as metric + target + date (program-charter skill).")
  fi
fi

# --- Check 4: dependency doc that is really a task list ----------------------
if printf '%s' "$base_lc" | grep -Eq 'depend'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'producer|consumer|handoff|critical path|interface|contract'; then
    warnings+=("Dependency content with no producer/consumer/handoff language — a 'dependency list' with no cross-team edges is a task list; a program is its dependencies, not its tasks (a-program-is-dependencies-not-tasks.md).")
  fi
fi

[[ ${#warnings[@]} -eq 0 ]] && exit 0

{
  echo "⚠️  technical-program-management advisory — $(basename "$file"):"
  for w in "${warnings[@]}"; do
    echo "   • $w"
  done
} >&2

if [[ "${TPM_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
