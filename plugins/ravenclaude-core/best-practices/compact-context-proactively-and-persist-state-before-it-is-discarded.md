# Compact context proactively, and persist load-bearing state before it's discarded

**Status:** Pattern
**Domain:** Agent design / Context management

**Applies to:** `ravenclaude-core`

---

## Why this exists

Auto-compaction is a safety net, not a plan. Claude Code "summarizes conversation
history when approaching context limits"
([Anthropic — Manage costs](https://code.claude.com/docs/en/costs)) — but by the
time it fires, the window is already near-full, so two things have quietly gone
wrong at once: the model has been reasoning in a **crowded, degraded** window for
a while, and the summary that replaces the old turns is itself generated **under
that same pressure**, from a window that no longer holds everything cleanly. You
inherit a summary made at the worst possible moment.

The fix the community converged on is to treat compaction as a **deliberate,
early** move rather than an automatic, late one — compact *before* quality
degrades (a widely-cited practitioner heuristic is **around ~60% context
utilization**, while the model still has full, uncompressed access to everything
and the summary it writes is based on complete information), not at the 90-95%
auto-trigger. The exact percentage is a rule of thumb, not an Anthropic-published
threshold; the load-bearing part is *proactive, not reactive*.

The second half is the one that actually loses work. **Compaction discards the
intermediate reasoning** — the approaches you tried and rejected, the verbose tool
output you already distilled a conclusion from, the "why we're not doing X" that
never got written down. A decision that lives *only* in the conversation is gone
the moment the window compacts. This repo's own
[`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md)
states the mechanism plainly: after compaction the older work "is now a
*summary* — which is why durable facts belong in `CLAUDE.md` or committed files,
not just in chat." So anything load-bearing must be **written to the filesystem
before** the window compacts, not trusted to survive inside it.

## How to apply

**Compact on your schedule, not the harness's.** Watch the budget —
[configure the status line to show context usage](https://code.claude.com/docs/en/statusline#context-window-usage)
or run `/usage` / `/context` — and run `/compact` yourself at a natural breakpoint
(a finished sub-task, a green test) while there's still headroom, rather than
letting the auto-trigger catch you mid-thought at the limit.

**Tell `/compact` what to keep.** A bare `/compact` summarizes generically. Pass
preservation instructions so the parts you'll need survive:

```text
/compact Preserve the chosen architecture and the two rejected alternatives,
the failing test names, the files in scope, and the open TODOs.
```

For a standing project policy, put it in `CLAUDE.md` so every compaction honors it
([Anthropic — Manage costs](https://code.claude.com/docs/en/costs)):

```markdown
# Compact instructions

When compacting, preserve: active architectural decisions and the alternatives
rejected (with the reason), in-flight bugs and their repro, the file scope of the
current task, and any active constraint.
```

**Persist the load-bearing state to a file first — that's the real durability
layer.** Before a long session compacts, write the schema / interface signature /
decision record / outstanding-tasks list to a committed file or a scratch note.
`/compact` (and `/rewind`) operate on the conversation; a fact on disk is
unaffected by either. This is the same discipline the
[`./give-the-agent-a-verification-signal-it-can-read.md`](./give-the-agent-a-verification-signal-it-can-read.md)
and [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md)
rules apply elsewhere: put the thing that must survive somewhere the model can
re-read, not somewhere the harness can summarize away.

**Keep the desk clear so compaction is rarely needed at all.** The cheapest
compaction is the context you never loaded. `/clear` between unrelated tasks;
delegate verbose operations (test runs, log parsing, doc fetches) to subagents so
the raw output stays in *their* window and only a summary returns; and move
specialized instructions out of `CLAUDE.md` into on-demand skills
([`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md)
covers why splitting alone doesn't help). Proactive compaction is the release
valve; keeping the window lean is what keeps you off it.

## Edge cases / when the rule does NOT apply

- **Short, single-task sessions don't need this.** If you're in and out before the
  window is a quarter full, manual compaction is ceremony — just work. The rule is
  for **long or multi-phase** sessions where the window genuinely fills.
- **The ~60% number is a heuristic, not a gate.** Don't wire a hard "compact at
  60%" trigger and treat it as law — the right moment is *a natural breakpoint with
  headroom*, which depends on how chatty the task is. Some tasks want compaction
  at 40%, some comfortably run to 80%. Watch quality, not just the percentage.
- **Compaction is lossy by design — don't rely on it for anything you can't
  reconstruct.** If a fact is expensive to re-derive (a hard-won repro, a specific
  API response, a decision rationale), it belongs in a file *regardless* of where
  the window sits. Compaction preservation instructions reduce the loss; they don't
  eliminate it.
- **`/compact` ≠ `/clear` ≠ `/rewind`.** `/compact` summarizes-and-continues (keeps
  the thread, shrinks it); `/clear` discards the conversation entirely (fresh
  start); `/rewind` restores a prior checkpoint (undo). Reaching for the wrong one
  loses different things — see
  [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md).
- **Non-Claude-Code hosts.** The *principle* (compact early; persist durable state
  to disk) ports to any long-context agent; the specific commands (`/compact`,
  `/usage`, the `# Compact instructions` CLAUDE.md block) are Claude Code surface.

## See also

- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md) — the mechanism: a finite window that fills and then compacts to a summary, which is *why* durable facts belong in files.
- [`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md) — the sibling context-budget rule: splitting a `CLAUDE.md` with `@imports` organizes but doesn't shrink cost; prune to actually reduce the load compaction has to manage.
- [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md) — right-sizing the enabled tool set so the window starts smaller and hits the compaction threshold later.
- [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) — `/rewind` vs. a commit; the recovery-layer companion to this context-durability rule.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — delegating verbose work so raw output never enters the main window in the first place.

## Provenance

Surfaced by the recurring Claude-community scan (the
[2026-07-05 subreddit scan](../../../docs/research/2026-07-05-claude-subreddit-scan/README.md)),
where it was the finding an earlier scan
([2026-07-02](../../../docs/research/2026-07-02-claude-subreddit-scan/README.md), H2)
had explicitly flagged as "the strongest next candidate" and deferred under the
one-rule-per-scan discipline. Grounded against
[Anthropic — Manage costs effectively](https://code.claude.com/docs/en/costs)
(auto-compaction summarizes near the limit; `/compact <instructions>` and the
`# Compact instructions` CLAUDE.md block customize what's preserved; `/clear`,
subagent delegation, and CLAUDE.md→skills all keep the window small) and
cross-checked against this repo's own
[`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md)
(post-compaction the older work is a summary, so durable facts belong in files).
The **proactive-not-reactive** framing and the **~60% utilization** heuristic are
community practitioner consensus (context-management write-ups aggregating
r/ClaudeAI discussion), read via unrestricted web search — **not** a direct
subreddit read (Reddit is blocked for the Anthropic crawler this session; the
sanctioned [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) route needs
`REDDIT_CLIENT_ID`/`SECRET`, still unset). Treat the percentage as a rule of
thumb, not an Anthropic-published threshold.

---

_Last reviewed: 2026-07-05 by `claude`_
