# Fan read work out to sub-agents freely — keep branch-mutating work in the main session

**Status:** Absolute rule
**Domain:** Agent design / Multi-agent / Branch management
**Applies to:** `ravenclaude-core`

---

## Why this exists

The Team Lead's most productive pattern is parallel fan-out: spawn multiple sub-agents simultaneously to read code, analyze different branches, or collect data from different parts of the codebase. That pattern works cleanly for reads. It fails silently for writes: background sub-agents spawned by the Team Lead are auto-denied git checkout, commit, and push operations (confirmed behavior — both worktree-isolated and plain non-isolated agents). A Team Lead that fans out branch-mutating work to sub-agents produces agents that appear to run but cannot complete their task, and the silence of the failure (the agent completes without writing anything) is the worst-case error mode.

## How to apply

Partition the delegation decision along a single axis — does this sub-task mutate a branch?

**Fan out freely (reads — no branch mutation):**
- Reading code across multiple branches simultaneously: `git show <ref>:<path>` — safe in parallel.
- Analyzing the same codebase from different angles (security, architecture, performance).
- Gathering data from multiple repos or multiple directories.
- Running tests and reading results (not committing).

**Keep in the main session (writes — branch-mutating):**
- `git checkout`, `git commit`, `git push`, `git merge`.
- Any tool call that creates or modifies a file that will be committed.
- Sequential dependency where sub-agent A's commit must land before sub-agent B reads it.

**Annotated spawn decision:**
```
# Safe — parallel reads
spawn([
    "analyze src/auth/ for security gaps",
    "analyze src/api/ for security gaps",
    "analyze src/db/ for security gaps",
])

# Unsafe — branch-mutating; keep in main session, run sequentially
main_session.do([
    "fix auth gap — commit",
    "fix api gap — commit",
    "fix db gap — commit",
])
```

**Do:**
- Use `git show <ref>:<path>` (not `git checkout <branch>`) when a sub-agent needs to read a specific branch's version of a file — it reads without touching the working tree.
- Sequence branch-mutating work in the main interactive session; parallelize only once the mutations are done and the next round of reads can begin.
- Name this pattern "sending Sleipnir" in user-facing dispatch prose when dispatching for cross-branch reading.

**Don't:**
- Spawn a background sub-agent and ask it to `git commit` or `git push` — it will be auto-denied and the task will silently not complete.
- Use `isolation: "worktree"` expecting it to unlock branch-mutating writes — it also strips `Read` from the working tree, making it worse for the mixed-purpose case.
- Fan out the design phase in parallel and then serially make all the mutations manually — the composition is fine; just keep the mutation in the main session.

## Edge cases / when the rule does NOT apply

- A sub-agent that writes to files in a worktree directory specifically isolated for that purpose (not the main session's working tree) may be able to complete writes inside that worktree — confirm the isolation model before relying on this.
- CI environments where multiple agents are independent processes (not sub-agents of the same Team Lead) have different isolation; this rule governs the sub-agent relationship, not peer-process parallelism.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — "Delegating branch-mutating work" section (the load-bearing rule with the confirmed behavior cite).
- [`./route-before-spawning.md`](./route-before-spawning.md) — the routing tree that precedes any spawn decision.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Delegating branch-mutating work (added 2026-05-23)" and the Sleipnir convention (added 2026-05-31, v0.76.0). Confirmed behavior: background sub-agent git-writes are auto-denied.

---

_Last reviewed: 2026-06-05 by `claude`_
