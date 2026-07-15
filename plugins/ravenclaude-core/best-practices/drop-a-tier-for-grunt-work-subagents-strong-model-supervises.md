# Drop a tier for grunt-work subagents — the strong model supervises, cheap models execute

**Status:** Pattern
**Domain:** Agent design / Multi-agent / Cost

**Applies to:** `ravenclaude-core`

---

## Why this exists

A dispatched subagent (or a workflow agent) **inherits the parent's model by
default** — set no model on the spawn and every worker runs at the orchestrator's
tier. That default is the trap: fan ten agents out to grep files, pull API pages,
or scan logs and, with no `model:` on the spawn, all ten grind at frontier
(Opus-class) cost and latency for work a fast (Haiku-class) model clears just as
reliably. The frontier tokens are spent silently — nothing errors, the run just
costs multiples of what it needed to.

The [`model-selection`](../knowledge/concepts/model-selection.md) concept states the
principle — _"use the smallest model that reliably clears this specific bar, and let
a stronger model check the cheaper ones' work"_ — and Claude Code, the Agent tool,
and the workflow harness all expose a per-agent model knob to act on it. But that
lesson lives in a Learn-tab teaching card; **no consumer-facing best-practice makes
it the dispatch-time discipline** an orchestrator applies when composing the spawn.
This rule is the actionable operationalization — the same knowledge-names-it /
no-rule-teaches-it gap the
[untrusted-config rule](./treat-repo-committed-claude-config-as-untrusted-input.md)
and the [sandbox rule](./the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md)
were each written to close.

## How to apply

**At the moment you compose a subagent dispatch or a workflow fan-out, set the
model explicitly — pick the smallest tier the sub-task's _hardest step_ needs, and
don't let it default-inherit the orchestrator's tier.** Three tiers, matched to the
work:

- **Fast (Haiku-class)** — search/grep, file reads, API-page pulls, log scans,
  classification, routing, summarizing. High-volume routine legwork where
  frontier-grade reasoning is overkill. This is where most fan-out workers belong.
- **Balanced (Sonnet-class)** — everyday reasoning + edits; the sensible default for
  a worker that has to _decide_ something, not just fetch it.
- **Frontier (Opus-class)** — the hardest planning, gnarliest debugging, the
  adversarial verify/judge step. Reserve it; it's the slowest and most expensive per
  token. Keep the **orchestrator** here so the strong model supervises while the
  cheap workers execute.

Concretely, on each spawn:

- **Agent tool** — set the `model` field (`haiku` / `sonnet` / `opus`) on the
  dispatch instead of omitting it. An omitted model inherits the parent; a `fork`
  always inherits the parent regardless.
- **Workflow harness** — pass `opts.model` on `agent()` for the tier, and
  `opts.effort` (`low` … `max`) for the reasoning depth: `low` for the cheap
  mechanical stages, a higher tier only for the hardest verify/judge stage. Both
  inherit the session default when omitted — so an unset `model` on a 100-item
  `pipeline()` stage silently runs all 100 at the session tier.

The tell that this rule was skipped: a fan-out of read-only workers whose token
bill (or wall-clock) is a multiple of the reasoning it actually did.

## The two-sided failure — don't under-tier either

Tiering is a floor as much as a ceiling. Dropping a worker **below** the tier its
hardest step needs is the mirror-image waste: a cheap model that botches the
reasoning produces a plausible-but-wrong result the orchestrator must catch and
redo — the redo costs more than the frontier call you were avoiding. Tier to the
sub-task's **hardest** step, not its average one. When unsure, the concept's
guidance holds: the _smallest model that reliably clears the bar_ — verified against
the actual work, not guessed downward to save tokens.

## Edge cases / when the rule does NOT apply

- **Review / verification panels want _diversity_, not the cheapest tier.** When ≥2
  agents _review_ the same thing, running them all on one backbone lets a single
  model's blind spot pass the whole panel (anti-correlated hallucination). There,
  deliberately run ≥2 _different_ models — the tribunal's model-diversity rule — and
  don't collapse them onto Haiku to save cost. Tier-dropping optimizes independent
  legwork; it is not the rule for a review panel.
- **A one-shot single agent** rarely needs the knob — this is a fan-out discipline.
  The savings compound with worker count; on a single dispatch, just use the
  session default unless the task is clearly routine.
- **Model tiers/ids are `verify-at-use`.** The current Claude line-up (the fast /
  balanced / frontier tiers, and their model ids) evolves; the durable fact is the
  _shape_ — three tiers exist so you can match model to work, and a spawn inherits
  the parent tier unless you set it. Verify the current ids against the
  [Claude models overview](https://docs.claude.com/en/docs/about-claude/models) /
  [Choosing a model — Claude Code](https://code.claude.com/docs/en/model-config) at
  time of use.
- **Cost knob, not a correctness gate.** Getting the tier wrong wastes tokens or
  forces a redo; it does not relax any permission, review, or safety boundary. A
  cheaper worker is still bounded by its `tools:` allowlist and the same posture.

## See also

- [`../knowledge/concepts/model-selection.md`](../knowledge/concepts/model-selection.md) — the concept this rule operationalizes (the three tiers; strong-supervises-cheap; diversity as a safety property).
- [`./delegate-reads-fan-out-keep-branch-writes-in-main.md`](./delegate-reads-fan-out-keep-branch-writes-in-main.md) — the sibling that owns _what_ to fan out (reads freely, writes serialized/isolated); this rule owns _which model_ each fanned-out worker runs.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — how to brief the worker; compose with the tier choice.
- [`./route-before-spawning.md`](./route-before-spawning.md) — pick the right specialist first; the tier is the second axis of the same spawn decision.
- [`../knowledge/model-fallback.md`](../knowledge/model-fallback.md) — the complementary _model-unavailable_ ladder (retry the next model in a tier ladder when one errors); distinct from cost-tiering.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-15 subreddit scan](../../../docs/research/2026-07-15-claude-subreddit-scan/README.md)),
where "assign cheaper/faster models to the subagents doing grunt work, reserve the
capable model for the actual reasoning" recurred as consensus practitioner guidance.
Grounded against this repo's own
[`../knowledge/concepts/model-selection.md`](../knowledge/concepts/model-selection.md)
(the principle at the knowledge tier) and the per-agent model knob verified
this-session against the Agent tool (`model`) and workflow-harness
(`opts.model` / `opts.effort`, which "inherit the main-loop model" when omitted)
schemas. Model tiers/ids are verify-at-use against the
[Claude models overview](https://docs.claude.com/en/docs/about-claude/models); the
durable claim — a spawned agent inherits the parent tier unless you set it, so
right-size the tier at dispatch — is the invariant.

---

_Last reviewed: 2026-07-15 by `claude`_
