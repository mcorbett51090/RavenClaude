#!/usr/bin/env bash
# flag-network-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit. Flags mechanically-detectable
# violations of the network-engineering team constitution (see
# plugins/network-engineering/CLAUDE.md and best-practices/):
#
#   1. Permissive any/any rules — a firewall/ACL line permitting any source to any
#      destination (segment-by-trust / default-deny east-west — best-practices/
#      segment-by-trust.md). Inspected in config-shaped files.
#   2. Cleartext management — telnet or http (non-TLS) management enabled, instead
#      of ssh/https. Inspected in config-shaped files.
#   3. A network CHANGE document with no rollback or no change window
#      (no-change-without-rollback.md). Inspected in change-doc .md files.
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set NETENG_STRICT=1 to make
# violations blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to the
# agent. exit 0 = allow.

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

violations=()

# --- Config-shaped files: any/any rules + cleartext management ---------------
case "$base_lc" in
  *.cfg | *.conf | *.ios | *.nxos | *.junos | *.txt)
    # 1. Permissive any/any permit (Cisco ACL "permit ip any any", or a generic
    #    firewall rule allowing any->any). Deny any/any is fine (default-deny).
    if grep -qiE '(permit|allow).*\bany\b.*\bany\b' "$file"; then
      violations+=("any/any PERMIT rule found — segment by trust, default-deny east-west, allow-list from a real flow inventory (best-practices/segment-by-trust.md). Security sufficiency verdict → security-engineering.")
    fi
    # 2. Cleartext management: telnet enabled, or http (non-secure) server.
    if grep -qiE '(^|[^a-z])transport input .*telnet|(^|[^a-z])telnet\b|ip http server\b' "$file"; then
      violations+=("Cleartext management detected (telnet / 'ip http server') — use SSH / HTTPS for device management (best-practices/no-change-without-rollback.md context: management plane hygiene).")
    fi
    ;;
esac

# --- Markdown change docs: missing rollback / window -------------------------
case "$base_lc" in
  *.md)
    # Only inspect docs that look like a network CHANGE plan/runbook.
    if grep -qiE 'change (plan|window|request)|cutover|migrat|maintenance window' "$file"; then
      if ! grep -qiE 'rollback|back[- ]?out|revert' "$file"; then
        violations+=("This reads like a network change doc but has no ROLLBACK — every change ships a tested rollback with a trigger (best-practices/no-change-without-rollback.md).")
      fi
      if ! grep -qiE 'change window|maintenance window|window:' "$file"; then
        violations+=("This reads like a network change doc but names no change WINDOW — size the window to the blast radius (best-practices/no-change-without-rollback.md).")
      fi
    fi
    ;;
esac

[[ ${#violations[@]} -eq 0 ]] && exit 0

{
  echo "network-engineering — advisory: ${#violations[@]} possible anti-pattern(s) in $(basename "$file"):"
  for v in "${violations[@]}"; do
    echo "  • $v"
  done
} >&2

if [[ "${NETENG_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
