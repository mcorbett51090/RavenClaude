#!/usr/bin/env bash
set -euo pipefail

# flag-tableau-anti-patterns.sh — advisory PreToolUse(Write|Edit) hook for the tableau plugin.
# Reads a file path as $1 (or from the hook JSON on stdin) and greps Tableau workbook/data-source
# XML (.twb/.twbx-unpacked, .tds/.tdsx-unpacked) for the grep-able anti-patterns from the team
# constitution (§4). Prints advisory notes to stderr. ALWAYS exits 0 — this is advisory, never
# blocking. Security verdicts (RLS, embedding auth) escalate to ravenclaude-core/security-reviewer.

target="${1:-}"

# If no arg, try to parse tool_input.file_path from stdin JSON (PreToolUse).
if [[ -z "$target" ]]; then
  if command -v jq >/dev/null 2>&1; then
    target="$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
  fi
fi

if [[ -z "$target" || ! -f "$target" ]]; then
  exit 0
fi

# Only inspect Tableau text/XML artifacts (workbooks, data sources, unpacked .twb/.tds).
case "$target" in
  *.twb | *.tds) ;;
  *) exit 0 ;;
esac

notes=()

# 1. Legacy trusted-ticket embedding instead of Connected Apps + JWT (house opinion #8)
if grep -qiE 'trusted[_-]?ticket|:tickets=|trusted_authentication' "$target" 2>/dev/null; then
  notes+=("Possible legacy trusted-ticket embedding — use a Connected App + JWT (Embedding API v3) instead; the auth verdict escalates to security-reviewer. (house opinion #8)")
fi

# 2. Embedded service-account credentials / inline password in a connection (anti-pattern + secret leak)
if grep -qiE '<connection[^>]*\bpassword=|<connection[^>]*\busername=[^>]*password' "$target" 2>/dev/null \
  || grep -qiE 'password=["'\''][^"'\'' ]+["'\'']' "$target" 2>/dev/null; then
  notes+=("Possible embedded credentials in a connection — never store a service-account password in a workbook/data source; use OAuth / a published data source with managed creds. (anti-pattern; escalate to security-reviewer)")
fi

# 3. Live connection (no extract) — flag to confirm a stated freshness requirement (house opinion #4)
if grep -qiE '<connection[^>]*\bclass=' "$target" 2>/dev/null \
  && ! grep -qiE '<extract\b|\.hyper|<connection[^>]*\bclass=["'\'']?(hyper|dataengine)' "$target" 2>/dev/null; then
  notes+=("Live connection with no extract detected — name the freshness requirement that justifies live, else extract by default for performance. (house opinion #4)")
fi

# 4. Data blend (multiple datasources joined at view level) where a relationship may be correct (anti-pattern)
if [[ "$(grep -ciE '<datasource\b' "$target" 2>/dev/null || echo 0)" -gt 1 ]] \
  && grep -qiE '<datasource-dependencies|primary-key|<cols>.*\[.*\]\.\[' "$target" 2>/dev/null; then
  notes+=("Multiple data sources detected — confirm this is a relationship/join, not a data blend used where a relationship would be correct (and faster). (anti-pattern)")
fi

# 5. Table calc left on default addressing (silently-wrong totals) (anti-pattern)
if grep -qiE 'compute-using|table-calc|WINDOW_|RUNNING_|TOTAL\(' "$target" 2>/dev/null \
  && ! grep -qiE 'compute-using=["'\''][^"'\'' ]' "$target" 2>/dev/null; then
  notes+=("Table calculation without explicit addressing — set compute-using/partitioning explicitly; default 'Table (across)' is a latent wrong-number bug. (anti-pattern)")
fi

# 6. RLS implemented as a hidden user filter rather than an enforced data policy (house opinion #6)
if grep -qiE 'USERNAME\(\)|ISMEMBEROF\(|FULLNAME\(\)' "$target" 2>/dev/null; then
  notes+=("USERNAME()/ISMEMBEROF() in a calc — a per-workbook user filter is a convenience, not a control; if a row leak matters, make it a data-policy RLS and escalate to security-reviewer. (house opinion #6)")
fi

# Emit notes (advisory, never blocking)
if [[ ${#notes[@]} -gt 0 ]]; then
  printf '\n[tableau] House-opinion advisory for %s:\n' "$target" >&2
  for n in "${notes[@]}"; do
    printf '  - %s\n' "$n" >&2
  done
  printf '  (RLS / embedding-auth findings escalate to ravenclaude-core/security-reviewer.)\n\n' >&2
fi

exit 0
