#!/usr/bin/env bash
# check-eyecare-billing-smells.sh — advisory PreToolUse hook for the optometry-eyecare-practice plugin.
# Flags mechanically-detectable eye-care operations/billing smells on Edit/Write/MultiEdit of .md/.txt
# files. Advisory by default (exit 0, prints a notice); set EYECARE_STRICT=1 to make it blocking (exit 2).
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
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect prose files where these patterns are meaningful.
case "$file" in
  *.md|*.txt) ;;
  *) exit 0 ;;
esac

findings=()

# 1. A claim / encounter note that mentions a refraction but never names a medical-vs-vision route.
if grep -nEi 'refract(ion|ed|ive)|chief complaint|encounter note|exam (note|finding)' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'medical|vision plan|vision-plan|vision benefit|route|routing|payor|payer' "$file" >/dev/null 2>&1; then
    findings+=("A refraction / encounter note with no medical-vs-vision routing noted — route the visit deliberately on the chief complaint (see medical-vs-vision-billing).")
  fi
fi

# 2. A recall / recare plan with no interval named.
if grep -nEi 'recall|recare|reactivat' "$file" >/dev/null 2>&1; then
  if ! grep -nEi '[0-9]+[[:space:]]*(month|mo|week|wk|year|yr|day)|annual|interval|cadence' "$file" >/dev/null 2>&1; then
    findings+=("A recall/recare plan with no interval — set the recall interval by exam type (clinical-protocol driven; verify-at-use).")
  fi
fi

# 3. A billing doc citing a payor rule / CPT / benefit with no date or verify-at-use flag.
if grep -nEi 'cpt|payor|payer|vision plan|vision-plan|benefit|allowance|covered|denial|claim' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'verify-at-use|retrieved|as of|20[0-9]{2}-[0-9]{2}|20[0-9]{2}|\[estimate\]' "$file" >/dev/null 2>&1; then
    findings+=("A payor/coding/benefit reference with no retrieval date or verify-at-use flag — payor and coding specifics are volatile; add a date + [verify-at-use].")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── optometry-eyecare-practice advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${EYECARE_STRICT:-0}" = "1" ]; then
  echo "(blocking: EYECARE_STRICT=1)" >&2
  exit 2
fi
exit 0
