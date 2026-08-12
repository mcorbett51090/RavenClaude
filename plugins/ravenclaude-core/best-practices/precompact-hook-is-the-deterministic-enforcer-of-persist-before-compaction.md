# `PreCompact` is not a persistence gate — compaction does not destroy the transcript

**Status:** Pattern
**Domain:** Agent design / Context management / Hooks

**Applies to:** `ravenclaude-core`

> ⛔ **CORRECTED 2026-08-12. This file previously prescribed the opposite of what it now says.**
> It told you to register a `PreCompact` command hook that "flushes the plan / open decisions /
> rejected-approaches to disk," on the premise that compaction destroys them. **Both halves were
> wrong**, and one was wrong in the dangerous direction:
>
> | The old claim | Reality | Consequence of believing it |
> |---|---|---|
> | *"`PreCompact` … is **not** a place to **block** compaction. Treat it as a persist-side-effect, not a veto."* | `PreCompact` **CAN block** — exit 2 blocks compaction `[docs-verified 2026-08-12]` | You write a hook without realising a non-zero exit **wedges a session whose window is already full** |
> | *"A plan, a decision-and-its-rationale, or a 'we ruled X out because Y' that lives only in the conversation **is gone after compaction**"* | Gone from the **window**. **Retained in full on disk** — the transcript is append-only across a compaction | You build a hook to save data that was never at risk |
>
> The filename is retained deliberately: six files link to it, two of them dated research records this
> repo's convention says not to rewrite. **The name asserts the retracted claim; the content is the
> correction.**

---

## What compaction actually does

Compaction **appends**. It does not truncate, rewrite, or delete. The session transcript at
`~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` keeps every turn from before the boundary and
every turn after it, in one file.

Measured against this repo's own transcripts `[verified 2026-08-12]`:

- **44** `compact_boundary` records across this project's transcripts — auto-compaction is frequent,
  not hypothetical.
- One 12,398-line transcript has its first boundary at **line 4031**. Before it: 1,207 assistant and
  735 user turns. After it: 2,923 assistant and 1,570 user turns. **The pre-compaction half is still
  there.**
- Every content-block type survives, including the one you would most expect to be dropped:
  **939 `thinking` blocks**, alongside 1,253 `text`, 2,136 `tool_use`, and 2,175 `tool_result`.
- The boundary record itself carries the accounting:

  ```jsonc
  {"subtype":"compact_boundary","compactMetadata":{
     "trigger":"auto","preTokens":1000599,"postTokens":32828,
     "cumulativeDroppedTokens":967771,"durationMs":116872,
     "preservedSegment":{"headUuid":"…","anchorUuid":"…","tailUuid":"…"}}}
  ```

  A 1M-token context compacted to 33K, and the transcript records **by UUID** exactly which segment
  survived into the new window. That is better provenance than any hook could write, and it is
  already there.

**So the loss is addressability, not durability.** The post-compaction agent does not lack the data.
It lacks the knowledge that the data exists, where the boundary fell, and that reading past it is an
option. Nothing a `PreCompact` hook writes changes that, because the hook's output is not injected
anywhere (see below).

## How to apply

**Do not write a `PreCompact` "flush state" hook.** Beyond the premise being false, the remedy is not
mechanizable: a command hook receives a JSON payload on stdin and nothing else
([`hook-authoring.md`](../../../docs/best-practices/hook-authoring.md) § "Read the stdin payload").
It has **no access to the model's plan, its open decisions, or the approaches it ruled out.** A
`flush-plan-state.sh` can append a timestamp and a file path; it cannot append the thing you wanted
saved. That is this repo's own
[gate-that-asserts-nothing](./a-policy-hook-only-gates-if-it-fails-closed.md) failure mode — it runs,
exits 0, reports success, and checks nothing.

**If you register a `PreCompact` hook for some other reason, exit 0 unconditionally.** This is the
load-bearing safety note and it inverts the usual posture:

```bash
#!/usr/bin/env bash
# PreCompact: exit 2 BLOCKS compaction. Compaction fires when the window is
# near-full, so blocking it wedges the session. Fail OPEN, always.
trap 'exit 0' EXIT
set -uo pipefail   # NOT -e: an aborted pipeline must not become a non-zero exit
```

[`a-policy-hook-only-gates-if-it-fails-closed.md`](./a-policy-hook-only-gates-if-it-fails-closed.md)
governs **policy** hooks, where a fail-open gate is no gate. `PreCompact` is not a policy hook — there
is no posture under which "prevent this session from compacting" is the safe answer, so its correct
posture is the opposite. Do not let the sibling rule's title pull you the wrong way here.

**Recover the pre-compaction record by reading it, not by having saved it.** The transcript path
arrives in the hook payload as `transcript_path`, and the boundary is greppable:

```bash
# where did the last compaction fall, and what did it drop?
grep -n 'compact_boundary' "$transcript_path" | tail -1
# search the pre-boundary half for the decision the summary dropped
head -n "$boundary_line" "$transcript_path" | grep -i 'ruled out\|rejected\|decided against'
```

**Re-anchor at `SessionStart`, not `PreCompact` — it is the only surface whose output reaches the
model.** Claude Code writes hook stdout to the debug log for most events; the exceptions are
`UserPromptSubmit`, `UserPromptExpansion`, and `SessionStart`, whose stdout is added as context
`[docs-verified 2026-08-12]`. `SessionStart` takes a `compact` matcher, so a post-compaction pointer
is one hook away — and it is the *only* placement that works:

```jsonc
{ "hooks": { "SessionStart": [ { "matcher": "compact", "hooks": [ /* … */ ] } ] } }
```

**Keep persisting decisions to durable files — for the right reason.** The companion rule's advice to
write plans and decisions into `docs/decisions/` and run artifacts is still correct, but *durability*
was never the justification. The justifications are **legibility** (nobody greps a 12,000-line JSONL
by choice) and **reach** — a transcript is host-private and does not cross to a teammate, to CI, or to
another CLI, which is exactly what `AGENTS.md` § "Where work files go" is about. Write it down because
someone else has to read it, not because it will otherwise be destroyed.

## Edge cases / when the rule does NOT apply

> control: the same probe run against a known-present and a known-absent host store ->
> `~/.claude/projects` = 227 transcripts / 57 `compact_boundary`; `~/.copilot` = 3 session `.jsonl` /
> 0 `compact_boundary`; `~/.codex` and `~/.cursor` absent. The probe discriminates in both directions,
> so the host scoping below is measured rather than assumed.

- **`PostCompact` and `SessionStart(compact)` overlap.** Both fire around the same boundary; only
  `SessionStart`'s stdout is injected. Prefer it for anything the model must see.
- **Other hosts: measured for Copilot, `[unverified]` elsewhere — do not port the reassurance.**
  `PreCompact` is a Claude Code event and the append-only transcript is a **Claude Code** property.
  Per the control above, Copilot writes **no** Claude-shaped boundary record; Codex and Cursor are not
  installed on this machine, so nothing is claimed about them. What the control establishes is that
  the probe discriminates — **not** that Copilot discards history in its own format, which was not
  measured. On any non-Claude-Code host, "persist load-bearing state" keeps a real durability motive
  until someone measures otherwise.
- **Verify the event surface at use.** The event set evolves. This correction exists because the
  previous version of this file carried that same warning, and thirteen months passed before anyone
  acted on it.

## See also

- [`./compact-proactively-and-persist-state-before-compaction.md`](./compact-proactively-and-persist-state-before-compaction.md)
  — the companion behavioral rule. Its *when to compact* half is unaffected; its "gone after
  compaction" framing is scoped to the **window** and is corrected here for the **disk**.
- [`./a-policy-hook-only-gates-if-it-fails-closed.md`](./a-policy-hook-only-gates-if-it-fails-closed.md)
  — the fail-closed rule for **policy** hooks, and the explicit exception `PreCompact` makes to it.
- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
  — mechanize a load-bearing rule *when it is mechanizable*. This file is the counter-example: the
  rule was real, the mechanization was unavailable, and reaching for a hook anyway would have shipped
  an inert one.
- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md) — the parent
  concept: the window is finite and compacts when full.

## Provenance

Originally distilled from the [2026-07-07 subreddit scan](../../../docs/research/2026-07-07-claude-subreddit-scan/README.md)
and grounded against the Anthropic hooks docs as they read then.

**Corrected 2026-08-12** after the prescription was reviewed before being implemented in this repo.
Two independent checks falsified it: the current [hooks reference](https://code.claude.com/docs/en/hooks)
(retrieved 2026-08-12) lists `PreCompact` as **able to block** (exit 2 → blocks compaction) and lists
the injected-stdout events as `UserPromptSubmit` / `UserPromptExpansion` / `SessionStart` only; and a
direct read of this project's own transcripts showed the pre-compaction history retained in full
(counts and `compactMetadata` above). The original file's own closing caveat — *"verify the event
surface at use"* — is what the review was honouring; it was correct to write, and thirteen months
passed before anyone ran it.

---

_Last reviewed: 2026-08-12 by `claude`_
