# Fan read work out to sub-agents freely — keep branch-mutating work in the main session

**Status:** Pattern _(downgraded from Absolute 2026-06-13 — see Provenance)_
**Domain:** Agent design / Multi-agent / Branch management
**Applies to:** `ravenclaude-core`

---

## Why this exists

The Team Lead's most productive pattern is parallel fan-out: spawn multiple sub-agents simultaneously to read code, analyze different branches, or collect data from different parts of the codebase. That pattern works cleanly for reads. It is hazardous for **writes** — but not for the reason this rule originally stated.

The original rationale ("background sub-agents are auto-denied git checkout/commit/push") is **not current** (see Provenance — corrected 2026-06-13). A non-isolated sub-agent in this environment was able to `git checkout -b` and `git commit` (both exit 0, no permission gate), and current docs confirm a sub-agent's tool access is governed by its `tools`/`disallowedTools` grant + permission mode, not a blanket deny. The real hazard is **shared mutable state**: a sub-agent that does not have its own worktree shares the main session's working tree and index, so —

- a sub-agent doing `git checkout <branch>` yanks the shared working tree out from under the main session and any sibling sub-agents; and
- multiple sub-agents committing to one shared tree concurrently race on the index and on each other's uncommitted edits — the same stomp the [worktree-isolation rule](./isolate-parallel-claude-instances-in-git-worktrees.md) prevents for peer processes.

The fix is the same in spirit: **fan reads out freely (they mutate no shared state); for writes, either keep the branch-mutating work serialized in the main session, or give each writing sub-agent its own worktree** (`isolation: "worktree"`). Don't turn two writers loose on one shared working tree — the failure is a silent race, not a clean denial.

## How to apply

Partition the delegation decision along a single axis — does this sub-task mutate a branch?

**Fan out freely (reads — no shared-state mutation):**
- Reading code across multiple branches simultaneously: `git show <ref>:<path>` — safe in parallel.
- Analyzing the same codebase from different angles (security, architecture, performance).
- Gathering data from multiple repos or multiple directories.
- Running tests and reading results (not committing).

**Serialize in the main session, or isolate each writer in its own worktree (writes — branch-mutating):**
- `git checkout`, `git commit`, `git push`, `git merge` against the **shared** working tree → keep in the main session, run sequentially.
- A sub-agent that genuinely needs to write should get its **own** worktree (`isolation: "worktree"` in its frontmatter) so its edits/commits land in an isolated copy, not the shared tree.
- Sequential dependency where sub-agent A's commit must land before sub-agent B reads it → serialize in main.

**Annotated spawn decision:**
```
# Safe — parallel reads (no shared-state mutation)
spawn([
    "analyze src/auth/ for security gaps",
    "analyze src/api/ for security gaps",
    "analyze src/db/ for security gaps",
])

# Unsafe to fan out — concurrent writers race on the shared tree + index;
# keep in main session (or give each its own worktree), run sequentially
main_session.do([
    "fix auth gap — commit",
    "fix api gap — commit",
    "fix db gap — commit",
])
```

**Do:**
- Use `git show <ref>:<path>` (not `git checkout <branch>`) when a sub-agent needs to read a specific branch's version of a file — it reads without touching the working tree.
- Sequence branch-mutating work in the main interactive session; parallelize only once the mutations are done and the next round of reads can begin.
- When a sub-agent must write in parallel, give it `isolation: "worktree"` so it works in an isolated copy of the repo — that's the sanctioned way to let it write without stomping the shared tree.
- Name this pattern "sending Sleipnir" in user-facing dispatch prose when dispatching for cross-branch reading.

**Don't:**
- Don't fan branch-mutating work out to multiple **non-isolated** sub-agents at once — they share one working tree + index and will stomp each other (and the main session). The corruption is a silent race, not a clean denial, which makes it the worst-case error mode.
- Don't assume `isolation: "worktree"` removes a sub-agent's tools — it isolates the **working directory**, not the tool grant (a worktree-isolated sub-agent keeps `Read`). It's the right lever **for** letting a sub-agent write safely, not a thing to avoid.
- Fan out the design phase in parallel and then serially make all the mutations manually — the composition is fine; just keep the mutation in the main session (or in per-writer worktrees).

## Edge cases / when the rule does NOT apply

- A **worktree-isolated** sub-agent (`isolation: "worktree"`) writes into its own copy of the repo, so its commits don't touch the shared tree — this is the sanctioned way to let a sub-agent write in parallel. _(Whether it may `git push` can still depend on the permission mode / remote — verify before relying on a sub-agent push specifically; that leg of the original claim was not re-tested.)_
- CI environments where multiple agents are independent processes (not sub-agents of the same Team Lead) have different isolation; this rule governs the sub-agent relationship, not peer-process parallelism — that case is [`isolate-parallel-claude-instances-in-git-worktrees.md`](./isolate-parallel-claude-instances-in-git-worktrees.md).

## See also

- [`./isolate-parallel-claude-instances-in-git-worktrees.md`](./isolate-parallel-claude-instances-in-git-worktrees.md) — the peer-process complement: when the writers are independent Claude Code **instances** (not sub-agents), give each its own worktree.
- [`../CLAUDE.md`](../CLAUDE.md) — "Delegating branch-mutating work" section (the constitution source — same 2026-06-13 correction applied there).
- [`./route-before-spawning.md`](./route-before-spawning.md) — the routing tree that precedes any spawn decision.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Delegating branch-mutating work (added 2026-05-23)" and the Sleipnir convention (added 2026-05-31, v0.76.0).

**Corrected 2026-06-13.** The original rule asserted background sub-agent git-writes are "auto-denied (confirmed behavior — both worktree-isolated and plain non-isolated agents)." Re-verification against current primary docs ([sub-agents.md](https://code.claude.com/docs/en/sub-agents)) and a direct this-session probe — a non-isolated general-purpose sub-agent ran `git checkout -b` and `git commit --allow-empty`, both exit 0 with no permission gate — **falsified that as a universal claim**: a sub-agent's writes are governed by its tool grant + permission mode, not a blanket deny. The advice (serialize branch-writes, or isolate each writer) is re-grounded in the real hazard — concurrent writers racing on one shared working tree, the same hazard the new [worktree-isolation rule](./isolate-parallel-claude-instances-in-git-worktrees.md) addresses for peer processes — and the status is downgraded Absolute → Pattern accordingly. **Residual uncertainty (not re-tested):** `git push` specifically from a sub-agent, `run_in_background: true` agents, and the web/remote restricted-git-proxy mode — the original 2026-05-23 observation may have held in one of those narrower contexts. Surfaced via PR #425's worktree-rule re-verification; full record in [`docs/research/2026-06-13-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-13-claude-subreddit-scan/README.md) §"Post-scan accuracy re-verification".

---

_Last reviewed: 2026-06-13 by `claude` (premise corrected against primary docs + direct probe)_
