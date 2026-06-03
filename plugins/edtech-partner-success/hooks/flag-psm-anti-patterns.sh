#!/usr/bin/env bash
# flag-psm-anti-patterns.sh
# PostToolUse hook for Edit | Write | MultiEdit on EdTech-PSM artifact files.
# Flags the most common mechanically-detectable violations of the EdTech-PSM
# team constitution (see plugins/edtech-partner-success/CLAUDE.md §3, §4):
#
#   1. Action item without a date — files matching *qbr*, *success-plan*,
#      *touchpoint*, *escalation* with a bullet/checkbox that looks like an
#      action item but lacks a YYYY-MM-DD reference (§3 #13)
#   2. Generic boilerplate ("we value your partnership", "just checking in",
#      "circling back", "touching base") — same artifact set (§3 #11)
#   3. Unverified numeric claim — number followed by "%" or "x" or "users" /
#      "students" with no source/baseline reference within ±2 lines (§3 #12)
#   4. Multiple partner names visible in a To: line — files matching *email*,
#      *broadcast*, *comms* (§4 anti-pattern)
#   5. Health-score status (red / yellow) without named signals — files
#      matching *health*, *qbr* (§3 #4 — cite the signal)
#
# Advisory by default: prints warnings to stderr so Claude and the user both see
# them, but exits 0 so the edit is not blocked. To make this hook BLOCK on
# violation, change the final `exit 0` to `exit 2` (or set
# EDTECH_PS_STRICT=1 in the environment).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed). STRICT=1 below
# uses exit 2 — the only blocking code.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Lowercased basename for pattern matching.
base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

violations=()

# --- Check 1: action item without a date ---
# An action-item line looks like a bullet/checkbox that starts with a verb-like
# token. We flag it if no YYYY-MM-DD substring appears on the same line.
# Heuristic: skip lines that obviously aren't actions ("see X", "per Y").
case "$base_lc" in
  *qbr*|*success-plan*|*touchpoint*|*escalation*|*onboarding-checklist*|*annual-partner-review*)
    while IFS= read -r line; do
      # Match: leading whitespace, then - [ ] or - or 1. and at least one word
      if [[ "$line" =~ ^[[:space:]]*(-[[:space:]]\[[[:space:]xX]\]|-|[0-9]+\.)[[:space:]]+[A-Za-z] ]]; then
        # Skip template placeholders (lines containing literal angle-bracket placeholders).
        [[ "$line" =~ \<[^\>]+\> ]] && continue
        # Skip "see X" / "per Y" / "ref:" / "note:" prose bullets.
        if [[ "$line" =~ [Ss]ee[[:space:]]|[Pp]er[[:space:]]|[Rr]ef:|[Nn]ote: ]]; then continue; fi
        # Skip lines containing a YYYY-MM-DD-shaped substring.
        if [[ "$line" =~ [0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then continue; fi
        # Skip empty checkbox lines (template scaffolding).
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]\[[[:space:]xX]\][[:space:]]+\` ]]; then continue; fi
        violations+=("  [action-without-date] $file: action item missing YYYY-MM-DD: $line")
      fi
    done < "$file"
    ;;
esac

# --- Check 2: generic boilerplate ---
case "$base_lc" in
  *qbr*|*success-plan*|*touchpoint*|*escalation*|*email*|*broadcast*|*comms*|*annual-partner-review*)
    boilerplate_pattern='we value your partnership|just checking in|circling back|touching base'
    if grep -EniI "$boilerplate_pattern" "$file" >/dev/null 2>&1; then
      sample=$(grep -EniI "$boilerplate_pattern" "$file" | head -1)
      violations+=("  [generic-boilerplate] $file uses boilerplate phrasing. Replace with substantive language; partners notice form-letters. Match: $sample")
    fi
    ;;
esac

# --- Check 3: unverified numeric claim ---
# A numeric claim looks like a number+% or number+x or "N students" / "N users"
# / "N teachers" / "N seats". We flag if no "source", "query", "baseline",
# "range", "vs", "compared", "since" appears within ±2 lines.
case "$base_lc" in
  *qbr*|*annual-partner-review*|*health*)
    while IFS=':' read -r line_num content; do
      # Skip lines containing a source-or-baseline-keyword.
      if echo "$content" | grep -qiE 'source|query|baseline|range|vs[[:space:]]|compared|since|\(20[0-9]{2}-'; then continue; fi
      # Skip template-placeholder lines.
      [[ "$content" =~ \<[^\>]+\> ]] && continue
      # Skip lines that are clearly schema headers (column headers).
      if echo "$content" | grep -qE '^\|.*\|$'; then continue; fi
      violations+=("  [unverified-claim] $file:$line_num: numeric claim with no source/baseline within line: $content")
    done < <(grep -EnI '\b[0-9]+(\.[0-9]+)?%|\b[0-9]+(\.[0-9]+)?x\b|\b[0-9]+[[:space:]]+(student|teacher|user|seat|partner)s?\b' "$file" 2>/dev/null | head -5)
    ;;
esac

# --- Check 4: multiple partner names in a To: line ---
# Heuristic: a line beginning with "To:" or "to:" that contains 2+ named-entity
# tokens (capital-cased multi-word strings) separated by commas or semicolons.
case "$base_lc" in
  *email*|*broadcast*|*comms*)
    while IFS= read -r line; do
      # Count comma- or semicolon-separated tokens that look like names/orgs.
      tokens=$(echo "$line" | tr ',;' '\n' | grep -cE '^[[:space:]]*[A-Z][A-Za-z]+([[:space:]]+[A-Z][A-Za-z]+)*[[:space:]]*$' || true)
      if [[ "$tokens" -ge 2 ]]; then
        violations+=("  [multi-partner-to-line] $file: multiple partner / school / district names appear visible in a To: line — use BCC or per-partner sends. Line: $line")
      fi
    done < <(grep -EniI '^[[:space:]]*to:[[:space:]]' "$file" 2>/dev/null | head -3)
    ;;
esac

# --- Check 5: health-score status without named signals ---
# Pattern: line mentioning "red" or "yellow" status (e.g., "status: red",
# "color: yellow") without "signal", "driver", "component", "because",
# or a colon-followed-list of components within the same paragraph.
case "$base_lc" in
  *health*|*qbr*)
    if grep -EniI '\b(red|yellow)\b' "$file" 2>/dev/null | head -10 | while read -r line; do
      # Heuristic: same line must mention signal/driver/component/because, OR
      # the line must contain a colon followed by content (suggesting a list of components).
      if echo "$line" | grep -qiE 'signal|driver|component|because|cited|caused|due[[:space:]]+to|:[[:space:]]+[A-Za-z]'; then
        :
      else
        # Skip template placeholders.
        if echo "$line" | grep -qE '\<[^\>]+\>'; then continue; fi
        # Skip headers and table-row separators.
        if echo "$line" | grep -qE '^[[:space:]]*\|.*\|$|^[[:space:]]*#'; then continue; fi
        echo "  [health-status-no-signals] $file: red/yellow status without named signals: $line"
      fi
    done | head -3 | grep -q .; then
      while IFS= read -r vline; do violations+=("$vline"); done < <(grep -EniI '\b(red|yellow)\b' "$file" 2>/dev/null | head -10 | while read -r line; do
        if echo "$line" | grep -qiE 'signal|driver|component|because|cited|caused|due[[:space:]]+to|:[[:space:]]+[A-Za-z]'; then :;
        elif echo "$line" | grep -qE '\<[^\>]+\>'; then :;
        elif echo "$line" | grep -qE '^[[:space:]]*\|.*\|$|^[[:space:]]*#'; then :;
        else echo "  [health-status-no-signals] $file: red/yellow status without named signals: $line";
        fi
      done | head -3)
    fi
    ;;
esac

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  EdTech-PSM anti-pattern check flagged ${#violations[@]} potential issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<EOF

  Why this matters: the EdTech-PSM constitution (see plugins/
  edtech-partner-success/CLAUDE.md §3 + §4) treats these patterns as
  partner-trust risks. Boilerplate erodes credibility. Action items
  without dates aren't tracked. Health-score status without signals
  is unconvincing to the partner. Multi-partner emails with visible
  names are a PII / professionalism issue. Unverified claims invite
  pushback.

  This hook is advisory — the edit was not blocked. To enforce, set
  EDTECH_PS_STRICT=1 in your env or change \`exit 0\` to \`exit 2\` at
  the bottom of this script (exit 2 = BLOCK; exit 1 is non-blocking
  and would silently allow the edit).
────────────────────────────────────────────────────────────────────

EOF
  # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is
  # non-blocking and would silently allow the edit despite the warning.
  if [[ "${EDTECH_PS_STRICT:-0}" == "1" ]]; then exit 2; fi
fi

exit 0
