#!/usr/bin/env bash
# check-devops-cicd-anti-patterns.sh — advisory PreToolUse hook for the devops-cicd plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DEVOPS_STRICT=1 to make it blocking (exit 2).
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
if grep -nEi "uses:\\s*[^@]+@(v?[0-9]+|main|master|latest)\\b" "$scan_target" >/dev/null 2>&1; then
  findings+=("Action pinned to a moving tag/branch — pin to a SHA (supply-chain surface in your own pipeline).")
fi
if grep -nEi "(aws_access_key_id|aws_secret_access_key|AKIA[0-9A-Z]{16})" "$scan_target" >/dev/null 2>&1; then
  findings+=("Possible long-lived AWS key in a pipeline/config — use OIDC federation + short-lived tokens instead.")
fi
if grep -nEi "image:\\s*\\S+:latest" "$scan_target" >/dev/null 2>&1; then
  findings+=("Container image pinned to ':latest' — pin a version/digest; 'latest' is not a version.")
fi
if grep -nEi "kubectl\\s+apply.*\\b(prod|production)\\b" "$scan_target" >/dev/null 2>&1; then
  findings+=("Direct kubectl apply to prod — under GitOps this is drift; promote via a PR that the reconciler enforces.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── devops-cicd advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DEVOPS_STRICT:-0}" = "1" ]; then
  echo "(blocking: DEVOPS_STRICT=1)" >&2
  exit 2
fi
exit 0
