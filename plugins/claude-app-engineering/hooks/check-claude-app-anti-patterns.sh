#!/usr/bin/env bash
# check-claude-app-anti-patterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on Claude-app source files
# (.py/.ts/.js/.tsx/.jsx). Flags four mechanically-detectable violations of the
# claude-app-engineering team constitution (see plugins/claude-app-engineering/CLAUDE.md §3):
#
#   1. A hardcoded sk-ant- API key literal — secrets never in code (#8). [security]
#   2. A messages.create / .messages.stream call in a file with NO max_tokens
#      anywhere — silent-truncation / overspend risk (#11).
#   3. A retired model id (claude-2 / claude-instant / claude-1) — pin a current 4.x (#11).
#   4. Full-message logging (print(messages / console.log(messages / logger.*(messages)
#      — never log full prompts; secret/PII leak (#8).
#
# Advisory by default: prints to stderr, exits 0. Set CLAUDE_APP_STRICT=1 to block.
# Model-version-coupled checks (adaptive-thinking params, temperature+thinking) live
# in the knowledge bank, not here — they rot monthly.

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
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

case "$base_lc" in
  *.py | *.ts | *.js | *.tsx | *.jsx) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: hardcoded sk-ant- API key literal --- (#8, security)
if grep -Eni 'sk-ant-[a-z0-9_-]{8,}' "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    violations+=("  [hardcoded-api-key] $file: $line — move the key to an env var / secret manager; never commit sk-ant- literals (CLAUDE.md §3 #8).")
  done < <(grep -Eni 'sk-ant-[a-z0-9_-]{8,}' "$file" | head -3)
fi

# --- Check 2: messages.create / .messages.stream with no max_tokens in the file --- (#11)
if grep -Eni '\.messages\.(create|stream)\b|client\.messages\.|anthropic\.messages\.' "$file" >/dev/null 2>&1; then
  if ! grep -Eni 'max_tokens|maxTokens' "$file" >/dev/null 2>&1; then
    violations+=("  [no-max-tokens] $file calls the Messages API but sets no max_tokens anywhere — risks silent truncation + overspend (CLAUDE.md §3 #11).")
  fi
fi

# --- Check 3: retired model id --- (#11)
if grep -Eni '"(claude-2|claude-instant|claude-1)[^"]*"|'\''(claude-2|claude-instant|claude-1)[^'\'']*'\''' "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    violations+=("  [retired-model] $file: $line — pin a current 4.x model (Opus 4.8 / Sonnet 4.6 / Haiku 4.5); claude-2/instant/1 are retired (CLAUDE.md §3 #11).")
  done < <(grep -Eni '(claude-2|claude-instant|claude-1)' "$file" | head -3)
fi

# --- Check 4: full-message logging --- (#8)
if grep -Eni '(print|console\.(log|info|debug|warn|error)|logger\.[a-z]+|logging\.[a-z]+)[[:space:]]*\([^)]*\bmessages\b' "$file" >/dev/null 2>&1; then
  while IFS= read -r line; do
    violations+=("  [full-message-logging] $file: $line — don't log full prompts/messages; redact (secret/PII leak) (CLAUDE.md §3 #8).")
  done < <(grep -Eni '(print|console\.(log|info|debug|warn|error)|logger\.[a-z]+|logging\.[a-z]+)[[:space:]]*\([^)]*\bmessages\b' "$file" | head -3)
fi

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Claude-app anti-pattern check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/claude-app-engineering/CLAUDE.md §3 (house opinions). This
  hook is advisory — the edit was not blocked. Set CLAUDE_APP_STRICT=1
  to make violations blocking.
────────────────────────────────────────────────────────────────────

EOF
  if [[ "${CLAUDE_APP_STRICT:-0}" == "1" ]]; then
    # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is a non-blocking
    # error Claude Code silently swallows, so STRICT would not actually block the edit.
    exit 2
  fi
fi

exit 0
