#!/usr/bin/env bash
# check-localization-i18n-engineering-anti-patterns.sh — advisory PreToolUse hook for the
# localization-i18n-engineering plugin. Flags mechanically-detectable i18n/l10n anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set L10N_I18N_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect source and config files where i18n bugs live; skip binaries and lockfiles.
case "$file" in
*.js | *.jsx | *.ts | *.tsx | *.mjs | *.cjs) ;;
*.py | *.java | *.kt | *.swift | *.dart) ;;
*.vue | *.svelte | *.html | *.htm) ;;
*.rb | *.php | *.go) ;;
*) exit 0 ;;
esac

findings=()

# ──────────────────────────────────────────────────────────────────────────────
# Check 1: Hard-coded user-facing string — a string literal used directly in a
# render/return/setText/display position instead of routing through a t() call.
# Heuristic: string literal assigned to a JSX attribute that typically holds
# display text, or returned directly in JSX text position.
# ──────────────────────────────────────────────────────────────────────────────
if grep -nE '(return|setText|setTitle|setPlaceholder|setLabel|setMessage|aria-label=|placeholder=|title=|alt=)\s*[\("]([A-Z][a-z ]{4,}[a-zA-Z .!?]*)[")\)]' "$file" >/dev/null 2>&1; then
  findings+=("Possible hard-coded user-facing string — user-visible text should be externalized via t(), i18n.t(), <FormattedMessage>, intl.formatMessage(), or equivalent. Hard-coded strings cannot be translated.")
fi

# ──────────────────────────────────────────────────────────────────────────────
# Check 2: String concatenation used to build a user-facing sentence.
# Pattern: string literal + variable + string literal (suggests sentence assembly).
# ──────────────────────────────────────────────────────────────────────────────
if grep -nE '"[A-Za-z ]+"\s*\+\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*\+\s*"[A-Za-z ]*"' "$file" >/dev/null 2>&1; then
  findings+=("String concatenation used to build a sentence ('prefix' + variable + 'suffix') — this produces untranslatable fragments. Use a single ICU MessageFormat message with named parameters: {\"key\": \"Hello {name}, you have {count, plural, one{# message} other{# messages}}\"}.")
fi

# Also catch template-literal sentence assembly: \`Hello ${name}!\`  where the template
# literal starts or ends with a non-trivial English word sequence.
if grep -nE '`[A-Z][a-z]+ \$\{[^}]+\}' "$file" >/dev/null 2>&1; then
  findings+=("Template literal used to build a user-facing sentence (\`Hello \${name}\`) — use a single ICU MessageFormat message with a named parameter instead of embedding variables in a template literal.")
fi

# ──────────────────────────────────────────────────────────────────────────────
# Check 3: Plural handled with if count == 1 (English-only plural logic).
# This pattern is incorrect for Arabic (6 forms), Russian (3+), Polish (4), etc.
# ──────────────────────────────────────────────────────────────────────────────
if grep -nE '(if|ternary|\?)\s*\(?[a-zA-Z_$][a-zA-Z0-9_$.]*\s*[=!]=+\s*1\s*\)?\s*([\{?]|then)' "$file" >/dev/null 2>&1 && \
   grep -nE '(count|num|length|size|total|qty|quantity)\s*[=!]=+\s*1' "$file" >/dev/null 2>&1; then
  findings+=("Plural handled with 'if count == 1' — this is correct only for English. Arabic has 6 plural categories; Russian and Polish have 3-4. Use ICU MessageFormat: {count, plural, one{# item} other{# items}}. Consult CLDR plural rules: https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html")
fi

# ──────────────────────────────────────────────────────────────────────────────
# Check 4: Hard-coded date/number/currency format.
# Patterns: toLocaleDateString/toLocaleString without a locale arg;
# hard-coded format strings like "MM/DD/YYYY"; hard-coded currency symbols.
# ──────────────────────────────────────────────────────────────────────────────

# 4a: toLocaleDateString() or toLocaleString() with no arguments (uses platform default locale)
if grep -nE '\.(toLocaleDateString|toLocaleString|toLocaleTimeString)\(\s*\)' "$file" >/dev/null 2>&1; then
  findings+=("toLocaleDateString() / toLocaleString() called without a locale argument — this uses the platform default locale, not the user's locale. Pass the explicit locale: date.toLocaleDateString(locale, options) or use new Intl.DateTimeFormat(locale, options).format(date).")
fi

# 4b: Hard-coded date format strings
if grep -nEi '(["'"'"'`])(MM[/\-.]DD[/\-.]YYYY|DD[/\-.]MM[/\-.]YYYY|YYYY[/\-.]MM[/\-.]DD|yyyy[/\-.]MM[/\-.]dd)\1' "$file" >/dev/null 2>&1; then
  findings+=("Hard-coded date format string (e.g. 'MM/DD/YYYY') — date formats are locale-specific. Use CLDR date skeletons via Intl.DateTimeFormat or ICU MessageFormat date skeleton: {date, date, ::yMMMd}.")
fi

# 4c: Hard-coded currency symbols as string literals
if grep -nE '"(\\\$|€|£|¥|₩|₹|₽|¢)"' "$file" >/dev/null 2>&1; then
  findings+=("Hard-coded currency symbol (\$, €, £, etc.) as a string literal — use Intl.NumberFormat(locale, { style: 'currency', currency: 'USD' }) or ICU number skeleton: {amount, number, ::currency/USD sign-accounting}.")
fi

# ──────────────────────────────────────────────────────────────────────────────
# Report findings
# ──────────────────────────────────────────────────────────────────────────────
if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── localization-i18n-engineering advisory: i18n anti-patterns detected ──" >&2
for f in "${findings[@]}"; do
  printf "  • %s\n" "$f" >&2
done
printf "%s\n" "── See plugins/localization-i18n-engineering/best-practices/ for the rules ──" >&2

if [ "${L10N_I18N_STRICT:-0}" = "1" ]; then
  echo "(blocking: L10N_I18N_STRICT=1)" >&2
  exit 2
fi
exit 0
