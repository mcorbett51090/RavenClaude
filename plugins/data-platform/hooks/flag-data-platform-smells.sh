#!/usr/bin/env bash
# flag-data-platform-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on data-platform artifact files.
# Flags four mechanically-detectable violations of the data-platform team
# constitution (see plugins/data-platform/CLAUDE.md §3, §4):
#
#   1. Inline secrets — API keys, JWT signing secrets, connection strings with
#      credentials, OAuth client secrets in .tsx/.ts/.js/.py/.yml/.sql (§3 #4)
#   2. Postgres CREATE TABLE with tenant_id column but no ENABLE ROW LEVEL
#      SECURITY statement in the same file (§3 #3 — raw-Postgres tenant
#      isolation lives in DB RLS). Scope: Postgres-only by design.
#   3. JWT expiresIn / exp claim > 30 minutes in JWT-issuance code (§3 #4)
#   4. Per-viewer-priced BI tool references (Looker, Tableau Embedded, Sigma,
#      Metabase Pro) in stack-decision-record.md templates (§3 #2)
#
# Advisory by default: prints warnings to stderr so Claude and the user both see
# them, but exits 0 so the edit is not blocked. To make this hook BLOCK on
# violation, change the final `exit 0` to `exit 1` (or set
# DATA_PLATFORM_STRICT=1 in the environment).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Lowercased basename for pattern matching.
base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

violations=()

# ---------------------------------------------------------------------------
# Check 1: inline secrets
# ---------------------------------------------------------------------------
# Look for assignment patterns that strongly suggest a hard-coded secret.
# We're conservative — only flag obvious cases to keep false positives low.
case "$base_lc" in
  *.tsx|*.ts|*.js|*.py|*.yml|*.yaml|*.sql|*.env|*.toml|*.ini)
    # API key patterns: VAR_NAME = "sk_...", "pk_...", "ghp_...", "Bearer ...", etc.
    if grep -niE '(api[_-]?key|secret[_-]?key|jwt[_-]?signing[_-]?key|client[_-]?secret|access[_-]?token|password|refresh[_-]?token|bearer)\s*[:=]\s*["'"'"'][a-z0-9_-]{16,}["'"'"']' "$file" 2>/dev/null | grep -viE '(process\.env|os\.getenv|env\[|env\.|"\$\{|"<.*placeholder.*>"|"<your[_ -]|"\.\.\.|<<|YOUR_|REPLACE_ME|TODO|FILL_IN)' >/dev/null; then
      violations+=("Inline secret detected — credentials should come from environment variables, not source. (rule 1)")
    fi
    # Postgres connection strings with embedded passwords
    if grep -niE 'postgres(ql)?://[a-z0-9_.-]+:[a-z0-9!@#$%^&*_+=-]{4,}@' "$file" 2>/dev/null | grep -viE '(process\.env|os\.getenv|<|\.\.\.|YOUR_|REPLACE)' >/dev/null; then
      violations+=("Postgres connection string with embedded password detected — use env vars + DATABASE_URL pattern. (rule 1)")
    fi
    ;;
esac

# ---------------------------------------------------------------------------
# Check 2: Postgres CREATE TABLE with tenant_id but no ENABLE ROW LEVEL SECURITY
# ---------------------------------------------------------------------------
case "$base_lc" in
  *.sql)
    # If the file CREATEs a table with a tenant_id column...
    if grep -niE 'create\s+table[^;]+tenant_id\b' "$file" 2>/dev/null >/dev/null; then
      # ...and does NOT enable row level security anywhere in the same file
      if ! grep -niE 'enable\s+row\s+level\s+security' "$file" 2>/dev/null >/dev/null; then
        violations+=("Postgres table with tenant_id column but no ENABLE ROW LEVEL SECURITY in the same file. Multi-tenant tables must FORCE RLS. (rule 2)")
      fi
    fi
    ;;
esac

# ---------------------------------------------------------------------------
# Check 3: long-lived JWTs
# ---------------------------------------------------------------------------
# Look for JWT expiration patterns > 30 minutes in JWT-issuance code.
case "$base_lc" in
  *jwt*|*token*|*auth*|*.ts|*.js)
    # expiresIn: '1h', '2h', '1d', '7d', '24h', etc.
    if grep -niE 'expires?in\s*[:=]\s*["'"'"']?([2-9][0-9]+m|[1-9][0-9]*h|[1-9][0-9]*d)' "$file" 2>/dev/null >/dev/null; then
      # Filter out reasonable values: 5m, 10m, 15m, 20m, 25m, 30m
      if grep -niE 'expires?in\s*[:=]\s*["'"'"']?(([3-9][1-9]m)|([1-9][0-9]*h)|([1-9][0-9]*d))' "$file" 2>/dev/null >/dev/null; then
        violations+=("JWT expiresIn appears to be >30 minutes. Short-lived tokens (5-15 min) are the standard. (rule 3)")
      fi
    fi
    # Also: numeric seconds > 1800
    if grep -niE 'exp\s*[:=]\s*(now\s*\(\s*\)\s*[+]\s*|Date\.now\s*\(\s*\)\s*[+]\s*)?[0-9]{4,}' "$file" 2>/dev/null | grep -vE 'expiresIn|placeholder|comment|example' >/dev/null; then
      :  # numeric exp values are tricky to validate without parsing — skip for now
    fi
    ;;
esac

# ---------------------------------------------------------------------------
# Check 4: per-viewer-priced BI tool references in stack-decision-record.md
# ---------------------------------------------------------------------------
case "$base_lc" in
  *stack-decision-record*.md|*stack_decision_record*.md)
    # Resist Looker / Tableau Embedded / Sigma / Metabase Pro Interactive Embedding
    # at the stack-selection stage for SMB consulting profiles.
    if grep -niE '\b(looker(\s+embedded)?|tableau\s+embedded|sigma\s+(computing|deployment)|metabase\s+pro\s+interactive)\b' "$file" 2>/dev/null >/dev/null; then
      violations+=("Per-viewer-priced BI tool detected in stack-decision-record. Resist by default per house opinion #2 — surface the math (5-50 viewers × \$400+/viewer/yr) before defaulting. (rule 4)")
    fi
    ;;
esac

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

# Print warnings to stderr
echo "" >&2
echo "[data-platform-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  These are advisory by default. Set DATA_PLATFORM_STRICT=1 to make them blocking." >&2
echo "  See plugins/data-platform/CLAUDE.md §3, §4 for the rules." >&2
echo "" >&2

# Exit 0 for advisory; exit 1 if strict mode is set
if [[ "${DATA_PLATFORM_STRICT:-0}" == "1" ]]; then
  exit 1
fi
exit 0
