---
name: cleanup-worktrees
description: Remove finished agent worktrees, prune their branches, and surface anything still in flight. Run at the end of a multi-agent session and weekly as hygiene.
---

# Skill: cleanup-worktrees

> **Labeling (Sleipnir):** worktrees are "Sleipnir's stables" in user-facing prose (see `ravenclaude-core/CLAUDE.md` → "Sleipnir"); this skill returns Sleipnir to the stable. Labeling only; the mechanics below are unchanged.

## Procedure
1. **List.** `git worktree list --porcelain`. Show the user a short table: path, branch, HEAD, dirty?
2. **Classify each worktree.**
   - **Merged** — its branch is fully reachable from `main` (or the configured base). Safe to remove.
   - **Open PR** — branch has an open PR. Don't remove.
   - **Dirty** — uncommitted changes. Surface and stop; the Team Lead must decide.
   - **UNKNOWN** — `git status` itself FAILED for that tree (stale linked worktree
     whose admin dir under `.git/worktrees/` is gone, corrupt `.git`, permission
     denied). ⛔ This is **not** a third flavour of clean: a failed inspection
     writes empty stdout, byte-identical to a clean tree's, so treating it as
     clean deletes work nobody looked at. `worktree-clean.sh` refuses it — and
     refuses it **even with `--force`**, because `--force` discards uncommitted
     work and here we do not know whether there is any. Repair it first
     (`git worktree repair` / `git worktree prune`) or move it aside; do not
     reach for `--force`.
   - **Stale** — last commit > 14 days old, no PR. Flag for the user, don't remove without confirmation.
3. **Close the lane first.** Close the VS Code window / end the Chat session for that worktree before `git worktree remove`, or the next session can reuse an Agents-window conversation from the removed tree.
4. **Remove the safe ones.**
   ```bash
   git worktree remove .claude/worktrees/<role>-<slug>
   git branch -d agent/<role>/<slug>     # only if fully merged
   ```
   Use `-d` (safe), never `-D` (force) without explicit user approval.
5. **Prune metadata.** `git worktree prune`.
6. **Report.** What was removed, what was kept, what needs attention.

## Output format
```
Removed (3):
  agent/coder/auth-refresh   merged into main 2 days ago
  agent/tester/auth-refresh  merged into main 2 days ago
  agent/coder/nav-typo       merged into main 5 days ago

Kept (2):
  agent/coder/billing-page   open PR #142
  agent/coder/exp-feature    dirty — uncommitted changes

Needs review (1):
  agent/coder/old-spike      stale, last commit 23 days ago, no PR
```

## Don'ts
- Never delete a worktree with uncommitted changes without explicit user approval.
- Never `git branch -D` (force-delete) without approval. `-d` will refuse to delete unmerged branches; that's the correct behavior.
- Never delete the worktree you're currently running inside.

## Why a skill, when the Agent tool has built-in `isolation: "worktree"`?
The Agent tool's native worktree isolation auto-cleans up its own ephemeral worktrees. This skill cleans up the *managed* worktrees created by [`new-worktree`](../new-worktree/SKILL.md) — predictable paths, predictable branch names, persisting across multiple sub-agent runs so the Team Lead can hand a worktree off between agents. Those won't be cleaned by the harness, so the Team Lead runs this skill at the end of a multi-agent session and weekly as hygiene.
