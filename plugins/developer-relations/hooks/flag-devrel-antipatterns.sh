#!/usr/bin/env bash
# flag-devrel-antipatterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on DevRel artifacts
# (.md/.mdx/.json/.yaml/.yml + common code-sample extensions). Flags three
# mechanically-detectable violations of the developer-relations team constitution
# (see plugins/developer-relations/CLAUDE.md §3, §4):
#
#   1. A vanity-metric headline (GitHub stars / followers / registered developers)
#      with NO activation / time-to-first-success metric anywhere in the file
#      (house opinion #1 — measure activation, not applause)
#   2. Marketing-speak aimed at developers ("revolutionary", "best-in-class",
#      "game-changer", "synergy", "leverage our")
#      (house opinion #2 — teach, don't market)
#   3. A placeholder secret / hard-coded API key / TODO in a code sample
#      (house opinion #3 — sample code runs as shipped)
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set DEVREL_STRICT=1 to make
# violations blocking (exit 2).
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

# Only inspect DevRel-shaped files.
case "$base_lc" in
  *.md | *.mdx | *.json | *.yaml | *.yml | *.txt) doc=1 ;;
  *.js | *.ts | *.jsx | *.tsx | *.py | *.rb | *.go | *.java | *.php | *.sh | *.env) doc=0 ;;
  *) exit 0 ;;
esac

violations=()

vanity_re='github stars|\bstars\b|followers|registered developers|impressions|member count'
activation_re='time[ _-]?to[ _-]?first[ _-]?success|\bttfs\b|activation rate|activation|first working result|returning developers|resolution rate'
marketing_re='revolutionary|best[ -]in[ -]class|game[ -]changer|cutting[ -]edge|leverage our|synergy|synergies|world[ -]class|next[ -]generation|paradigm shift'
todo_re='\bTODO\b|\bFIXME\b|left as an exercise|implement this yourself'
secret_re='YOUR[_-]?API[_-]?KEY|sk_live_|sk_test_|api[_-]?key\s*[:=]\s*["'"'"'][A-Za-z0-9]{12,}|AKIA[0-9A-Z]{16}|hard[ -]?coded (key|secret|token)'

# ---------------------------------------------------------------------------
# Check 1: vanity-metric headline with no activation metric (doc files)
# ---------------------------------------------------------------------------
if [[ "$doc" == "1" ]]; then
  if grep -niEq "$vanity_re" "$file" 2>/dev/null; then
    if ! grep -niEq "$activation_re" "$file" 2>/dev/null; then
      violations+=("A vanity metric (stars / followers / registered developers) appears with no activation / time-to-first-success metric in the file. Lead with activation, demote vanity to context. (house opinion #1)")
    fi
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: marketing-speak at developers (doc files)
# ---------------------------------------------------------------------------
if [[ "$doc" == "1" ]]; then
  if grep -niEq "$marketing_re" "$file" 2>/dev/null; then
    violations+=("Marketing-speak aimed at developers (revolutionary / best-in-class / synergy / game-changer …). Teach, don't market — would this sentence survive in a competitor's docs? (house opinion #2)")
  fi
fi

# ---------------------------------------------------------------------------
# Check 3: placeholder secret / hard-coded key / TODO in a code sample
# ---------------------------------------------------------------------------
if [[ "$doc" == "0" ]]; then
  if grep -nEq "$secret_re" "$file" 2>/dev/null; then
    violations+=("A placeholder/hard-coded secret in a code sample. Read secrets from env/config; never commit a real-looking key. A security verdict routes to ravenclaude-core/security-reviewer. (house opinion #3)")
  fi
  if grep -nEq "$todo_re" "$file" 2>/dev/null; then
    violations+=("A TODO / 'left as an exercise' in a code sample. Samples run as shipped — the happy path has no gaps. (house opinion #3)")
  fi
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[devrel-antipatterns] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set DEVREL_STRICT=1 to make them blocking." >&2
echo "  See plugins/developer-relations/CLAUDE.md §3/§4 for the fixes." >&2
echo "" >&2

if [[ "${DEVREL_STRICT:-0}" == "1" ]]; then
  # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is non-blocking
  # and would silently allow the edit despite the warning.
  exit 2
fi
exit 0
