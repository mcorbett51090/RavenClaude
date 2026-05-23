# Sub-agent isolation & tooling — what delegated agents can and can't do

> **Last reviewed:** 2026-05-23, against observed Claude Code (Opus 4.7) behavior during a parallel multi-agent PR-review engagement. **Refresh when:** Anthropic changes sub-agent permission inheritance, the `isolation: "worktree"` behavior, or background-task tooling. Companion to [`claude-code-permissions.md`](claude-code-permissions.md).

This file records a non-obvious, load-bearing constraint on how the Team Lead delegates work to sub-agents. It cost a full round of blocked agents to discover — capture it so the next orchestration doesn't repeat the mistake.

## The lesson in one line

**A sub-agent launched with `isolation: "worktree"` is denied `Bash` (and `Read`) in this environment — so it cannot run any git operation (checkout / commit / push) or read files via the shell. Worktree isolation buys a clean working tree at the cost of the very tools branch-mutating work needs.**

## What was observed (2026-05-23)

A 7-PR review ran two waves of delegated agents against the same repo:

| Wave | Agents | Isolation | Tools needed | Result |
|---|---|---|---|---|
| Review (read-only) | 18 background agents | none | `git show <ref>:<path>`, `Read`, `Grep` | ✅ all worked, fully in parallel |
| Edit-application (writes) | 7 background agents | `worktree` | `git checkout` / `commit` / `push` | ❌ all 7 denied `Bash` + `Read`; zero progress |

The read-only wave parallelized perfectly because `git show <ref>:<path>` reads any branch **without touching the working tree** — no checkout, no collision, no isolation needed. The write wave failed because worktree isolation stripped Bash.

## Why it happens

- `git show origin/<branch>:<file>` prints a blob from any ref without changing `HEAD` or the working tree. N agents can read N different branches concurrently in one shared clone with zero contention.
- `git checkout <branch>` mutates the shared working tree. Two agents checking out two branches in the same clone collide — which is _why_ you'd reach for `isolation: "worktree"` in the first place.
- But here, `isolation: "worktree"` runs the agent in a restricted permission context where `Bash` (and `Read`) are denied. So the isolation that would prevent the collision also removes the tools the write needs. Dead end.

## How to actually delegate the work

**Read-only fan-out (analysis, review, search):** spawn non-isolated background agents freely and in parallel. Have them read via `git show <ref>:<path>`. Fast, safe, and the right default for multi-branch review.

**Branch-mutating work (edit / commit / push across branches):** pick one —

1. **Main agent does it sequentially.** The Team Lead (main session) has full Bash; check out each branch, edit, commit, push, in turn. Most reliable; best when edits are precise and the doc set is small.
2. **Non-isolated agents, serialized one at a time.** Non-isolated background agents _do_ have Bash; launch one per branch, waiting for each to finish before the next, so they never fight over the shared working tree.
3. **Agents manage their own worktree by hand via Bash.** A non-isolated agent runs `git worktree add /tmp/wt-<branch> <branch>`, works there, then `git worktree remove`. This restores parallelism without the isolation flag — at the cost of a more failure-prone prompt.

**Do NOT** use `isolation: "worktree"` for any task whose acceptance criterion requires Bash or Read. Reserve it for self-contained reasoning that needs a scratch copy of the tree but no shell.

## Rule of thumb

> Reading a branch needs no isolation (`git show`); writing a branch needs Bash, and `isolation: "worktree"` takes Bash away. Parallel reads: yes. Parallel writes: serialize, or let the agent build its own worktree by hand.
