#!/usr/bin/env bash
# check-aws-cloud-anti-patterns.sh — advisory PreToolUse hook for the aws-cloud plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set AWSCLOUD_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
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
