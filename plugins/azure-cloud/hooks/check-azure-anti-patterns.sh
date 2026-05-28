#!/usr/bin/env bash
# check-azure-anti-patterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on Azure IaC files
# (.bicep/.tf/.json/.yml/.yaml). Flags six mechanically-detectable violations of the
# azure-cloud team constitution (see plugins/azure-cloud/CLAUDE.md §3):
#
#   1. Hardcoded secret in IaC (password=/accountKey=/client_secret/connectionString/
#      primaryKey/SAS) — use Key Vault / managed identity (#4). [security]
#   2. Public exposure (0.0.0.0/0, publicNetworkAccess 'Enabled', allowBlobPublicAccess
#      true, allowSharedKeyAccess true) — deny-public-by-default (#6).
#   3. Owner/Contributor role assignment at subscription/management-group scope — over-
#      privilege; scope to RG/resource (#5).
#   4. TLS/HTTPS off (minimumTlsVersion < 1.2, httpsOnly/supportsHttpsTrafficOnly false).
#   5. Hardcoded subscription/tenant GUID — parameterize (#2).
#   6. Terraform local backend (backend "local") — use remote, locked state (#2).
#
# Advisory by default: prints to stderr, exits 0. Set AZURE_STRICT=1 to block.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

case "$base_lc" in
  *.bicep | *.tf | *.json | *.yml | *.yaml) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: hardcoded secret in IaC --- (#4)
# A secret-ish identifier (possibly with a Bicep type keyword before the '='/':')
# assigned a non-empty quoted literal. Excludes Key Vault references.
secret_re="(password|secret|accountkey|primarykey|connectionstring|apikey|sas[_-]?token)[a-z0-9_]*[^'\"=:]{0,24}[:=][[:space:]]*['\"][^'\"]{4,}['\"]"
if grep -Eni "$secret_re|sharedaccesskey" "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    case "$line" in
      *KeyVault*|*keyVault*|*getSecret*|*@Microsoft.KeyVault*|*"reference("*|*existing*) continue ;;
    esac
    violations+=("  [hardcoded-secret] $file: $line — use a Key Vault reference / managed identity, not a literal (CLAUDE.md §3 #4).")
  done < <(grep -Eni "$secret_re|sharedaccesskey" "$file" | head -3)
fi

# --- Check 2: public exposure --- (#6)
if grep -Eni "0\.0\.0\.0/0|publicnetworkaccess[\"' ]*[:=][\"' ]*enabled|allowblobpublicaccess[\"' ]*[:=][\"' ]*true|allowsharedkeyaccess[\"' ]*[:=][\"' ]*true" "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    violations+=("  [public-exposure] $file: $line — deny-public-by-default; use Private Endpoint / restrict source (CLAUDE.md §3 #6).")
  done < <(grep -Eni "0\.0\.0\.0/0|publicnetworkaccess|allowblobpublicaccess[\"' ]*[:=][\"' ]*true|allowsharedkeyaccess[\"' ]*[:=][\"' ]*true" "$file" | head -3)
fi

# --- Check 3: Owner/Contributor at subscription/MG scope --- (#5)
# File-level: an Owner/Contributor role reference + a role assignment/definition +
# a subscription/MG scope that is NOT narrowed to a resource group.
if grep -Eqi '(owner|contributor)' "$file" && grep -Eqi 'role[_]?(definition|assignment)' "$file"; then
  if grep -Eqi "scope[\"' ]*[:=][\"' ]*['\"]?(/subscriptions/[^/'\"[:space:]]+|/providers/[Mm]icrosoft\.[Mm]anagement)" "$file" && ! grep -Eqi '/resourcegroups/' "$file"; then
    violations+=("  [broad-rbac] $file assigns Owner/Contributor at subscription or management-group scope — scope to resource group/resource + use PIM (CLAUDE.md §3 #5).")
  fi
fi

# --- Check 4: TLS/HTTPS off --- (security baseline)
if grep -Eni "minimumtlsversion[\"' ]*[:=][\"' ]*['\"]?(1\.0|1\.1|tls1_0|tls1_1)|(httpsonly|supportshttpstrafficonly)[\"' ]*[:=][\"' ]*false" "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    violations+=("  [tls-or-https-off] $file: $line — require TLS 1.2+ and HTTPS-only (CLAUDE.md §3, security baseline).")
  done < <(grep -Eni "minimumtlsversion[\"' ]*[:=][\"' ]*['\"]?(1\.0|1\.1|tls1_0|tls1_1)|(httpsonly|supportshttpstrafficonly)[\"' ]*[:=][\"' ]*false" "$file" | head -3)
fi

# --- Check 5: hardcoded subscription/tenant GUID --- (#2)
if grep -Eni "(subscriptionid|tenantid|subscription_id|tenant_id)[[:space:]]*[:=][[:space:]]*['\"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}['\"]" "$file" >/dev/null 2>&1; then
  violations+=("  [hardcoded-guid] $file hardcodes a subscription/tenant GUID — parameterize it (CLAUDE.md §3 #2).")
fi

# --- Check 6: Terraform local backend --- (#2)
case "$base_lc" in
  *.tf)
    if grep -Eni 'backend[[:space:]]+"local"' "$file" >/dev/null 2>&1; then
      violations+=("  [local-tf-state] $file uses a local Terraform backend — use remote, locked, encrypted state (Azure Storage) for shared infra (CLAUDE.md §3 #2).")
    fi
    ;;
esac

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Azure anti-pattern check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/azure-cloud/CLAUDE.md §3 (house opinions). This hook is
  advisory — the edit was not blocked. Set AZURE_STRICT=1 to block.
────────────────────────────────────────────────────────────────────

EOF
  if [[ "${AZURE_STRICT:-0}" == "1" ]]; then
    exit 1
  fi
fi

exit 0
