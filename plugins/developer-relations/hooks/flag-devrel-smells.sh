#!/usr/bin/env bash
# flag-devrel-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on DevRel content / strategy files
# (.md / .mdx). Flags three mechanically-detectable violations of the
# developer-relations team constitution (see
# plugins/developer-relations/CLAUDE.md §3 / §4 and
# knowledge/devrel-metrics.md):
#
#   1. A quickstart / tutorial fenced code block opened with a bare ``` (no
#      runnable language tag like ```bash / ```python / ```js / ```ts / ```go).
#      A sample a developer can't copy-paste-run is a broken golden path.
#      (house opinion: sample apps must run unmodified)
#   2. A DevRel goal / KPI stated ONLY in vanity metrics (raw follower counts,
#      GitHub stars, page views, impressions) with NO activation / TTFHW /
#      funnel metric anywhere in the file. (pitfall — vanity metrics)
#   3. A quickstart / "time to first hello world" doc that never names a
#      measurable success criterion (TTFHW / activation / "you should see").
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

# Only inspect DevRel content / strategy markdown.
case "$base_lc" in
  *.md | *.mdx) ;;
  *) exit 0 ;;
esac

violations=()

# Patterns reused below.
quickstart_re='quickstart|quick start|getting started|hello world|time to first|ttfhw|tutorial|golden path'
vanity_re='follower|followers|github stars?|star count|page ?views?|impressions|likes|raw views|subscriber count'
real_metric_re='ttfhw|time to first|activation|first[ -]?hello[ -]?world|funnel|retention|conversion|aaarrp|qualitative feedback|signup[ -]?to[ -]?activation'
goal_re='\bgoal\b|\bkpi\b|\bok[rs]\b|\bnorth star\b|\bobjective\b|success metric|we measure|key metric'
success_criterion_re='you should see|expected output|success looks like|you.?ll see|verify|activation|ttfhw|time to first|done when|by the end'

# ---------------------------------------------------------------------------
# Check 1: a fenced code block with no language tag in a quickstart/tutorial doc
# ---------------------------------------------------------------------------
# Detect a code fence line that is exactly ``` (optionally trailing spaces) — a
# bare fence has no runnable language tag. `|| true` keeps a no-match grep from
# aborting under set -o pipefail.
if grep -niEq "$quickstart_re" "$file" 2>/dev/null; then
  bare_fences=$(grep -nE '^[[:space:]]*```[[:space:]]*$' "$file" 2>/dev/null | wc -l | tr -d ' ' || true)
  # Each opening+closing pair is 2 fence lines; a bare OPENING fence is the smell.
  # An opening fence with a language has text after the backticks, so it isn't
  # counted here. Two or more bare fences => at least one bare opening block.
  if [[ "${bare_fences:-0}" -ge 2 ]]; then
    violations+=("A quickstart/tutorial code block uses a bare \`\`\` fence with no runnable language tag (\`\`\`bash / \`\`\`python / \`\`\`js …). A sample a developer cannot copy-paste-run is a broken golden path.")
  fi
fi

# ---------------------------------------------------------------------------
# Check 2: a goal/KPI stated only in vanity metrics, no real funnel metric
# ---------------------------------------------------------------------------
if grep -niEq "$goal_re" "$file" 2>/dev/null && grep -niEq "$vanity_re" "$file" 2>/dev/null; then
  if ! grep -niEq "$real_metric_re" "$file" 2>/dev/null; then
    violations+=("A DevRel goal/KPI is stated only in vanity metrics (followers / stars / page views / impressions) with no activation, TTFHW, or funnel metric. Vanity metrics measure reach, not developer success — pair them with an activation/retention metric.")
  fi
fi

# ---------------------------------------------------------------------------
# Check 3: a quickstart/TTFHW doc with no measurable success criterion
# ---------------------------------------------------------------------------
if grep -niEq 'hello world|ttfhw|time to first|quickstart|quick start' "$file" 2>/dev/null; then
  if ! grep -niEq "$success_criterion_re" "$file" 2>/dev/null; then
    violations+=("A quickstart / time-to-first-hello-world doc names no measurable success criterion (\"you should see …\", expected output, an activation/TTFHW target). The developer cannot tell when they have succeeded.")
  fi
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#violations[@]} -eq 0 ]]; then
  exit 0
fi

echo "" >&2
echo "[developer-relations-smells] Advisory warnings for ${file}:" >&2
for v in "${violations[@]}"; do
  echo "  - ${v}" >&2
done
echo "" >&2
echo "  Advisory by default. Set DEVREL_STRICT=1 to make them blocking." >&2
echo "  See plugins/developer-relations/knowledge/devrel-metrics.md for the fixes." >&2
echo "" >&2

if [[ "${DEVREL_STRICT:-0}" == "1" ]]; then
  # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is non-blocking
  # and would silently allow the edit despite the warning.
  exit 2
fi
exit 0
