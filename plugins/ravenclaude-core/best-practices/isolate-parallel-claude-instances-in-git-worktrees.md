# Run parallel Claude Code instances in separate git worktrees — never aim two writers at one working tree

**Status:** Pattern
**Domain:** Multi-agent / Branch management / Project setup
**Applies to:** `ravenclaude-core`

---

## Why this exists

There are two different kinds of "parallelism," and the safe mechanism is different for each:

1. **Sub-agents inside one session** (the Team Lead fanning work to `Agent` workers) — governed by [`delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md): fan _reads_ out freely, keep branch-mutating writes in the main session. That rule **explicitly excludes** the other kind — its own edge-case line says "CI environments where multiple agents are independent processes (not sub-agents of the same Team Lead) have different isolation; this rule governs the sub-agent relationship, **not peer-process parallelism**."
2. **Peer-process parallelism** — multiple independent Claude Code instances running at once (two terminals, a CI matrix, an orchestrator launching several `claude` processes), each one a full writer. This rule governs that case, the one the sub-agent rule hands off.

When two independent writers share **one working tree**, they stomp each other: instance A's edit to `src/auth.ts` is clobbered (or merge-mangled) by instance B's, each one's reads see the other's half-finished state, and the staging area becomes a race. The failure is silent at write time and only surfaces later as lost work or an incoherent diff — the worst error mode. A git **worktree** is the deterministic fix: `git worktree add` attaches a second working directory on its own branch, sharing the one `.git` object store but with a **private working tree and index**. Each instance edits, stages, and commits in isolation; the branches reconcile through a normal merge/PR, not through a filesystem race.

This marketplace already _ships the tooling_ for this — the [`new-worktree`](../skills/new-worktree/SKILL.md) and [`cleanup-worktrees`](../skills/cleanup-worktrees/SKILL.md) skills, and the **Sleipnir** labeling convention (the mount that crosses realm boundaries safely) — but it had no consumer-facing _rule_ naming the posture those tools exist to serve. This is that rule.

## How to apply

Partition on a single question — **is this a second independent writer, or a sub-agent of the current session?**

**One worktree per parallel writer (peer-process parallelism):**

- Spinning up a second `claude` to work a different feature/branch while the first keeps going → give it its own worktree, don't open it in the same checkout.
- An orchestrator or CI matrix launching N independent agents that each commit → N worktrees (or N clones), one branch each.
- "I want to try two approaches at once" → a worktree per approach; compare the branches, keep the winner.

```shell
# Each parallel instance gets an isolated working tree on its own branch:
git worktree add ../repo-feat-auth   feat/auth      # instance A lives here
git worktree add ../repo-feat-search feat/search    # instance B lives here
# …work both in parallel, commit independently, then merge/PR each branch.
git worktree remove ../repo-feat-auth                # clean up when the branch lands
```

**Do:**

- Give every concurrently-writing Claude Code instance its **own** worktree (or its own clone) on its **own** branch — the working tree and index are what must not be shared, and a worktree isolates exactly those while sharing history.
- Reconcile the parallel work through **merge / PR**, the same way you'd integrate two humans' branches — that's the integration point, not the filesystem.
- Use the bundled [`new-worktree`](../skills/new-worktree/SKILL.md) / [`cleanup-worktrees`](../skills/cleanup-worktrees/SKILL.md) skills so the create/branch/remove lifecycle is consistent (and prune stale worktrees — an abandoned one holds a branch ref and disk).
- In user-facing dispatch prose, the cross-branch traversal is "**Sleipnir**" — the same convention the sub-agent reads use.

**Don't:**

- Don't point two parallel instances at the **same** working directory expecting git to sort it out — it can't; concurrent edits/stages to one tree race and silently lose writes.
- Don't reach for peer-process worktrees to solve the **sub-agent** write problem — a background sub-agent's git-write is auto-denied regardless of worktree, and `isolation: "worktree"` on a sub-agent _also strips `Read`_ (see the sibling rule). Worktrees are for independent **processes**, not for unlocking sub-agent commits.
- Don't leave worktrees lying around after their branch merges — `git worktree remove` (or the cleanup skill); a stale worktree is the peer-process analogue of an un-deleted merged branch.

## Edge cases / when the rule does NOT apply

- **A single Claude Code instance** working one branch at a time needs no worktree — this is purely a _concurrent-writers_ rule. Sequential branch-switching in one session is fine on one tree.
- **Sub-agents of one Team Lead** are the _other_ rule's domain ([`delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md)) — fan reads out, keep writes in main; a worktree doesn't change that.
- **Full clones** are a heavier but equally-valid isolation when the processes are on different machines or you want fully independent object stores; the worktree is the lighter-weight same-host choice (shared `.git`, no re-fetch).
- **Web / remote sessions** (Claude Code on the web) run in an isolated container that _is_ the boundary — within one such session you're still a single writer; this rule bites when _you_ deliberately run several instances in parallel.

## See also

- [`./delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md) — the sibling rule for **sub-agent** parallelism (this rule is its named complement: that one is intra-session, this one is peer-process; that rule's edge case explicitly defers peer-process parallelism here).
- [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) — why commits (not `/rewind`) are the durable unit each worktree's branch records.
- [`../skills/new-worktree/SKILL.md`](../skills/new-worktree/SKILL.md) · [`../skills/cleanup-worktrees/SKILL.md`](../skills/cleanup-worktrees/SKILL.md) — the bundled create/cleanup lifecycle this rule's posture is built on.

## Provenance

Distilled from a 2026-06-13 scan of Claude Code community discussion (r/ClaudeAI / r/ClaudeCode and aggregations of it) cross-checked against [Anthropic's Claude Code best-practices docs](https://code.claude.com/docs/en/best-practices) and the [git-worktree documentation](https://git-scm.com/docs/git-worktree). The community's recurring "run multiple Claude Code instances in parallel, each in its own git worktree, so they don't stomp each other" lesson was already _tooled_ on this repo (the `new-worktree`/`cleanup-worktrees` skills + the Sleipnir convention) and the sub-agent rule explicitly _deferred_ peer-process parallelism to a future rule — this names it as a consumer-facing best-practice. Research + panel record: [`docs/research/2026-06-13-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-13-claude-subreddit-scan/README.md).

---

_Last reviewed: 2026-06-13 by `claude`_
