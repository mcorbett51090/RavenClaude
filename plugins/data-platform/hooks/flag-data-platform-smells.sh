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
# Advisory by default: prints warnings to stderr so a human watching the
# terminal sees them, AND emits a hookSpecificOutput.additionalContext JSON
# envelope on stdout so the MODEL sees them too (a stderr-at-exit-0 line never
# reaches the model's context on its own — see
# plugins/ravenclaude-core/knowledge/hook-advisory-channel-and-cache.md). Exits
# 0 so the edit is not blocked by default. To make this hook BLOCK on
# violation, set DATA_PLATFORM_STRICT=1 in the environment (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed). STRICT=1 below
# uses exit 2 — the only blocking code.
#
# ⛔ WHAT GETS CHECKED, AND WHY (fixed 2026-09-03 — FORGE dashboard-top1pct
# P0-3; both panels found this independently and the critic verified it
# firsthand): at PreToolUse the write has NOT happened yet. Grepping the file
# as it exists ON DISK misses a Write of a brand-new file (nothing on disk
# yet — the old code hit `[[ ! -f "$file" ]] && exit 0` here) and misses an
# Edit that introduces a violation (the on-disk content is the PRE-edit
# state). This hook instead builds its subject text from the tool payload
# itself — `.tool_input.content` (Write), `.tool_input.new_string` (Edit),
# each `.tool_input.edits[].new_string` (MultiEdit) — which is the only way
# to see the PROPOSED write before it lands. `.tool_input.file_path` is used
# solely for extension/basename routing (deciding which checks apply), never
# as the thing that gets grepped. The on-disk file is read only as a legacy
# fallback for a non-Claude-Code manual invocation (no stdin JSON at all —
# e.g. `bash flag-data-platform-smells.sh <path>` from a terminal or a test
# harness that doesn't synthesize a PreToolUse payload).
#
# ⛔ MANUAL-TEST CAVEAT: this repo's marketplace-dev hook mirror
# (`.claude/settings.json`) does NOT include data-platform's hooks —
# `grep -c "data-platform" .claude/settings.json` reads 0 in this worktree
# (checked 2026-09-03). So the "does additionalContext actually reach a live
# model's reply" acceptance test cannot run from inside this worktree as-is;
# it needs either a scratch project with `data-platform@ravenclaude` installed
# via `/plugin install`, or a temporary dev-mirror entry added for the
# duration of the test. Fixture-level behavior (fires/silent, both the
# legacy arg-path and the real PreToolUse-stdin-payload path, STRICT
# blocking) IS verified — see scripts/audit-gates.sh Gate 30's
# data-platform-smells assertions.

set -euo pipefail

file=""
write_content=""
edit_new=""
multi_new=""
have_content=0

# Read stdin JSON once (Claude Code's canonical PreToolUse contract).
if [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
    write_content="$(printf '%s' "$payload" | jq -r '.tool_input.content // empty' 2>/dev/null || true)"
    edit_new="$(printf '%s' "$payload" | jq -r '.tool_input.new_string // empty' 2>/dev/null || true)"
    multi_new="$(printf '%s' "$payload" | jq -r '(.tool_input.edits // [])[]?.new_string // empty' 2>/dev/null || true)"
    if [[ -n "$write_content$edit_new$multi_new" ]]; then
      have_content=1
    fi
  fi
fi

# Legacy fallback: $1 as a bare file-path arg with NO stdin JSON at all — a
# manual/non-Claude-Code invocation. Under a real Claude Code PreToolUse
# dispatch, stdin JSON is always supplied, so this branch never fires there.
if [[ -z "$file" ]]; then
  file="${1:-}"
fi
[[ -z "$file" ]] && exit 0

if [[ "$have_content" -eq 1 ]]; then
  subject_text="${write_content}
${edit_new}
${multi_new}"
elif [[ -f "$file" ]]; then
  subject_text="$(cat "$file" 2>/dev/null || true)"
else
  exit 0 # nothing proposed in the payload and nothing on disk — nothing to check
fi

# Write the subject text to a scratch file so the checks below can keep using
# plain `grep <file>` exactly as before — the fix is WHAT gets grepped
# (proposed content, not the on-disk file), not the grep mechanics themselves.
subject_file="$(mktemp)"
trap 'rm -f "$subject_file"' EXIT
printf '%s' "$subject_text" >"$subject_file"

# Lowercased basename for pattern matching — routing only (which checks apply
# to this file extension/name), never the thing that gets grepped.
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
    if grep -niE '(api[_-]?key|secret[_-]?key|jwt[_-]?signing[_-]?key|client[_-]?secret|access[_-]?token|password|refresh[_-]?token|bearer)\s*[:=]\s*["'"'"'][a-z0-9_-]{16,}["'"'"']' "$subject_file" 2>/dev/null | grep -viE '(process\.env|os\.getenv|env\[|env\.|"\$\{|"<.*placeholder.*>"|"<your[_ -]|"\.\.\.|<<|YOUR_|REPLACE_ME|TODO|FILL_IN)' >/dev/null; then
      violations+=("Inline secret detected — credentials should come from environment variables, not source. (rule 1)")
    fi
    # Postgres connection strings with embedded passwords
    if grep -niE 'postgres(ql)?://[a-z0-9_.-]+:[a-z0-9!@#$%^&*_+=-]{4,}@' "$subject_file" 2>/dev/null | grep -viE '(process\.env|os\.getenv|<|\.\.\.|YOUR_|REPLACE)' >/dev/null; then
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
    if grep -niE 'create\s+table[^;]+tenant_id\b' "$subject_file" 2>/dev/null >/dev/null; then
      # ...and does NOT enable row level security anywhere in the same file
      if ! grep -niE 'enable\s+row\s+level\s+security' "$subject_file" 2>/dev/null >/dev/null; then
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
    if grep -niE 'expires?in\s*[:=]\s*["'"'"']?([2-9][0-9]+m|[1-9][0-9]*h|[1-9][0-9]*d)' "$subject_file" 2>/dev/null >/dev/null; then
      # Filter out reasonable values: 5m, 10m, 15m, 20m, 25m, 30m
      if grep -niE 'expires?in\s*[:=]\s*["'"'"']?((3[1-9]m)|([4-9][0-9]m)|([0-9]{3,}m)|([1-9][0-9]*h)|([1-9][0-9]*d))' "$subject_file" 2>/dev/null >/dev/null; then
        violations+=("JWT expiresIn appears to be >30 minutes. Short-lived tokens (5-15 min) are the standard. (rule 3)")
      fi
    fi
    # Also: numeric seconds > 1800
    if grep -niE 'exp\s*[:=]\s*(now\s*\(\s*\)\s*[+]\s*|Date\.now\s*\(\s*\)\s*[+]\s*)?[0-9]{4,}' "$subject_file" 2>/dev/null | grep -vE 'expiresIn|placeholder|comment|example' >/dev/null; then
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
    if grep -niE '\b(looker(\s+embedded)?|tableau\s+embedded|sigma\s+(computing|deployment)|metabase\s+pro\s+interactive)\b' "$subject_file" 2>/dev/null >/dev/null; then
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

# Print warnings to stderr (terminal-visible).
{
  echo ""
  echo "[data-platform-smells] Advisory warnings for ${file}:"
  for v in "${violations[@]}"; do
    echo "  - ${v}"
  done
  echo ""
  echo "  These are advisory by default. Set DATA_PLATFORM_STRICT=1 to make them blocking."
  echo "  See plugins/data-platform/CLAUDE.md §3, §4 for the rules."
  echo ""
} >&2

# Also emit an inline additionalContext envelope on stdout — self-contained,
# zero cross-plugin dependency (no _advise.sh reference: data-platform can be
# installed without ravenclaude-core, and a hard-coded path into that
# plugin's version-keyed cache would break on every ravenclaude-core bump).
# A stderr-at-exit-0 line does NOT reach the model on its own; this is what
# actually delivers the warning into the agent's context on the advisory
# (non-STRICT) path. The banner self-identifies the text as a local hook
# notice so it cannot be mistaken for an injection attempt — mirrors
# _advise.sh's own documented reasoning for why an unlabelled advisory gets
# discounted by the model.
DP_SMELL_FILE="$file" DP_SMELL_VIOLATIONS="$(printf '%s\n' "${violations[@]}")" python3 -c '
import json, os
banner = "[data-platform-smells guard notice — emitted locally by a plugin hook, not by the user and not by the tool]"
file_path = os.environ.get("DP_SMELL_FILE", "")
violations = os.environ.get("DP_SMELL_VIOLATIONS", "")
msg = "Advisory warnings for %s:\n%s\nSet DATA_PLATFORM_STRICT=1 to make these blocking. See plugins/data-platform/CLAUDE.md sections 3 and 4." % (file_path, violations)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": banner + "\n" + msg}}))
' 2>/dev/null || true

# Exit 0 for advisory; exit 2 = BLOCK if strict mode is set (Claude Code
# PreToolUse blocking code; exit 1 is non-blocking and would silently allow).
if [[ "${DATA_PLATFORM_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
