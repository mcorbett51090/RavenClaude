#!/usr/bin/env bash
# check-terraform-iac-anti-patterns.sh — advisory PreToolUse hook for the terraform-iac plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set IAC_STRICT=1 to make it blocking (exit 2).
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
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(access_key|secret_key|password)\\s*=\\s*\\\"[^\\\"]+\\\"" "$file" >/dev/null 2>&1; then
  findings+=("Hardcoded credential in Terraform — source from a secrets manager + mark sensitive; never commit it (and it lands in state).")
fi
if grep -nEi "^\\s*count\\s*=" "$file" >/dev/null 2>&1; then
  findings+=("Resource uses 'count' — for collections prefer for_each (count recreates on reorder); count is fine only for a 0/1 conditional.")
fi
if grep -Pzi "(source\\s*=\\s*\\\"[^\\\"]+\\\"(?![\\s\\S]{0,80}version\\s*=))" "$file" >/dev/null 2>&1; then
  findings+=("Module source without a pinned version nearby — pin module versions for reproducible init.")
fi
if grep -nEi "backend\\s+\\\"local\\\"" "$file" >/dev/null 2>&1; then
  findings+=("Local state backend — use a remote, locked, encrypted backend; local state is unsafe for teams.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── terraform-iac advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${IAC_STRICT:-0}" = "1" ]; then
  echo "(blocking: IAC_STRICT=1)" >&2
  exit 2
fi
exit 0
