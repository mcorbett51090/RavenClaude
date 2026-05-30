#!/usr/bin/env bash
set -euo pipefail

# flag-salesforce-anti-patterns.sh — advisory PostToolUse hook for the salesforce plugin.
# Reads a file path as $1 (or from the PostToolUse JSON on stdin) and greps for the
# grep-able Salesforce anti-patterns. Prints advisory notes to stderr. ALWAYS exits 0 —
# this is advisory, never blocking. Security verdicts escalate to
# ravenclaude-core/security-reviewer.

target="${1:-}"

# If no arg, try to parse the tool_input.file_path from stdin JSON (PostToolUse).
if [[ -z "$target" ]]; then
  if command -v jq >/dev/null 2>&1; then
    target="$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
  fi
fi

if [[ -z "$target" || ! -f "$target" ]]; then
  exit 0
fi

# Only inspect Apex-ish files.
case "$target" in
  *.cls | *.trigger | *.apex) ;;
  *) exit 0 ;;
esac

notes=()

# 1. SOQL inside a loop (house opinion #1)
if grep -qiE '(for|while)\s*\(' "$target" 2>/dev/null \
  && grep -qiE '\[\s*SELECT\b' "$target" 2>/dev/null; then
  notes+=("Possible SOQL in a loop — query once outside the loop and use a Map. (house opinion #1)")
fi

# 2. DML inside a loop (house opinion #1)
if grep -qiE '(for|while)\s*\(' "$target" 2>/dev/null \
  && grep -qiE '^\s*(insert|update|upsert|delete|undelete|merge)\s' "$target" 2>/dev/null; then
  notes+=("Possible DML in a loop — collect into a List and issue one DML on the collection. (house opinion #1)")
fi

# 3. Hard-coded 15/18-char Salesforce IDs (house opinion #5)
if grep -qiE "'[a-zA-Z0-9]{15}([a-zA-Z0-9]{3})?'" "$target" 2>/dev/null; then
  notes+=("Possible hard-coded 15/18-char Salesforce ID — query by DeveloperName or use custom metadata. (house opinion #5)")
fi

# 4. SeeAllData=true (house opinion #10)
if grep -qiE 'SeeAllData\s*=\s*true' "$target" 2>/dev/null; then
  notes+=("@isTest(SeeAllData=true) detected — build data with a TestDataFactory instead. (house opinion #10)")
fi

# 5. Missing 'with sharing' on a class (house opinion #6)
if grep -qiE '\bclass\b' "$target" 2>/dev/null \
  && ! grep -qiE '(with|without|inherited)\s+sharing' "$target" 2>/dev/null; then
  notes+=("Class declares no sharing mode — default to 'with sharing'; justify any 'without sharing'. (house opinion #6)")
fi

# Emit notes (advisory, never blocking)
if [[ ${#notes[@]} -gt 0 ]]; then
  printf '\n[salesforce] House-opinion advisory for %s:\n' "$target" >&2
  for n in "${notes[@]}"; do
    printf '  - %s\n' "$n" >&2
  done
  printf '  (Security findings escalate to ravenclaude-core/security-reviewer.)\n\n' >&2
fi

exit 0
