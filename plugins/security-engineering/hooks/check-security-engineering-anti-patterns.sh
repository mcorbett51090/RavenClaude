#!/usr/bin/env bash
# check-security-engineering-anti-patterns.sh — advisory PreToolUse hook for the security-engineering plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set SECENG_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(AKIA[0-9A-Z]{16}|secret_key\\s*=|password\\s*=\\s*[\\\"'][^\\\"']+[\\\"']|api[_-]?key\\s*=\\s*[\\\"'][^\\\"']+[\\\"'])" "$file" >/dev/null 2>&1; then
  findings+=("Possible hardcoded secret/credential — a committed secret is compromised; vault it and rotate.")
fi
if grep -nEi "(verify\\s*=\\s*False|InsecureSkipVerify\\s*:\\s*true|rejectUnauthorized\\s*:\\s*false)" "$file" >/dev/null 2>&1; then
  findings+=("TLS verification disabled — this defeats transport security; do not ship.")
fi
if grep -nEi "(\\\"Resource\\\"\\s*:\\s*\\\"\\*\\\"|\\\"Action\\\"\\s*:\\s*\\\"\\*\\\"|iam:\\*|AdministratorAccess)" "$file" >/dev/null 2>&1; then
  findings+=("Wildcard IAM permission — least-privilege violation; grant the minimum needed.")
fi
if grep -nEi "(0\\.0\\.0\\.0/0).*(22|3389|admin)" "$file" >/dev/null 2>&1; then
  findings+=("Network open to 0.0.0.0/0 on an admin/SSH/RDP port — unintended exposure.")
fi
if grep -nEi "(md5|sha1)\\s*\\(" "$file" >/dev/null 2>&1; then
  findings+=("Weak hash (MD5/SHA1) — use SHA-256+ / a password KDF (bcrypt/argon2) as appropriate.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── security-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${SECENG_STRICT:-0}" = "1" ]; then
  echo "(blocking: SECENG_STRICT=1)" >&2
  exit 2
fi
exit 0
