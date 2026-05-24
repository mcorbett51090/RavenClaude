---
name: new-worktree
description: Create an isolated git worktree under .claude/worktrees/ for a sub-agent to work in. Use this before dispatching any coder agent so that parallel work cannot collide.
---

# Skill: new-worktree

## Inputs
- `role` — one of: `architect`, `backend-coder`, `frontend-coder`, `fullstack-coder`, `tester`.
- `slug` — short kebab-case identifier of the task (e.g. `auth-refresh`, `nav-redesign`).
- `base` — branch to fork from. Default: `main`.

## Procedure
1. **Validate inputs.** Slug must match `^[a-z0-9][a-z0-9-]{1,40}$`. Reject otherwise.
2. **Resolve paths.**
   - Path: `.claude/worktrees/<role>-<slug>/`
   - Branch: `agent/<role>/<slug>`
3. **Refuse if either exists.** If the path or branch already exists, surface it — do not silently reuse. The Team Lead must decide whether to clean up the old one or pick a new slug.
4. **Sync base.** `git fetch origin <base>` so the worktree starts from current upstream.
5. **Create the worktree.**
   ```bash
   git worktree add -b agent/<role>/<slug> .claude/worktrees/<role>-<slug> origin/<base>
   ```
6. **Install dependencies if needed.** If the project requires a per-tree install (e.g. `pnpm install`), run it once in the new worktree before handing off.
7. **Report the path and branch back to the Team Lead.** The Team Lead then briefs the agent and points it at this directory.

## Cleanup
Worktrees are NOT auto-removed. Use [`cleanup-worktrees`](../cleanup-worktrees/SKILL.md) when the task is integrated.

## Why this exists
Two parallel coder agents on the same working tree will silently corrupt each other's diffs. Worktrees are cheap; recovery from a stomped diff is not.

## Why a skill, when the Agent tool has built-in `isolation: "worktree"`?
The Agent tool's native worktree isolation is a one-off, ephemeral worktree that gets cleaned up automatically when the sub-agent makes no changes. This skill is for the Team Lead's *managed* worktrees that persist across sub-agent runs: predictable paths under `.claude/worktrees/<role>-<slug>/`, predictable branch names `agent/<role>/<slug>`, and tracked by [`cleanup-worktrees`](../cleanup-worktrees/SKILL.md) so they don't accumulate silently. Use the native isolation for fire-and-forget exploration; use this skill when the worktree is part of a multi-step Team Lead workflow that needs to be visible to subsequent agents.
