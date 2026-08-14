#!/usr/bin/env bash
# write-lane-stamp.sh — write $dest/.ravenclaude/lane.md (tree-local identity).
# Usage: write-lane-stamp.sh <dest> <task> <branch> <created_by>
# The stamp is gitignored identity, not constitution. Do not commit it.
set -euo pipefail

dest="${1:?usage: write-lane-stamp.sh <dest> <task> <branch> <created_by>}"
task="${2:?}"
branch="${3:?}"
created_by="${4:-unknown}"

rp="$( cd "$dest" 2>/dev/null && pwd -P )" || rp="$dest"
created_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$dest/.ravenclaude"
cat > "$dest/.ravenclaude/lane.md" <<EOF
task: ${task}
branch: ${branch}
worktree_path: ${rp}
created_at: ${created_at}
created_by: ${created_by}

## Hard rules

- This session's write root is **this worktree only**.
- Do **not** open a sibling worktree as a second folder in this window (multi-root = context pool).
- Do **not** continue an Agents-window session that was started for another workspace.
- Prefer a **new Chat session** when switching windows/worktrees.
- Shared committed \`AGENTS.md\` is intentional; ignore other trees' dirty files / \`.ravenclaude/runs/<other-task>/\`.
EOF
