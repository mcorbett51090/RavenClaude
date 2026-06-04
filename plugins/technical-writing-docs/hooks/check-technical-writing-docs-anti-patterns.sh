#!/usr/bin/env bash
# check-technical-writing-docs-anti-patterns.sh — advisory PreToolUse hook for the technical-writing-docs plugin.
# Flags mechanically-detectable anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DOCS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()
if grep -nEi "(TODO|TBD|FIXME|coming soon|lorem ipsum|XXX)" "$file" >/dev/null 2>&1; then
  findings+=("Placeholder text in docs (TODO/TBD/coming soon/lorem) — ship complete content or omit the section; placeholders erode trust.")
fi
if grep -nEi "(localhost:[0-9]+|127\\.0\\.0\\.1|YOUR_API_KEY|example\\.com/api)(?![\\s\\S]{0,40}#\\s*example)" "$file" >/dev/null 2>&1; then
  findings+=("Hardcoded localhost/placeholder in a doc example — ensure the example is runnable or clearly marked as a placeholder to fill in.")
fi
if grep -nEi "\\b(click here|read more|this link)\\b" "$file" >/dev/null 2>&1; then
  findings+=("Non-descriptive link text ('click here'/'read more') — use descriptive link text for accessibility and scannability.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── technical-writing-docs advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DOCS_STRICT:-0}" = "1" ]; then
  echo "(blocking: DOCS_STRICT=1)" >&2
  exit 2
fi
exit 0
