# A skill's body is the gotchas the model doesn't know — not the happy path it does

**Status:** Pattern
**Domain:** Agent design / Skill authoring

**Applies to:** `ravenclaude-core` and every plugin in this marketplace that ships a `skills/` directory

---

## Why this exists

Once a skill has fired, the question is no longer _whether_ it loads but _what
its body should say_. The reflex is to write a tutorial: explain the tool,
restate the happy path, walk the concept from first principles. That reflex
wastes the skill. **The model already knows the happy path** — it can write the
SQL, call the API, format the PDF. What it _can't_ know is the local truth that
isn't in its training data and can't be inferred from the code: the append-only
table whose "current" row is the highest version, not the newest timestamp; the
field called `@request_id` in one service and `trace_id` in another; the staging
endpoint that returns `200` even when the webhook never processed. That
hard-won, non-inferable knowledge is the entire marginal value a skill adds over
the bare model.

Anthropic's own guidance from running _hundreds_ of skills inside Claude Code is
blunt about where the signal is: **"the highest-signal content in any skill is
the Gotchas section,"** built from the failure points Claude actually hits when
using it — and the skill-authoring docs put the same rule from the other side:
**"only add context Claude doesn't already have… the context window is a public
good."** A skill body padded with happy-path exposition the model didn't need is
the worst of both: it spends the on-invoke budget
([`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md))
_and_ buries the two gotchas that would actually have changed the outcome.

This is the **content-value** axis, and it is distinct from its two skill-authoring
siblings. `scope-a-skill-to-one-workflow` governs the **description** (whether the
skill fires); `keep-skill-bodies-lean` governs the **body's length** (how much of
the on-invoke budget it costs). This rule governs **which content earns a place in
that lean body** — and the answer is: the failure modes, not the happy path. A
perfectly-scoped, perfectly-lean skill still adds nothing if the lean words it
spends are words the model already had. With this marketplace shipping **~670
`SKILL.md` files across ~100 plugins**, a skill that re-teaches the baseline is a
standing tax that buys the consumer no reliability in return — the exact profile
of the community skills that score badly in the wild.

## How to apply

**Give every non-trivial skill a Gotchas section — and make it the highest-value
part of the body.** List the ways this task usually goes wrong: the silent
failure, the misleading success signal, the field/name mismatch, the ordering
constraint, the "looks done but isn't." Each entry should be a fact the model
could not have inferred from the code in front of it.

**Apply the "does the model already know this?" test to every line.** If a
sentence restates something a competent model does by default — how to write a
loop, what a REST call is, the tool's happy path — cut it. Keep the sentence only
if it encodes _local, non-obvious, or failure-mode_ knowledge. The body is the
decision spine plus the gotchas, not a manual.

**Grow the gotchas from real runs, not imagination.** The strongest Gotchas
sections are accreted: every time the skill (or a review of its output) surfaces a
new way the task went wrong, add that failure to the list. This is what makes a
skill compound over time — it turns each incident into encoded, reusable expertise
instead of a lesson that has to be re-learned.

**When there are no gotchas, question the skill.** If a task has no non-obvious
failure modes and the model already does it reliably, the skill may be adding
description-tier cost for no marginal value — the honest move is to _not_ ship it,
not to pad it with happy-path prose to look substantial.

## Edge cases / when the rule does NOT apply

- **New _capabilities_ are the exception to "only encode what it doesn't know."**
  A skill that gives the model an ability it lacks — a script that manipulates a
  PDF form, a bundled binary, a domain calculator — legitimately carries the
  usage instructions for that capability. The "cut the happy path" rule is about
  not re-teaching things the model already does; it is not an argument against
  documenting a genuinely new tool the skill provides.
- **Some baseline framing can be load-bearing for _routing within_ the body.** A
  one-line statement of what the workflow is can help the model orient before the
  gotchas; the rule is against _tutorial-length_ happy-path exposition, not
  against a single orienting sentence.
- **Depth still belongs in `references/`, not the body.** A long list of gotchas
  is real content, but if it grows past the lean-body budget, the same
  progressive-disclosure move applies — keep the top few inline and push the long
  tail to a bundled reference the body points at
  ([`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md)).
- **Non-Claude hosts** (GitHub Copilot CLI reads `.claude/skills` too) run on the
  same "the body adds value only where it exceeds the model's baseline" logic, so
  the discipline ports; which specific facts a _different_ backbone already knows
  is model-specific and `[verify-at-use]`.

## See also

- [`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) — the length sibling: that rule keeps the body _short_; this one governs _what the remaining words should be_ (failure modes over happy path). Same body, different lever.
- [`./scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md`](./scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md) — the description sibling: that rule governs whether the skill _fires_; this one governs what its body is _worth_ once it does. Together the three cover trigger → budget → content.
- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the claim-grounding discipline: a gotcha written into a skill is a consequential, durable claim, so it carries the same "cite the check that backs it / mark it `[verify-at-use]`" bar.
- [`./scope-the-reviewer-to-correctness-or-it-manufactures-work.md`](./scope-the-reviewer-to-correctness-or-it-manufactures-work.md) — the same "signal over volume" instinct one surface over: a reviewer scoped to real defects, a skill body scoped to real failure modes.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-11 subreddit scan](../../../docs/research/2026-07-11-claude-subreddit-scan/README.md)).
Grounded against two Anthropic primaries: the engineering blog
[Lessons from building Claude Code: How we use skills](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills)
— which states, from running hundreds of skills in Claude Code, that _"the highest-signal
content in any skill is the Gotchas section"_ built from _"common failure points that
Claude runs into,"_ with concrete examples (an append-only `subscriptions` table whose
current row is the highest version not the newest `created_at`; a `@request_id`/`trace_id`
field-name mismatch across services; a staging endpoint that returns `200` when the Stripe
webhook never processed) — and the
[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
doc, which states _"only add context Claude doesn't already have… the context window is a
public good"_ (both retrieved 2026-07-11). Cross-checked against this repo's own
[`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md)
(which owns body-length but states no content-selection discipline) and
[`./scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md`](./scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md)
(which owns the description/trigger axis). The "grow gotchas from real runs" and
"73% of audited community skills scored below 60" observations are practitioner
guidance and `[verify-at-use]`; Claude Code's skill-loading mechanics evolve.

---

_Last reviewed: 2026-07-11 by `claude`_
