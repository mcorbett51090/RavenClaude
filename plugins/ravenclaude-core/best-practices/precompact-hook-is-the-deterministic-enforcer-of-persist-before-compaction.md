# The `PreCompact` hook is the deterministic enforcer of "persist before compaction"

**Status:** Pattern
**Domain:** Agent design / Context management / Hooks

**Applies to:** `ravenclaude-core`

---

## Why this exists

Two rules already in this library point straight at each other but stop one step
short of meeting:

- [`./compact-proactively-and-persist-state-before-compaction.md`](./compact-proactively-and-persist-state-before-compaction.md)
  says compaction _discards_ intermediate reasoning, so anything load-bearing (the
  plan, a decision-and-its-rationale, the approaches you already ruled out) must be
  written somewhere durable **before** the window compacts.
- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
  says when a load-bearing rule can be mechanized, it belongs in a hook or CI gate,
  not in prose that the model has to _remember_ to follow.

Put them together and the gap is obvious. "Persist your state before compaction"
as stated today is **advisory**: it fires only if the model (or the user) notices
the window is filling and reacts in time. Auto-compact, by design, fires _late_ and
_without warning_ — at roughly 80%+ of the window — which is exactly the moment the
model is reasoning at its worst and least likely to stop and flush state cleanly.
An advisory "remember to persist first" is the weakest possible guard for the one
event that destroys un-persisted context.

Claude Code exposes the mechanism that closes this: a **`PreCompact`** hook event
that fires _before_ every context compaction, and receives a `trigger` value of
`manual` (the user ran `/compact`) or `auto` (the harness hit the threshold). A
command hook on `PreCompact` runs deterministically whether or not anyone
remembered — it is the "persist before compaction" discipline turned from a prose
rule into a gate. Its bookend, **`PostCompact`** ("after compaction completes"), is
where you verify the flush landed or re-anchor state _after_ the summary replaced
the thread. (Compaction also re-fires instruction loading: `InstructionsLoaded`
carries a `compact` reason, which is how root `CLAUDE.md` re-injects post-compact —
see the imports rule below.)

## How to apply

**Register a `PreCompact` command hook that flushes load-bearing state to disk.**
The hook's job is small and deterministic: append the current plan / open decisions
/ rejected-approaches to a durable file (a run doc, a scratch `PLAN.md`, a commit
message body) so they survive the summarizer's judgement. Because it is a command
hook, it cannot hallucinate the flush away — it runs on the event, every time.

```jsonc
// settings.json (or a plugin's hooks.json)
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto", // fire on the dangerous case: unattended auto-compaction
        "hooks": [{ "type": "command", "command": "scripts/flush-plan-state.sh" }]
      }
    ]
  }
}
```

**Branch on `trigger`.** `manual` means the user is compacting deliberately at a
task boundary and has likely already anchored the summary; `auto` is the
crowded-window case the rule above warns about. Gate the expensive flush on
`trigger == "auto"` so a deliberate `/compact` isn't slowed by a redundant write.

**Keep the hook idempotent and fail-open.** It runs on a hot path (the harness is
about to compact); a slow or erroring hook must not wedge the session. Bound any
network/IO (`--connect-timeout`, `-m`), and exit 0 even on partial failure — the
durable append is best-effort insurance, not a blocker. This is the same
fail-safe discipline the layout/notify hooks in this repo already follow.

**Use `PostCompact` to verify, not to re-do the work.** A `PostCompact` hook (or a
`SessionStart` hook with the `compact` source) can re-inject a pointer to the
flushed file so the post-compact agent knows where its own pre-compaction state
lives, instead of re-exploring a dead end the summary dropped.

## Edge cases / when the rule does NOT apply

- **Short, single-task sessions that never compact don't need the hook.** If the
  work finishes well inside the window, no compaction fires and the hook never runs
  — harmless, but it's the long/multi-task session where it earns its place.
- **The hook is insurance, not a replacement for the discipline.** Anchoring a
  `/compact` summary with explicit "keep:" instructions and committing firm
  decisions as you go (the companion rule) is still the primary move; the
  `PreCompact` hook is the backstop for the `auto` case nobody was watching. Belt
  _and_ braces, matching this repo's hook-**plus**-prose pattern elsewhere.
- **`PreCompact` is a hook event, not a place to _block_ compaction.** Treat it as
  a persist-side-effect, not a veto — the window still needs to compact. Don't try
  to make the hook prevent compaction; make it survive it.
- **Verify the event surface at use.** `PreCompact` / `PostCompact` and the
  `manual`/`auto` trigger values are confirmed against the current Claude Code hooks
  reference (see Provenance), but the hook event set evolves — confirm the event
  name and payload against the settings schema before wiring a consumer repo, the
  same as any other hook (`./prefer-a-deterministic-gate-over-a-prose-rule.md`).
- **Non-Claude-Code hosts have no `PreCompact`.** Copilot/Cursor/Codex manage
  context with their own truncation and expose no equivalent pre-compaction hook;
  there, "persist before the window fills" stays a behavioral discipline. The
  _principle_ ports — mechanize the flush where the host lets you — the specific
  event does not.

## See also

- [`./compact-proactively-and-persist-state-before-compaction.md`](./compact-proactively-and-persist-state-before-compaction.md)
  — the behavioral half this rule mechanizes: _what_ to persist and _why_ compaction
  destroys it. This rule is the _how-to-enforce-it-deterministically_ sibling.
- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
  — the general principle (mechanize load-bearing rules into hooks/gates) that this
  rule is a specific application of.
- [`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md)
  — the re-injection axis: root `CLAUDE.md` re-loads on the `compact` instruction
  reason after a compaction; nested imports don't until re-read.
- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md)
  — the parent concept: the window is finite and compacts when full.
- [`../../../docs/best-practices/hook-authoring.md`](../../../docs/best-practices/hook-authoring.md)
  — the marketplace-wide hook-authoring reference (event list, stdin payload,
  fail-open discipline) this rule's example follows.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-07 subreddit scan](../../../docs/research/2026-07-07-claude-subreddit-scan/README.md)).
It is the deterministic-enforcement sibling the [2026-07-03 scan](../../../docs/research/2026-07-03-claude-subreddit-scan/README.md)
left implicit when it shipped the behavioral "persist before compaction" rule.
Grounded against the Anthropic primary docs on hooks
([Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) — the
`PreCompact` / `PostCompact` events and their `manual`/`auto` trigger values, and
the `InstructionsLoaded` `compact` reason, confirmed 2026-07-07) and cross-checked
against this repo's own [`../../../docs/best-practices/hook-authoring.md`](../../../docs/best-practices/hook-authoring.md)
(which lists `PreCompact` only as a passing "other event," never as a load-bearing
pattern) and the two companion rules above. The exact event payload is
verify-at-use — the hook event set evolves.

---

_Last reviewed: 2026-07-07 by `claude`_
