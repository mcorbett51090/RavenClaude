#!/usr/bin/env bash
# check-localization-i18n-anti-patterns.sh — advisory PreToolUse hook for the localization-i18n plugin.
# Flags mechanically-detectable i18n anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set I18N_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. 2-form plural logic — English-only branching the translator should own via ICU plural.
if grep -qE "\b(count|n|num|len|length|qty|quantity)\s*===?\s*1\s*\?" "$file" 2>/dev/null \
  || grep -qiE "===?\s*1\s*\?.*(singular|plural)|\bn\s*>\s*1\b.*plural" "$file" 2>/dev/null; then
  findings+=("Looks like 2-form plural logic (n === 1 ? ...). CLDR defines up to 6 plural categories — use ICU plural/select so the translator owns the grammar.")
fi

# 2. Concatenating a translated/interpolated fragment into a sentence — word order varies per language.
if grep -qE "(t\(|i18n|translate|gettext|__\()" "$file" 2>/dev/null \
  && grep -qE "(\"[^\"]* \"\s*\+|\+\s*\"[^\"]+ \")|'[^']* '\s*\+|\+\s*'[^']+ '" "$file" 2>/dev/null; then
  findings+=("String concatenation around translatable text — never build a sentence from fragments. Use one ICU message with named placeholders.")
fi

# 3. Hand-rolled date/number formatting instead of Intl/CLDR.
if grep -qiE "(MM/DD/YYYY|DD/MM/YYYY|YYYY-MM-DD)" "$file" 2>/dev/null \
  || grep -qE "\.toLocaleString\(\)\s*//.*hardcode" "$file" 2>/dev/null \
  || grep -qiE "(strftime\(['\"]%m/%d|moment\([^)]*\)\.format\(['\"]MM/DD)" "$file" 2>/dev/null; then
  findings+=("Hardcoded date/number format detected — read formats from CLDR via Intl (DateTimeFormat/NumberFormat), never hand-roll a locale-specific format.")
fi

# 4. Physical CSS in a file that also references RTL/dir — should use logical properties.
if grep -qiE "(dir\s*=\s*[\"']?rtl|direction\s*:\s*rtl|\[dir=rtl\]|rtl)" "$file" 2>/dev/null; then
  if grep -qiE "(margin-left|margin-right|padding-left|padding-right|text-align\s*:\s*(left|right)|left\s*:|right\s*:)" "$file" 2>/dev/null; then
    findings+=("Physical CSS (margin-left / text-align: left) in a file that handles RTL — use logical properties (margin-inline-start, text-align: start) so the layout mirrors automatically.")
  fi
fi

# 5. A locale catalog/config that declares locales but no fallback — a missing string renders a raw key.
if printf '%s' "$file" | grep -qiE "(i18n|locale|translation).*\.(json|ya?ml|js|ts)$" 2>/dev/null \
  && grep -qiE "(supportedLngs|locales|languages)\s*[:=]" "$file" 2>/dev/null; then
  if ! grep -qiE "(fallbackLng|fallback|defaultLocale|fallbackLocale)" "$file" 2>/dev/null; then
    findings+=("Locale config with no fallback chain — define fallbackLng/fallback (e.g. pt-BR -> pt -> en) so a missing string falls back instead of rendering a raw key.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── localization-i18n advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${I18N_STRICT:-0}" = "1" ]; then
  echo "(blocking: I18N_STRICT=1)" >&2
  exit 2
fi
exit 0
