#!/usr/bin/env bash
# check-manufacturing-operations-anti-patterns.sh — advisory PreToolUse hook for the manufacturing-operations plugin.
# Flags mechanically-detectable manufacturing anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set MFG_STRICT=1 to make it blocking (exit 2).
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
[ -z "$file" ] && exit 0
# --- proposed-edit scan target (repo-review 2026-09-23) ----------------------
# At PreToolUse the write has NOT landed: the on-disk file is the PRE-edit state
# (or absent for a new-file Write), so grepping "$file" misses the very content
# this hook exists to catch. Build the scan target from the tool payload —
# .tool_input.content (Write) / .tool_input.new_string (Edit) /
# .tool_input.edits[].new_string (MultiEdit) — and scan THAT. The on-disk file is
# used only as a legacy fallback for a manual, no-stdin invocation (payload unset).
# (Fix propagated from data-platform/hooks/flag-data-platform-smells.sh, 2026-09-03.)
scan_target="$file"
if [ -n "${payload:-}" ] && command -v jq >/dev/null 2>&1; then
  _rc_proposed="$(printf '%s' "$payload" | jq -r '[.tool_input.content // empty, .tool_input.new_string // empty, ((.tool_input.edits // [])[]?.new_string // empty)] | map(select(. != "")) | join("\n")' 2>/dev/null || true)"
  if [ -n "$_rc_proposed" ]; then
    _rc_scan_tmp="$(mktemp 2>/dev/null || true)"
    if [ -n "$_rc_scan_tmp" ]; then
      printf '%s\n' "$_rc_proposed" > "$_rc_scan_tmp"
      scan_target="$_rc_scan_tmp"
      trap 'rm -f "$_rc_scan_tmp"' EXIT
    fi
  fi
fi
[ -z "$scan_target" ] && exit 0
[ ! -f "$scan_target" ] && exit 0

findings=()

# 1. An OEE figure quoted without a stated ideal cycle time / downtime basis — undefined denominators = theater.
if grep -qiE "\bOEE\b" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "(ideal\s+cycle\s+time|cycle\s+time|planned\s+downtime|unplanned\s+downtime|availability.*performance.*quality)" "$scan_target" 2>/dev/null; then
    findings+=("OEE referenced with no stated ideal cycle time / downtime basis — define the denominators or the number is uncomparable theater.")
  fi
fi

# 2. A CAPA/NCR that contains containment but no root-cause or preventive action — the defect will recur.
if grep -qiE "\b(CAPA|NCR|nonconformance|non-conformance)\b" "$scan_target" 2>/dev/null \
  && grep -qiE "\b(contain|containment|scrap|rework)\b" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "(root[ -]?cause|preventive\s+action|5[ -]?why|fishbone|ishikawa|corrective\s+and\s+preventive)" "$scan_target" 2>/dev/null; then
    findings+=("CAPA/NCR with containment but no root-cause / preventive action — containment alone is not a CAPA; the defect is scheduled to recur.")
  fi
fi

# 3. A master schedule / MPS asserted with no capacity or constraint reference — infinite-capacity planning.
if grep -qiE "(master\s+schedule|\bMPS\b|production\s+schedule)" "$scan_target" 2>/dev/null; then
  if ! grep -qiE "(capacity|bottleneck|constraint|finite|takt|load)" "$scan_target" 2>/dev/null; then
    findings+=("Master schedule / MPS with no capacity or constraint reference — plan to the bottleneck's finite rate, not to infinite capacity.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── manufacturing-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${MFG_STRICT:-0}" = "1" ]; then
  echo "(blocking: MFG_STRICT=1)" >&2
  exit 2
fi
exit 0
