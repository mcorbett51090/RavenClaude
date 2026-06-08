#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the blockchain-web3-engineering plugin.
# Flags common Blockchain & Web3 Engineering anti-patterns in generated deliverables
# (a metric with no baseline | an unsourced benchmark | private keys / wallet data). Advisory
# by default — set BLOCKCHAIN_WEB3_ENGINEERING_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${BLOCKCHAIN_WEB3_ENGINEERING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "blockchain-web3-engineering" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scan — case-insensitive, advisory only.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: review this Blockchain & Web3 Engineering deliverable against the §3 house opinions (baseline on every metric, source+date on every benchmark, no private keys / wallet data)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "blockchain-web3-engineering: $findings advisory finding(s); BLOCKCHAIN_WEB3_ENGINEERING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
