#!/usr/bin/env bash
# flag-graph-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on graph-shaped files.
# Flags three ERROR-class smells from the graph-engineering constitution
# (see plugins/graph-engineering/CLAUDE.md). Mirrors lint_graph_shape.py
# ERROR checks in POSIX ERE — no Python, no \\d \\s \\b look-around.
#
#   1. Unbounded variable-length path: [*]  [*..]  [*1..]
#   2. Missing relationship type: -[]-  -[]->  <-[]-
#   3. Anonymous MATCH ()- / MATCH ()<- expansion
#
# Advisory by default (exit 0). GRAPH_SMELLS_STRICT=1 → exit 2.
#
# Dual-source path: $1 then stdin JSON .tool_input.file_path // .tool_input.path
# because $CLAUDE_TOOL_FILE_PATH is often empty.

set -euo pipefail

file="${1:-}"
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

case "$base_lc" in
  *.cypher | *.cyp | *.gql | *.sparql | *.rq | *.groovy | *.py | *.js | *.ts | *.md) ;;
  *) exit 0 ;;
esac

violations=()

# 1. Unbounded [*] or [*..] or [*digits..]  (no upper bound after ..)
if grep -nE '\[\s*([A-Za-z_][A-Za-z0-9_]*)?\s*\*(\s*[0-9]+)?\s*(\.\.\s*)?\]' "$file" >/dev/null 2>&1; then
  # Allow [*1..3] / [*..5] — a digit AFTER the dots.
  if grep -nE '\[\s*([A-Za-z_][A-Za-z0-9_]*)?\s*\*(\s*[0-9]+)?\s*\.\.\s*\]|\[\s*([A-Za-z_][A-Za-z0-9_]*)?\s*\*\s*\]' "$file" >/dev/null 2>&1; then
    violations+=("Unbounded variable-length path ([*], [*..], [*1..]). Give an upper bound ([*1..5]). (bound-variable-length-paths)")
  fi
fi

# 2. Untyped relationship -[]- / -[]-> / <-[]-
if grep -nE '<-\s*\[\s*\]\s*-|-\s*\[\s*\]\s*-' "$file" >/dev/null 2>&1; then
  violations+=("Missing relationship type (-[]- / -[]->). Type and direct every edge. (type-every-relationship)")
fi

# 3. Anonymous MATCH ()-
if grep -nE 'MATCH[[:space:]]+\(\)[[:space:]]*<?-' "$file" >/dev/null 2>&1; then
  violations+=("Anonymous MATCH ()- expansion. Name the start node and type the edge (supernode scan). (model-for-supernodes)")
fi

if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

{
  echo "graph-engineering hook: ${#violations[@]} smell(s) in $file"
  for v in "${violations[@]}"; do
    echo "  - $v"
  done
  echo "Advisory. Set GRAPH_SMELLS_STRICT=1 to block. Twin linter: scripts/lint_graph_shape.py"
} >&2

if [[ "${GRAPH_SMELLS_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
