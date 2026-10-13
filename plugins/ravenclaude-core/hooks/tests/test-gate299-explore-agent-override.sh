#!/usr/bin/env bash
# test-gate299-explore-agent-override.sh — Gate 299 fixture (v0.352.0).
#
# Proves the project-level `Explore` agent override exists and stays a
# read-only Haiku worker, and that the ravenclaude-core agent count claims
# track the roster that now includes it.
#
#   E1  agents/explore.md exists with `name: Explore`
#   E2  `model: haiku`
#   E3  `tools:` is exactly {Read, Grep, Glob} (no Write/Edit/Bash)
#   E4  ravenclaude-core has exactly 18 agent definitions (17 + Explore)
#   E5  README "Specialist agents" row claims the on-disk count
#   E6  codex + copilot projections of the Explore agent exist
#   T1  teeth: a copy of explore.md with `Write` added to tools must fail E3
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-gate299-explore-agent-override.sh
# Run via gate:   bash scripts/audit-gates.sh --check 299

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT" || exit 1
CORE="plugins/ravenclaude-core"
AGENT="$CORE/agents/explore.md"
EXPECTED_AGENTS=18
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

fm_field() { # file key -> value of a top-level frontmatter key
  awk -v k="$2" 'NR==1&&$0!="---"{exit} NR>1&&$0=="---"{exit} NR>1{ if (index($0, k":")==1){ sub("^"k":[[:space:]]*",""); print; exit } }' "$1"
}
tools_ok() { # file -> 0 iff tools is exactly Read, Grep, Glob (any order)
  local t; t="$(fm_field "$1" tools | tr -d '[]"' | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed '/^$/d' | sort | paste -sd, -)"
  [ "$t" = "Glob,Grep,Read" ]
}

if [ -f "$AGENT" ]; then
  pass "E1a agents/explore.md exists"
  [ "$(fm_field "$AGENT" name)" = "Explore" ] && pass "E1b name: Explore" || fail "E1b name is '$(fm_field "$AGENT" name)', want Explore"
  [ "$(fm_field "$AGENT" model)" = "haiku" ] && pass "E2 model: haiku" || fail "E2 model is '$(fm_field "$AGENT" model)', want haiku"
  tools_ok "$AGENT" && pass "E3 tools exactly Read, Grep, Glob" || fail "E3 tools is '$(fm_field "$AGENT" tools)', want Read, Grep, Glob only"
else
  fail "E1 $AGENT missing"
fi

n="$(find "$CORE/agents" -maxdepth 1 -type f -name '*.md' ! -iname 'README.md' ! -iname 'CHANGELOG.md' ! -iname 'NOTES.md' | wc -l | tr -d ' ')"
[ "$n" = "$EXPECTED_AGENTS" ] && pass "E4 core agent count = $EXPECTED_AGENTS" || fail "E4 core agent count = $n, want $EXPECTED_AGENTS"

claim="$(sed -n 's/^| Specialist agents | \([0-9]\{1,\}\) |.*/\1/p' "$CORE/README.md" | head -1)"
[ "$claim" = "$n" ] && pass "E5 README claims $claim agents (matches disk)" || fail "E5 README claims '$claim' agents, disk has $n"

# Generators name projections after the agent's `name:` (Explore), so match case-insensitively.
[ -n "$(find "$CORE/codex/agents" -maxdepth 1 -iname 'explore.toml' 2>/dev/null)" ] && pass "E6a codex projection exists" || fail "E6a codex/agents/explore.toml (any case) missing"
[ -n "$(find "$CORE/copilot/agents" -maxdepth 1 -iname 'explore.agent.md' 2>/dev/null)" ] && pass "E6b copilot projection exists" || fail "E6b copilot/agents/explore.agent.md (any case) missing"

# Teeth: a mutant with Write added must NOT satisfy the read-only check.
if [ -f "$AGENT" ]; then
  tmp="$(mktemp)"
  sed 's/^tools:.*/tools: Read, Grep, Glob, Write/' "$AGENT" > "$tmp"
  if tools_ok "$tmp"; then fail "T1 teeth: Write-added mutant passed the read-only check"; else pass "T1 teeth: Write-added mutant rejected"; fi
  rm -f "$tmp"
fi

echo "  passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]
