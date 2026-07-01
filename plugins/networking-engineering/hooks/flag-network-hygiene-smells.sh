#!/usr/bin/env bash
# flag-network-hygiene-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on networking files.
# Flags two mechanically-detectable violations of the networking-engineering team
# constitution (see plugins/networking-engineering/CLAUDE.md and best-practices/):
#
#   1. A config that trunks "allowed vlan all" — this sprawls the L2 broadcast
#      domain / STP topology across the trunk and defeats deliberate segmentation
#      ("segment by trust boundary, not convenience"; keep L2 blast radius small).
#   2. A change plan / runbook (by filename or by config-apply wording) that names
#      NO rollback path — "no network change without a rollback path."
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set NETENG_STRICT=1 to make
# violations blocking (exit 2).
#
# Patterns use POSIX ERE only (grep -E / -iE) — no PCRE constructs — per the
# check-grep-ere-pcre.py CI gate.
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base=$(basename "$file")
base_lc=$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')

warnings=()

# --- Check 1: trunk allowing all VLANs (L2 blast-radius sprawl) ---
if grep -iqE 'trunk[[:space:]]+allowed[[:space:]]+vlan[[:space:]]+all' "$file"; then
  warnings+=("a trunk allows 'vlan all' — pin an explicit allowed-VLAN list; 'all' sprawls the L2 domain / STP topology and defeats segmentation (best-practices/segment-by-trust-boundary-not-convenience.md).")
fi

# --- Check 2: a change/runbook that applies config but names no rollback ---
is_change_doc=0
case "$base_lc" in
  *change* | *runbook* | *rollback*) is_change_doc=1 ;;
esac
if [[ "$is_change_doc" -eq 0 ]]; then
  # Also treat a file containing device-config-apply wording as a change doc.
  if grep -iqE '(configure[[:space:]]+terminal|conf[[:space:]]+t|commit[[:space:]]+confirm|apply[[:space:]]+the[[:space:]]+change)' "$file"; then
    is_change_doc=1
  fi
fi
if [[ "$is_change_doc" -eq 1 ]]; then
  if ! grep -iqE 'roll[[:space:]-]?back' "$file"; then
    warnings+=("this looks like a change/runbook doc but names no rollback path — every production network change needs an auto-revert / saved rollback (best-practices/no-change-without-a-rollback-path.md).")
  fi
fi

if [[ ${#warnings[@]} -eq 0 ]]; then
  exit 0
fi

{
  echo "networking-engineering — advisory hygiene check flagged $file:"
  for w in "${warnings[@]}"; do
    echo "  • $w"
  done
} >&2

if [[ "${NETENG_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
