#!/usr/bin/env bash
# check-pt-documentation-smells.sh — advisory PreToolUse hook for the physical-therapy-rehab-clinic plugin.
# Flags mechanically-detectable PT/rehab documentation smells on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set PTCLINIC_STRICT=1 to make it blocking (exit 2).
# ADVISORY ONLY — not clinical, legal, or billing advice. It does not read or store PII.
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

# Only inspect note/plan text files where these patterns are meaningful.
case "$file" in
  *.md|*.txt) ;;
  *) exit 0 ;;
esac

findings=()

# 1. Timed-treatment minutes recorded but no unit count anywhere in the file.
#    Look for a "<n> min(utes)" near treatment minutes; flag if no "unit(s)" appears.
if grep -nEi '([0-9]+)[[:space:]]*(min|mins|minute|minutes)\b' "$file" >/dev/null 2>&1; then
  if ! grep -nEi '\b[0-9]+[[:space:]]*units?\b|\bunits?[[:space:]]*[:=]' "$file" >/dev/null 2>&1; then
    findings+=("Timed treatment minutes are recorded but no unit count appears — apply the 8-minute rule and state the units (see therapy-billing-and-units).")
  fi
fi

# 2. "patient tolerated (treatment) well" boilerplate with no skilled-care justification.
if grep -nEi 'tolerated[[:space:]]+(the[[:space:]]+)?(treatment|session|exercises?|activity)?[[:space:]]*well' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'skilled|clinical[[:space:]]+(reasoning|decision)|progress(ed|ion)?|cue(d|ing|s)?|medical[[:space:]]+necessity|because|in[[:space:]]+order[[:space:]]+to' "$file" >/dev/null 2>&1; then
    findings+=("\"tolerated well\" boilerplate with no skilled-care justification — name the clinical decision-making/progression that required a licensed therapist (see defensible-documentation).")
  fi
fi

# 3. A plan-of-care file with no certification / recertification / review date.
if grep -nEi 'plan[[:space:]]+of[[:space:]]+care|\bPOC\b' "$file" >/dev/null 2>&1; then
  if ! grep -nEi 'certif(y|ied|ication)|recertif(y|ied|ication)|re-?cert|review[[:space:]]+date|cert(ification)?[[:space:]]+date' "$file" >/dev/null 2>&1; then
    findings+=("A plan of care with no certification / recertification / review date — track the cert clock so it doesn't lapse (see plan-of-care-management).")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── physical-therapy-rehab-clinic advisory (not clinical/billing advice): review before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${PTCLINIC_STRICT:-0}" = "1" ]; then
  echo "(blocking: PTCLINIC_STRICT=1)" >&2
  exit 2
fi
exit 0
