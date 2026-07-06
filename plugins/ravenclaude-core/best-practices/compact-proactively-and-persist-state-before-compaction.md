# Compact proactively, and persist load-bearing state before compaction

**Status:** Pattern
**Domain:** Agent design / Context management

**Applies to:** `ravenclaude-core`

---

## Why this exists

The context window is finite, and when it nears full the harness **compacts** —
it summarizes the older turns into a compact recap and continues with that plus
the recent turns ([`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md)).
That concept card tells you compaction _happens_. This rule is the actionable
discipline it implies, and it has two halves that are easy to get wrong in
opposite directions.

**Half one — compact _proactively_, not reactively.** Auto-compact fires late, at
roughly 80%+ of the window (for a 200K model, ~167K tokens, with a ~20K reserve
kept so the model has room to write the summary). By the time it fires the session
is already crowded — the "context rot" where far-back details get crowded out has
usually started, so the model is reasoning at its _worst_ right when the summary
that will define the rest of the session gets written. Running `/compact` yourself
**at a task boundary** (a feature shipped, a bug fixed) compacts while the context
is clean and the summary is sharp. The cheap first move is often not to compact at
all: `/context` shows what's actually consuming the window, and disabling an unused
MCP server (its schemas ride in the window —
[`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md))
can buy back enough room to skip the compaction entirely.

**Half two — compaction _discards_, so persist first.** A compact recap is a
_summary_. Intermediate reasoning, the approaches you tried and rejected, and
verbose tool output do **not** survive it — only what the summarizer judged worth
keeping. A plan, a decision-and-its-rationale, or a "we ruled X out because Y" that
lives **only in the conversation** is gone after compaction, and the post-compact
agent will happily re-explore the dead end you already killed. Anything
load-bearing has to be written somewhere durable — a file, a commit, a test —
_before_ the window compacts, not recalled from a summary after.

## How to apply

**Compact at task boundaries, not at the 95% cliff.** When you finish a unit of
work and are about to switch tasks, `/compact` (or `/clear` if the next task is
truly unrelated) while the context is still clean — don't wait for auto-compact to
fire mid-task. Watch the `/context` gauge; treat "getting cramped" as the signal to
_persist-then-compact_, not to push on until the harness forces it.

**Anchor the summary — tell compaction what to keep.** `/compact` takes free-form
preservation instructions; use them so the load-bearing facts survive the
summarizer's judgement:

```
/compact Keep: the list of modified file paths, the decision to use Postgres over
SQLite and why, and the two approaches we already rejected (global lock — too slow;
optimistic retry — lost updates). Drop the exploratory greps.
```

For a preference that should hold on **every** compaction in a repo, put it in
`CLAUDE.md` (e.g. "When compacting, always preserve the full list of modified files
and the test/validation commands") — but treat that as a _tone-setter_, not a
guarantee: `CLAUDE.md` is advisory
([`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)).

**Persist load-bearing state to disk _before_ the window fills.** The durable
version of "don't lose the plan to compaction" is not a better `/compact` string —
it's writing the plan/decision to a doc, a commit message, or a test the moment it's
firm, so it's recoverable regardless of what the summary keeps. This is the same
desk-not-filing-cabinet discipline the context-budget rules apply to _input_ cost,
applied here to _survival_ across a compaction.

## Edge cases / when the rule does NOT apply

- **A short, single-task session doesn't need managed compaction.** If you'll
  finish well inside the window, forcing an early `/compact` just adds a
  summarization round-trip. The discipline is for long or multi-task sessions where
  the window is a real constraint.
- **`/compact` vs `/clear` are different tools.** `/compact` keeps a summary of the
  thread; `/clear` starts fresh with nothing carried. Use `/clear` when the next
  task shares no context with the last (a fresh, sharply-prompted session beats a
  long one full of failed attempts); use `/compact` when continuity matters.
- **Microcompact is a complement, not a substitute.** The lightweight pass that
  prunes stale tool output as you go reduces _how often_ you hit a full compaction;
  it doesn't remove the need to persist load-bearing state before one.
- **This is about the model's context, not durable memory.** Facts that must
  outlive the _session_ (not just survive a mid-session compaction) belong in
  `CLAUDE.md`, committed files, or the memory system regardless — compaction
  hygiene is the in-session layer beneath that.
- **Non-Claude-Code hosts** manage context differently (Copilot/Cursor/Codex have
  their own truncation/summarization); the _principle_ — persist load-bearing state
  rather than trust it to survive summarization — ports, the `/compact` mechanics do
  not.

## See also

- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md) — the parent concept: the window is finite and compacts when full. This rule is the actionable discipline for _when_ to compact and _what to save first_.
- [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md) — the input-cost sibling: right-size what rides in the window so you compact _later_ (or not at all); `/context` is the shared instrument.
- [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) — the recovery-layer sibling: a commit is durable state that survives a compaction (and a `/rewind`); "persist before compaction" is why that matters.
- [`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md) — the "what re-injects after `/compact`" axis (root `CLAUDE.md` re-injects; nested ones don't until re-read), distinct from this rule's "what you must persist before compaction."

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-03 subreddit scan](../../../docs/research/2026-07-03-claude-subreddit-scan/README.md)),
where it was the candidate the [2026-07-02 scan](../../../docs/research/2026-07-02-claude-subreddit-scan/README.md)
explicitly deferred as "the strongest next candidate." Grounded against the
Anthropic primary docs on context management
([Best practices](https://code.claude.com/docs/en/best-practices)) and cross-checked
against this repo's own [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md)
(which describes compaction but states no discipline for it). The specific
thresholds (auto-compact ~80%, the ~20K summary reserve, the "compact at ~60% / at
task boundaries" practitioner guidance) are verify-at-use — Claude Code's compaction
behavior evolves.

---

_Last reviewed: 2026-07-03 by `claude`_
