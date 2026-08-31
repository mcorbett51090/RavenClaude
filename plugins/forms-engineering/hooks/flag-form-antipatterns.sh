#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the forms-engineering plugin.
#
# Flags anti-patterns for rules THIS plugin owns. It deliberately does NOT
# detect placeholder-as-only-label, an asterisk on a required field, or
# type="text" on an email/tel input: those are owned by web-design, and a second
# enforcement home for someone else's rule is rubric drift wearing a hook's
# clothes.
#
# Advisory by default — set FORMS_STRICT=1 to make it blocking (exit 2).
#
# Portability floor: bash 3.2, BSD grep (no -P), no GNU timeout, no sed -i.

FILE="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives via
# the canonical stdin JSON contract. Fall back to it — the same dual-source
# pattern the core file hooks use.
if [ -z "$FILE" ] && [ ! -t 0 ] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    FILE="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.html | *.htm | *.jsx | *.tsx | *.js | *.ts | *.vue | *.svelte | *.astro | *.php | *.py | *.rb | *.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${FORMS_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "forms-engineering" "$1" >&2
  findings=$((findings + 1))
}

# 1. A honeypot that assistive tech or autofill can reach. All three properties
#    are required; any one missing is a silent-rejection mechanism aimed at real
#    users. (best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md)
if grep -Eiq 'honeypot|honey-pot' "$FILE"; then
  if ! grep -Eiq 'aria-hidden' "$FILE" ||
    ! grep -Eiq 'tabindex="?-1' "$FILE" ||
    ! grep -Eiq 'autocomplete="?off' "$FILE"; then
    note "A honeypot appears without all three of aria-hidden, tabindex=\"-1\" and autocomplete=\"off\" — a screen reader or a password manager will fill it and the submission is silently rejected. Count the rejections too."
  fi
fi

# 2. A challenge widget introduced with no server-side verification in the same
#    change. The MECHANICS are owned by ravenclaude-core — this message cites
#    them, it does not restate them.
if grep -Eiq 'cf-turnstile|g-recaptcha|h-captcha|hcaptcha|data-sitekey' "$FILE"; then
  if ! grep -Eiq 'siteverify|verify.?token|challenge.?verif' "$FILE"; then
    note "A challenge widget appears with no server-side verification in the same file — a token that is never verified is decoration. The mechanics (lifetime, replay, verification endpoint) are owned by plugins/ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md; read it rather than reimplementing."
  fi
fi

# 3. A form POST handler with no duplicate guard. Anti-forgery is not
#    anti-duplicate. (best-practices/every-public-form-post-needs-a-double-submit-guard.md)
if grep -Eiq 'method="?post|\.post\(|function +POST|request\.method *[=!]= *"?POST' "$FILE"; then
  if ! grep -Eiq 'idempot|dedup|de-dup|double.submit|submission.?token|already.?submitted|one.?shot' "$FILE"; then
    note "A form POST path appears with no duplicate-submission guard — CSRF protection is anti-forgery, not anti-duplicate. A double-click, a retry or a back button will produce two of whatever this creates."
  fi
fi

# 4. A form rate quoted with no denominator named.
#    (best-practices/name-the-denominator-before-you-quote-a-completion-rate.md)
if grep -Eiq '(completion|abandonment) rate|conversion rate on the form' "$FILE"; then
  if ! grep -Eiq 'denominator|form start|per start|per session|of starts|first interaction' "$FILE"; then
    note "A form rate is quoted with no denominator named — page views, form starts and eligible sessions do not agree, and the gap is usually larger than the improvement being argued about. Print the denominator next to the figure."
  fi
fi

# 5. Three-sigma limits on a form series with no minimum-n statement.
#    (best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md)
if grep -Eiq '3.?sigma|three.?sigma|control limit|\bUCL\b|\bLCL\b' "$FILE"; then
  if grep -Eiq 'form|abandonment|completion|submission' "$FILE"; then
    if ! grep -Eiq '20 individual observations|charting floor|minimum of 20' "$FILE"; then
      note "Control limits are applied to a form series with no minimum-n statement — form series are low-volume and autocorrelated by weekday and campaign, so three-sigma limits below 20 individual observations manufacture false special-cause signals. State the floor, or do not chart."
    fi
  fi
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "forms-engineering: $findings advisory finding(s); FORMS_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
