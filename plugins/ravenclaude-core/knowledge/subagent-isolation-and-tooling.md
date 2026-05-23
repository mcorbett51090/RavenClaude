# Sub-agent isolation & tooling — what delegated agents can and can't do

> **Last reviewed:** 2026-05-23, against observed Claude Code (Opus 4.7) behavior during a parallel multi-agent PR-review engagement. **Refresh when:** Anthropic changes sub-agent permission inheritance, the `isolation: "worktree"` behavior, or background-task tooling. Companion to [`claude-code-permissions.md`](claude-code-permissions.md).

This file records a non-obvious, load-bearing constraint on how the Team Lead delegates work to sub-agents. It cost two blocked waves of agents to pin down — capture it so the next orchestration doesn't repeat the mistake.

## The lesson in one line

**Delegated sub-agents in this environment cannot run git-_write_ commands (`fetch` / `checkout` / `commit` / `push`) — both worktree-isolated _and_ plain non-isolated background agents were denied. Read-only review agents using `git show` worked fine. Conclusion: branch-mutating git work must be done by the main (interactive) agent — only it can obtain the approval that mutating commands require. Worktree isolation is a _further_ restriction that also strips `Read`.**

## What was observed (2026-05-23)

A 7-PR review ran three waves of delegated agents against the same repo:

| Wave | Agents | Isolation | Tools needed | Result |
|---|---|---|---|---|
| 1. Review (read-only) | 18 background agents | none | `git show <ref>:<path>`, `Read`, `Grep` | ✅ all worked, fully in parallel |
| 2. Edit-application (writes) | 7 background agents | `worktree` | `git checkout` / `commit` / `push` | ❌ all denied **`Bash` + `Read`** |
| 3. Edit-application retry (writes) | 1 background agent | **none** | `git fetch` / `checkout` / `commit` / `push` | ❌ denied **`Bash`** (git-write) — even non-isolated |

Wave 1 parallelized perfectly because `git show <ref>:<path>` reads any branch **without touching the working tree** — no checkout, no collision, no isolation needed. Waves 2 and 3 both failed: the writes never ran. Wave 3 is the decisive data point — dropping isolation did **not** restore the ability to write.

## Why it happens

- `git show origin/<branch>:<file>` prints a blob from any ref without changing `HEAD` or the working tree, and is read-only — so it sits in the pre-allowed tier and runs unattended. N agents can read N different branches concurrently in one clone with zero contention.
- `git fetch` / `checkout` / `commit` / `push` **mutate** state. In this session's permission posture those land in the "ask" tier, and **a background sub-agent cannot surface an interactive approval prompt** — so the call is auto-denied. The main (interactive) agent hits the same tier but _can_ get approval, which is why the Team Lead's own `git commit`/`push` succeed while a sub-agent's identical command is refused.
- `isolation: "worktree"` is a **separate, additional** restriction: it also strips `Read` (wave 2 lost both `Bash` and `Read`). So worktree isolation is strictly worse for this kind of work, not a workaround.

The earlier draft of this file guessed the cause was worktree isolation alone and suggested "serialize non-isolated agents" as a fix. Wave 3 disproved that — recording the correction here so the wrong workaround isn't attempted again.

## How to actually delegate the work

**Read-only fan-out (analysis, review, search):** spawn non-isolated background agents freely and in parallel. Have them read via `git show <ref>:<path>`. Fast, safe, and the right default for multi-branch review.

**Branch-mutating work (edit / commit / push across branches):** **the main (interactive) agent does it** — sequentially, branch by branch (checkout → edit → commit → push → next). This is the only path confirmed to work in this environment, because mutating git needs approval a background sub-agent can't get. Two things that look like workarounds but do **not** help here:

- _Non-isolated agents, serialized one per branch_ — still denied (wave 3); the blocker is the approval tier, not working-tree contention.
- _Agents building their own `git worktree` by hand_ — still needs git-write Bash (denied), and edits land on `/tmp/...` paths that the `enforce-layout` hook rejects as off-pattern.

If the write volume is large, the lever is **the main agent's context budget**, not delegation: read targeted sections of large files (`git show`/`grep` to locate, `Read` with offset/limit) rather than whole files, and commit each branch before moving to the next so progress survives a context summarization.

## Rule of thumb

> Reading a branch needs no isolation and no approval (`git show` — parallelize across sub-agents freely). Writing a branch needs approval that only the main agent can obtain — so do all checkout/commit/push work in the main session, sequentially. `isolation: "worktree"` only makes it worse (it also removes `Read`). Don't delegate git-writes to sub-agents in this environment.
