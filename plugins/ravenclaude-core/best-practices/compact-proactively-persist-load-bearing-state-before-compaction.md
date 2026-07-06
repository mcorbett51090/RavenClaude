# Compact proactively — and persist load-bearing state *before* compaction, because compaction discards intermediate reasoning

**Status:** Pattern
**Domain:** Session hygiene / context management / Guardrails
**Applies to:** `ravenclaude-core` (any long-running, multi-step, or unsupervised session)

---

## Why this exists

Every long session eventually hits the context ceiling, and when it does the harness **compacts** — it summarizes the older turns into a compact recap and continues with that plus the recent turns. The repo already teaches *that this happens* ([`knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md): _"When it's nearly full, the harness compacts … the work isn't lost, but it's now a summary"_) and it teaches how to keep the window *small* ([`mcp-tool-context-is-a-budget-...`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md), [`claude-md-imports-organize-...`](./claude-md-imports-organize-they-dont-shrink-context.md)). What no rule states is the **discipline for the compaction event itself** — and it has a non-obvious, sharp edge that bites hard in exactly the sessions this repo cares about (multi-agent runs, overnight loops, long refactors):

**Compaction is lossy summarization, and what it drops is the reasoning, not just the chatter.** A summary keeps *what was decided*; it discards the *intermediate reasoning* that got there — the approaches tried and rejected, the verbose tool output, the "we ruled out X because Y" that keeps the agent from re-litigating a settled question. Anthropic's own guidance treats the recap as lossy by design: `/compact Focus on …` and a `# Compact instructions` block in `CLAUDE.md` exist precisely to tell the summarizer *what to preserve* — which only makes sense because everything you don't name is at risk. The community lesson is blunter: after an auto-compaction the agent often asks _"what are we working on?"_ and re-explores ground it already covered, because the plan lived **only in the conversation** and the conversation is now a paragraph.

Two failure modes follow, and both are avoidable:

1. **Reactive compaction** — letting the window hit ~95% and auto-compact mid-thought. The summary is taken at the worst possible moment (deep in a sub-task, reasoning half-formed) and the recap quality is correspondingly poor.
2. **State that lived only in chat** — a decision, a plan, a rejected-approaches list, or a task's acceptance criteria that was never written anywhere durable. Compaction summarizes it into vagueness (or drops it), and the agent silently loses the thread.

The fix is the same one-liner the repo already applies to session *end* (`/wrap`, run-artifacts) and to cross-session recovery (commits, not `/rewind` — see [`checkpoints-are-the-recovery-layer-...`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md)), pulled one step earlier: **write the load-bearing state to disk before the window forces the summary, and compact on your terms rather than the ceiling's.**

## How to apply

Treat compaction like a save point you *schedule*, not a crash you *survive*.

**Do:**

- **Persist load-bearing state to a durable surface the moment it's decided — not at compaction time.** The plan, the design decision, the rejected approaches (with the *why*), and the task's acceptance criteria belong in a file (`CLAUDE.md`, a committed doc, a `.ravenclaude/runs/<id>/` artifact, or a failing test that encodes the intent) — the same "reference artifacts, not full history" discipline the constitution's Context & Session Hygiene section already names. A written decision survives compaction verbatim; a spoken one becomes a summary of a summary.
- **Compact proactively, before quality degrades — not at the ceiling.** Reach a natural boundary (a sub-task done, a phase closed) with headroom to spare and compact *there*, so the recap is taken when the reasoning is complete and clean. Watch the budget (a context-usage status line / `/context`) so you choose the moment.
- **Tell the summarizer what to keep.** When you do compact, name the load-bearing content (`/compact Focus on the migration plan and the failing test`), or set a persistent `# Compact instructions` block in `CLAUDE.md` for the session's recurring priorities. Everything you don't name is the collateral.
- **For unrelated work, prefer `/clear` over letting one long session accrete** — a fresh window with a sharp prompt beats a compacted one full of a prior task's summary (the `/clear`-hygiene lesson, applied at the compaction boundary).

**Don't:**

- **Don't rely on the auto-compaction recap to carry a decision you never wrote down.** If losing a line from the summary would make the agent redo work or re-litigate a settled call, that line was load-bearing and belonged in a file *before* the summary was taken.
- **Don't treat compaction as free or lossless.** It preserves the gist and discards the reasoning; an agent that "forgets why we ruled out approach X" after a compaction will cheerfully try X again.
- **Don't wait for the 95%-full auto-trigger by default.** That's the reactive mode — the recap is worst exactly when the window is most stressed.

## Edge cases / when the rule does NOT apply

- **Short, single-task sessions** that never approach the ceiling don't need scheduled compaction — the ceremony is for long/multi-step/unsupervised runs where the window *will* fill. Applying it to a five-minute task is noise.
- **The persistence half is universal; the `/compact` and `/clear` half is Claude-Code-specific.** Under Copilot CLI / other hosts the exact command names differ or are absent, but "write load-bearing state to disk before the context is summarized" holds on any harness with a finite window — it's a property of context windows, not of one tool. (Same split as the checkpoints rule: the durable-anchor half is portable, the `/rewind` half isn't.)
- **This is not a substitute for commits.** Compaction is *within-session* context pressure; a commit is the *cross-session* anchor that survives a fresh session or a reclaimed remote container. Persist-before-compact keeps the current session coherent; commit keeps the work at all. They compose — see the checkpoints rule.

## See also

- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md) — the mechanism this rule acts on ("when it's nearly full, the harness compacts … it's now a summary"); the desk-not-filing-cabinet model.
- [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md) · [`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md) — the two rules that keep the window *small* (reduce what fills it); this rule governs *what happens when it fills anyway*.
- [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) — the sibling within-session-vs-durable distinction (`/rewind` vs commit); persist-before-compact is the same "write the durable anchor" move applied to the compaction boundary.
- The constitution's **Context & Session Hygiene** + **Run Artifacts** sections ([`../CLAUDE.md`](../CLAUDE.md)) — "reference artifacts, not full history" and the `.ravenclaude/runs/<id>/` substrate are the *where* this rule writes load-bearing state to.

## Provenance

Distilled from a 2026-07-06 scan of Claude Code community discussion (r/ClaudeAI + aggregations of it — direct subreddit reads are blocked to the Anthropic crawler, so this is the documented web-search fallback), **explicitly promoted from the 2026-07-02 scan's deferred "next-scan candidate"** ([`docs/research/2026-07-02-claude-subreddit-scan/README.md`](../../../docs/research/2026-07-02-claude-subreddit-scan/README.md) §3, H2). Grounded in [Anthropic's manage-costs / compaction guidance](https://code.claude.com/docs/en/costs) (auto-compaction summarizes conversation history near the limit; `/compact Focus on …` and a `CLAUDE.md` compact-instructions block tell it what to preserve) and cross-checked against this repo's own [`knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md). Community corroboration that the problem is real and painful: the recurring _"what are we working on?"_ post-compaction thread and the `anthropics/claude-code` issue [#25999 "Persistent state across context compaction"](https://github.com/anthropics/claude-code/issues/25999), plus the third-party memory-layer tools built to survive compaction (evidence the gap is felt, not that we should ship such tooling — the domain-neutral principle is *persist load-bearing state yourself*, and this repo's run-artifacts substrate already IS that surface). The repo taught *that* compaction happens and how to keep the window small, but had **no** consumer-facing rule on the compaction *event* itself — this closes that gap. Research + panel record: [`docs/research/2026-07-06-claude-subreddit-scan/README.md`](../../../docs/research/2026-07-06-claude-subreddit-scan/README.md).

---

_Last reviewed: 2026-07-06 by `claude`_
