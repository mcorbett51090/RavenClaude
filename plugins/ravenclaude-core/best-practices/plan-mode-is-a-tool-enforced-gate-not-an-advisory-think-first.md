# Plan Mode is a tool-enforced read-only gate — enter it, don't just ask the agent to "think first"

**Status:** Pattern
**Domain:** Agent design / Workflow / Correctness

**Applies to:** `ravenclaude-core`

---

## Why this exists

Telling an agent to "think before you code" is a **prompt** — advisory, and the
model can talk itself past it and start editing on the next tool call. Claude
Code's **Plan Mode** is a different kind of thing: a **tool-enforced read-only
state**. In Plan Mode the agent can Read / Grep / Glob / search / explore, but the
platform **structurally blocks Write / Edit / Bash-mutation until you approve the
plan** it presents (via `ExitPlanMode`). The constraint lives in the tool, not in
the model's good intentions — so it holds even when the prose rule would have been
skipped. This is the [prefer-a-deterministic-gate-over-a-prose-rule](./prefer-a-deterministic-gate-over-a-prose-rule.md)
principle applied to the explore-then-execute boundary: Plan Mode is the
**deterministic gate** version of "think first."

The cost of skipping it is the "almost right" failure — the agent jumps straight to
editing, solves the *wrong* problem, writes to the *wrong* file, or misses a
dependency that only becomes visible after exploration. The edit "succeeds," passes
a shallow check, and the wrong direction is now baked in; the cleanup dwarfs the
minute the plan would have cost. Under fan-out this compounds: without a planning
gate, parallelism just ships the wrong thing N times faster.

This repo already leans on Plan Mode — the root [`CLAUDE.md`](../../../CLAUDE.md)
carries a "Plan-mode default" (enter it for non-trivial changes, present a
Keep / Update / Deny structure before writing), and the
[`init-agent-ready`](../commands/init-agent-ready.md) template seeds the same line
into a consumer's `CLAUDE.md`. But that is **maintainer/setup guidance, not a
consumer-facing best-practice**: no rule states the *discipline* — that Plan Mode is
a hard gate, when to enter it, and why it beats an advisory prompt. This rule closes
that gap — the same knowledge-names-it / no-rule-teaches-it shape the
[model-tiering rule](./drop-a-tier-for-grunt-work-subagents-strong-model-supervises.md)
and the [untrusted-config rule](./treat-repo-committed-claude-config-as-untrusted-input.md)
were each written to close.

## How to apply

**Enter Plan Mode _before_ the first edit on any change where getting the approach
wrong is expensive — don't rely on an in-prompt "think first."** Concretely, enter
it when:

- the change **spans three or more files**, or touches a **schema / data migration /
  manifest**, or is **security-sensitive**;
- you are **unsure of the approach**, or working in **code you don't know well**;
- the task is ambiguous enough that "solve the wrong problem" is a live risk.

In Plan Mode the agent explores read-only and returns a plan you approve, revise, or
reject **before** any file changes — which is exactly the Keep / Update / Deny shape
this repo already uses for design check-ins. Approve the plan, *then* it edits.

**How it composes with this repo's own gates** (Plan Mode is upstream of all of
them):

- It is the **explore-then-execute** gate; the [`design_checkins`](../CLAUDE.md)
  Keep / Update / Deny flow is the **decision** gate for structural choices. Plan
  Mode is where those decisions surface for approval before code exists.
- It bounds **which problem** the run commits to; the
  [DoD gate](./definition-of-done-gate-makes-done-mean-done.md) bounds **whether the
  work is correct** on the way out. Different ends of the same run.
- For a fan-out, plan **first, in the orchestrator**, then dispatch — so the workers
  execute an approved plan, not N independent guesses (compose with
  [`route-before-spawning`](./route-before-spawning.md) and
  [`focused-task-delegation-beats-full-context-dumps`](./focused-task-delegation-beats-full-context-dumps.md)).

The tell that this rule was skipped: an edit landed, then a *second* run to undo or
redo it because the first solved the wrong problem or hit the wrong file — the
avoidable cost a one-minute read-only plan would have caught.

## Edge cases / when the rule does NOT apply

- **Small, obvious edits skip it.** A one-file change you could describe in a single
  sentence, a typo fix, a read-only question — the planning overhead isn't worth it.
  Reserve Plan Mode for changes where a wrong approach is costly; forcing it on
  trivial edits is friction, not safety.
- **Plan Mode is a _correctness_ gate, not a _safety/permission_ boundary.** It stops
  the agent editing before you approve the direction; it does **not** replace the
  permission posture, the Bash sandbox, or the command-review tribunal. A cheap read
  in Plan Mode is still bounded by `deny`/`ask`/`allow` and the `tools:` allowlist.
  Don't treat "it was in Plan Mode" as a security assurance.
- **Approval is the human's judgment, not a rubber stamp.** The gate's value is that
  you *read* the plan and catch the wrong-problem/wrong-file/missed-dependency error
  before code exists. Auto-approving every plan unread reduces Plan Mode back to the
  advisory "think first" it was meant to replace.
- **Exact activation/keybinding is `verify-at-use`.** How Plan Mode is entered (a
  keybinding, a flag, an auto-enter setting) and the precise tool name evolve across
  Claude Code releases; the durable fact is the _shape_ — a tool-enforced read-only
  state that blocks mutation until you approve a plan. Verify the current mechanic
  against [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)
  at time of use.

## See also

- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md) — the umbrella principle; Plan Mode is the deterministic-gate form of "think before you code."
- [`./definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) — the exit-side correctness gate; Plan Mode is the entry-side one.
- [`./route-before-spawning.md`](./route-before-spawning.md) + [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — plan first, then dispatch the approved plan to workers.
- Root [`CLAUDE.md`](../../../CLAUDE.md) § "Plan-mode default" and the [`init-agent-ready`](../commands/init-agent-ready.md) template — where the maintainer/setup default this rule generalizes already lives.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-16 subreddit scan](../../../docs/research/2026-07-16-claude-subreddit-scan/README.md)),
where "use Plan Mode before you let it edit" recurred as consensus practitioner
guidance — with the load-bearing distinction that Plan Mode is a **tool-enforced
read-only constraint**, categorically different from an advisory "think first"
prompt (verified against [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)
and the practitioner write-ups the scan surfaced, retrieved this session). Grounded
against this repo's own root [`CLAUDE.md`](../../../CLAUDE.md) "Plan-mode default"
(the principle at the maintainer tier) and the
[`prefer-a-deterministic-gate-over-a-prose-rule`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
best-practice it operationalizes. The exact activation mechanic is verify-at-use; the
durable claim — a tool-enforced read-only plan gate beats an advisory in-prompt
"think first," so enter it before the first edit on any costly-to-get-wrong change —
is the invariant.

---

_Last reviewed: 2026-07-16 by `claude`_
