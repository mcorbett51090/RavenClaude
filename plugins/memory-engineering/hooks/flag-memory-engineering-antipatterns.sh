#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the memory-engineering plugin.
# Flags two memory-engineering anti-patterns in generated deliverables
# (a memory-benchmark figure with no source or retrieval date | a cost or
# break-even claim with no named baseline). Advisory by default — set
# MEMORY_ENGINEERING_STRICT=1 to make it blocking.

FILE="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives via
# the canonical stdin JSON contract. Fall back to it — the same dual-source
# pattern guard-destructive.sh / the core file hooks use, and the exact
# regression the ai-rag-engineering sibling shipped and fixed in its 0.1.1.
if [ -z "$FILE" ] && [ ! -t 0 ] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    FILE="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${MEMORY_ENGINEERING_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "memory-engineering" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scans — case-insensitive, advisory only. Each is a reminder to check
# the deliverable against the §3 house opinions, not a hard verdict.
#
# PORTABILITY: every pattern below is pure POSIX ERE — no \d, \s, \b, no
# look-around, no non-capturing groups. A PCRE-only construct is misparsed by
# GNU grep (warns, matches nothing) and BSD/macOS grep rejects the PCRE flag
# outright with exit 2, which inside an `if` reads as NO MATCH — so the check
# would never fire and a clean run would look like a pass. Character classes
# ([[:space:]], [0-9]) are the portable spelling. Gated by
# scripts/check-grep-ere-pcre.py.

# 1. A memory-benchmark or leaderboard figure with no source URL, no arXiv ID,
#    no retrieval date and no [unverified] marker (§3 #8; §4 cite-or-mark).
#    Every published memory ranking is self- or competitor-reported, so an
#    unattributed figure is the one most likely to be read as a property of the
#    technique rather than of one vendor's run.
if grep -Eiq 'longmemeval|locomo|leaderboard|benchmark|state[ -]of[ -]the[ -]art' "$FILE" &&
  grep -Eiq '[0-9]+(\.[0-9]+)?[[:space:]]*%|[0-9]+[[:space:]]*(j/correct|joules per correct)' "$FILE" &&
  ! grep -Eiq 'https?://|arxiv|retrieved|[[]unverified|self-reported|competitor-reported|vendor-published' "$FILE"; then
  note "A memory-benchmark figure appears with no source URL, arXiv ID, retrieval date or [unverified] marker — every published memory ranking is self- or competitor-reported, so attribute it or mark it (§3 #8, §4)."
fi

# 2. A cost, amortization or break-even claim with no named baseline anywhere in
#    the file (§3 #1, #2). `amortize` requires --baseline and has no default for
#    exactly this reason: a break-even with no baseline beside it is not a number.
if grep -Eiq 'cost per correct|cost-per-correct|break-even|breakeven|breaks even|amortiz|pays for itself|earns its write path|per-query cost|cost per query' "$FILE" &&
  ! grep -Eiq 'baseline|full-context-prefill|lexical-retrieval|stateless|bm25|no[ -]memory' "$FILE"; then
  note "A cost / amortization / break-even claim appears with no named baseline (full-context-prefill, lexical-retrieval, stateless, or the no-memory baseline) — cost is only meaningful against the thing it replaces (§3 #1, #2)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "memory-engineering: $findings advisory finding(s); MEMORY_ENGINEERING_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
