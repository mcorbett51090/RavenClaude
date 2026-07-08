#!/usr/bin/env bash
# check-aws-cloud-anti-patterns.sh — advisory PreToolUse hook for the aws-cloud plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set AWSCLOUD_STRICT=1 to make it blocking (exit 2).
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
if grep -nEi "(AKIA[0-9A-Z]{16}|aws_access_key_id\\s*=|aws_secret_access_key\\s*=)" "$file" >/dev/null 2>&1; then
  findings+=("Long-lived AWS access key in code/config — use roles/IRSA/OIDC federation; rotate this key now.")
fi
if grep -nEi "\\\"Action\\\"\\s*:\\s*\\\"\\*\\\"|\\\"Resource\\\"\\s*:\\s*\\\"\\*\\\"|iam:\\*|AdministratorAccess" "$file" >/dev/null 2>&1; then
  findings+=("Wildcard IAM permission — scope to minimum actions + resource ARNs; cap with a permission boundary.")
fi
if grep -nEi "(0\\.0\\.0\\.0/0).*(22|3389|3306|5432|6379)" "$file" >/dev/null 2>&1; then
  findings+=("Security group open to 0.0.0.0/0 on an admin/DB port — restrict to referential SG / specific CIDR.")
fi
if grep -nEi "(\\\"PublicAccessBlockConfiguration\\\"\\s*:\\s*false|acl\\s*=\\s*\\\"public-read\\\"|BlockPublicAcls\\s*=\\s*false)" "$file" >/dev/null 2>&1; then
  findings+=("S3 public access enabled — block public access unless this is a reviewed exception.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── aws-cloud advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${AWSCLOUD_STRICT:-0}" = "1" ]; then
  echo "(blocking: AWSCLOUD_STRICT=1)" >&2
  exit 2
fi
exit 0
