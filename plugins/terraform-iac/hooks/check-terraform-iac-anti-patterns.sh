#!/usr/bin/env bash
# check-terraform-iac-anti-patterns.sh — advisory PreToolUse hook for the terraform-iac plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set IAC_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(access_key|secret_key|password)\\s*=\\s*\\\"[^\\\"]+\\\"" "$file" >/dev/null 2>&1; then
  findings+=("Hardcoded credential in Terraform — source from a secrets manager + mark sensitive; never commit it (and it lands in state).")
fi
if grep -nEi "^\\s*count\\s*=" "$file" >/dev/null 2>&1; then
  findings+=("Resource uses 'count' — for collections prefer for_each (count recreates on reorder); count is fine only for a 0/1 conditional.")
fi
if grep -nEi "(source\\s*=\\s*\\\"[^\\\"]+\\\"(?![\\s\\S]{0,80}version\\s*=))" "$file" >/dev/null 2>&1; then
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
