#!/usr/bin/env bash
# flag-email-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on email-related files
# (.html/.mjml/.eml/.py/.js/.ts/.json/.tf/.dns/.zone/.txt). Flags mechanically-
# detectable violations of the email-engineering team constitution (see
# plugins/email-engineering/CLAUDE.md §3/§4 and the knowledge bank):
#
#   1. A DMARC record at p=reject/quarantine with NO rua= (enforcing blind)
#   2. An SPF record using +all (passes every sender — effectively no SPF)
#   3. A likely email-provider API key / SMTP password committed in a file
#   4. A bulk/marketing HTML email with NO List-Unsubscribe header/mention
#
# Advisory by default: prints warnings to stderr but exits 0 (does not block).
# Set EMAIL_ENG_STRICT=1 to make violations blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK with stderr surfaced; exit 1 = silently
# swallowed non-blocking error (so we never use exit 1 for a real finding).

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

# Only inspect email-shaped files.
case "$base_lc" in
  *.html | *.htm | *.mjml | *.eml | *.py | *.js | *.ts | *.json | *.tf | *.dns | *.zone | *.txt) ;;
  *) exit 0 ;;
esac

violations=()

# ---------------------------------------------------------------------------
# Check 1: DMARC p=reject/quarantine with no rua=
# ---------------------------------------------------------------------------
if grep -niEq 'v=DMARC1' "$file" 2>/dev/null; then
  if grep -niEq 'p=\s*(reject|quarantine)' "$file" 2>/dev/null; then
    if ! grep -niEq 'rua=' "$file" 2>/dev/null; then
      violations+=("DMARC at p=reject/quarantine with no rua= aggregate-report address — you're enforcing with zero visibility. Add rua= and verify alignment at p=none first. (CLAUDE.md §3)")
    fi
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: SPF +all
# ---------------------------------------------------------------------------
if grep -niEq 'v=spf1' "$file" 2>/dev/null; then
  if grep -niEq '(^|[[:space:]"])\+all' "$file" 2>/dev/null; then
    violations+=("SPF record uses '+all' — it passes EVERY sender, which is effectively no SPF. Use '~all' (softfail) or '-all' (hardfail).")
  fi
fi

# ---------------------------------------------------------------------------
# Check 3: a likely ESP API key / SMTP secret in the file
# ---------------------------------------------------------------------------
secret_re='SG\.[A-Za-z0-9_-]{16,}|SMTP_PASSWORD\s*[:=]|SENDGRID_API_KEY\s*[:=]\s*["'"'"']?SG\.|postmark[_-]?server[_-]?token\s*[:=]|key-[0-9a-f]{32}'
if grep -niEq "$secret_re" "$file" 2>/dev/null; then
  violations+=("A likely email-provider API key / SMTP secret appears in this file. Keep it in the secret store, never the template/repo. (CLAUDE.md §4)")
fi

# ---------------------------------------------------------------------------
# Check 4: bulk/marketing HTML email with no List-Unsubscribe
# ---------------------------------------------------------------------------
case "$base_lc" in
  *.html | *.htm | *.mjml | *.eml)
    # Heuristic: an email body mentioning newsletter/unsubscribe-context but with
    # no List-Unsubscribe header reference.
    if grep -niEq 'newsletter|marketing|campaign|unsubscribe' "$file" 2>/dev/null; then
      if ! grep -niEq 'list-unsubscribe' "$file" 2>/dev/null; then
        violations+=("This looks like bulk/marketing email but has no List-Unsubscribe reference. Bulk mail needs one-click unsubscribe (RFC 8058). (CLAUDE.md §3)")
      fi
    fi
    ;;
esac

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[email-engineering-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set EMAIL_ENG_STRICT=1 to make them blocking." >&2
echo "  See plugins/email-engineering/knowledge/email-authentication-decision-tree.md for fixes." >&2
echo "" >&2

if [[ "${EMAIL_ENG_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
