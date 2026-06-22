#!/usr/bin/env bash
# flag-devrel-antipatterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on developer-relations artifact
# files (.md). Flags four mechanically-detectable violations of the DevRel team
# constitution (see plugins/developer-relations/CLAUDE.md):
#
#   1. A getting-started doc with NO first-success milestone / TTFS framing
#      (time-to-first-success-is-the-metric.md)
#   2. Sample/code content with a HARDCODED secret (api key / token literal)
#      (sample-code-is-production-code.md)
#   3. Sample/code content that SWALLOWS errors (empty catch / pass on except)
#      (sample-code-is-production-code.md)
#   4. A content/calendar doc with NO activation goal — demand-gen drift
#      (devrel-is-not-demand-gen.md)
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set DEVREL_STRICT=1 to make
# violations blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to the
# agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect markdown artifacts.
case "$base_lc" in
  *.md) : ;;
  *) exit 0 ;;
esac

content_lc=$(tr '[:upper:]' '[:lower:]' < "$file" 2>/dev/null || true)
[[ -z "$content_lc" ]] && exit 0

warnings=()

# --- Check 1: getting-started doc with no first-success milestone ------------
if printf '%s' "$base_lc" | grep -Eq 'getting-started|getting_started|quickstart|onboard'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'first success|first-success|time.to.first|first api call|first call|you did it|works?\b'; then
    warnings+=("Getting-started content with no first-success milestone / TTFS framing — anchor on one explicit, early 'you did it' moment; time-to-first-success is the metric (time-to-first-success-is-the-metric.md).")
  fi
fi

# --- Check 2: hardcoded secret in sample/code content -----------------------
# Look for an assignment of an api-key/token/secret to a quoted literal that is
# NOT an env-var reference or an obvious placeholder.
if grep -Eiq '(api[_-]?key|secret|token|password|bearer)["'"'"' ]*[:=][[:space:]]*["'"'"'][^"'"'"'<$]{6,}' "$file" 2>/dev/null; then
  if ! printf '%s' "$content_lc" | grep -Eq 'your[_-]?key|placeholder|example|getenv|environ|process\.env|os\.environ|<.*>|\$\{'; then
    warnings+=("Possible hardcoded secret/API-key literal in sample content — sample code is copied verbatim; use env vars / a secret manager, never a literal key (sample-code-is-production-code.md).")
  fi
fi

# --- Check 3: swallowed errors in sample/code content -----------------------
if grep -Eq 'catch[[:space:]]*\([^)]*\)[[:space:]]*\{[[:space:]]*\}|except[[:space:]]*:[[:space:]]*pass|catch[[:space:]]*\{[[:space:]]*\}' "$file" 2>/dev/null; then
  warnings+=("Sample code appears to swallow errors (empty catch / 'except: pass') — show real failure modes (rate limit, auth expiry, bad input) and handle them; sample code is production code (sample-code-is-production-code.md).")
fi

# --- Check 4: content/calendar doc with no activation goal ------------------
if printf '%s' "$base_lc" | grep -Eq 'content|calendar'; then
  if ! printf '%s' "$content_lc" | grep -Eq 'activation|first success|funnel|retention|ttfs|goal'; then
    warnings+=("Content/calendar with no activation goal — every item names which funnel step it moves; DevRel measures activation, not reach/MQLs (devrel-is-not-demand-gen.md).")
  fi
fi

[[ ${#warnings[@]} -eq 0 ]] && exit 0

{
  echo "⚠️  developer-relations advisory — $(basename "$file"):"
  for w in "${warnings[@]}"; do
    echo "   • $w"
  done
} >&2

if [[ "${DEVREL_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
