# Scope a skill to one workflow — the description is what triggers it

**Status:** Pattern
**Domain:** Agent design / Skill authoring

**Applies to:** `ravenclaude-core` and every plugin in this marketplace that ships a `skills/` directory

---

## Why this exists

A skill only ever fires because Claude matched the current task against its
**`name` + `description`** — the one tier preloaded into the system prompt for
every installed skill. The `SKILL.md` body loads _after_ the skill is already
firing ([`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md)),
so the description is not documentation — it is the **trigger surface**, the whole
of what decides whether the skill runs at all.

That reframes the most common skill-authoring mistake: building a skill that does
**too much**. A skill scoped to "everything about pull requests" — draft _and_
review _and_ merge _and_ write post-mortems — fails in two opposite directions,
and a lean body fixes neither:

1. **It won't fire when it should.** A compound, abstract description can't be
   cleanly matched to a concrete request. Claude can't tell that "set up the
   project here" is what `manages-my-project` is for, so it routes elsewhere or
   does the work inline — the skill you wrote never loads.
2. **It fires at the wrong moment.** A skill that advertises five things triggers
   on a request that wanted only one of them, dragging its whole body onto the
   desk and crowding the instructions that actually matter for the task.

This is the **scope-and-trigger** axis, and it is distinct from the token-budget
axis its sibling owns: `keep-skill-bodies-lean` keeps the _body_ from bloating the
on-invoke budget; **this rule keeps the _description_ from covering so many
workflows that the skill misfires** — even a perfectly lean body can't rescue a
description that matches the wrong requests. Same tier, different lever.

It is also the **skill-tier counterpart of the marketplace's own agent-routing
discipline**: `AGENTS.md` caps every agent `description` at ≤300 chars precisely
because it is the surface the orchestrator matches on to route to a subagent. A
skill's description is that same surface one tier down. With this marketplace
shipping **~670 `SKILL.md` files across ~100 plugins**, a skill that triggers at
the wrong moment — or never — is a standing tax every consumer who installs the
plugin pays.

## How to apply

**One skill = one workflow.** If the description needs the word "and" more than
once to say what the skill covers, that is the signal to **split it** into focused
skills. "Draft a PR title and body" · "Review an open PR against our checklist" ·
"Write a post-mortem for a failed deploy" are three triggers, so they are three
skills — each of which now matches its own concrete request cleanly.

**Write the description as a trigger, in this shape:**

```
Use when [the user action or context that should fire it].
[What the skill does — one line.]
[A disambiguator, only if a neighbour skill could also match.]
```

Lead with the **when**, and use the concrete keywords a real request would carry.
An abstract description ("manages my project") won't match a concrete ask ("set up
the project here"); a keyworded one ("Use when initializing a new project in this
repo — scaffolds the layout and config") will.

**Name it to match, too.** The `name` is part of the trigger surface. Anthropic's
convention is **verb-ing + noun**, lowercase-with-hyphens (`analyzing-campaigns`,
`generating-questions`) — a name that describes the action helps the match as much
as the description does.

**Test the trigger, don't assume it.** Phrase the task the way a user actually
would and check that it plausibly matches this description alone. If the only way
you can make the skill fire in practice is by naming it explicitly, the
description is too abstract — rewrite it around the real trigger, don't paper over
it in the body (the body isn't loaded yet when the routing decision is made).

## Edge cases / when the rule does NOT apply

- **"One workflow" ≠ "one step."** A genuinely multi-step _single_ workflow — the
  ordered dispatch in [`../skills/spawn-team/SKILL.md`](../skills/spawn-team/SKILL.md),
  a render→see→iterate loop — is still one skill. The split test is "are these
  _separable triggers_?", not "how many steps does it have?"
- **Chaining is not a reason to merge.** A skill can hand off to another skill;
  that's composing focused skills, not an argument for one skill that does
  everything. Keep each trigger sharp and let them chain.
- **This is about the skill's own description, not surface-selection.** _Whether_ a
  capability should be a skill vs. a slash command vs. a hook vs. a subagent is a
  different decision (owned by [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
  and [`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md)).
  Once it _is_ a skill, this rule governs how tightly to scope and describe it.
- **Non-Claude-Code hosts** (GitHub Copilot CLI reads `.claude/skills` too) match
  on the same `name`+`description` surface, so the discipline ports; the exact
  listing-truncation and budget mechanics are host-specific and `[verify-at-use]`.

## See also

- [`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) — the token-budget sibling: this rule keeps the _description_ from covering too many workflows; that one keeps the _body_ from bloating the on-invoke budget. Both are the same "the metadata is the routing tier" mechanic, one axis apart.
- [`./domain-plugins-extend-via-skills-not-parallel-agents.md`](./domain-plugins-extend-via-skills-not-parallel-agents.md) — the mechanism-choice sibling: domain craft ships as a skill a core agent invokes; this rule is how to scope that skill so it fires.
- [`./route-before-spawning.md`](./route-before-spawning.md) — the agent-routing analog: the Team Lead matches a request to a specialist the same way Claude matches a request to a skill; sharp, non-overlapping descriptions make both reliable.
- [`../../../AGENTS.md`](../../../AGENTS.md) — the agent-description token budget (≤300-char cap): the orchestrator-routing tier this rule mirrors one level down.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-09 subreddit scan](../../../docs/research/2026-07-09-claude-subreddit-scan/README.md)).
Grounded against the Anthropic primary docs on Agent Skills
([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview),
[Extend Claude with skills](https://code.claude.com/docs/en/skills)) — the
description "describes both what it does and when to use it" and is what Claude
matches on to decide whether to trigger; the metadata is preloaded while the body
is not; the verb-ing+noun naming convention — and cross-checked against this
repo's own [`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md)
(which owns the body-token axis but states no scope/trigger discipline). The "more
than one _and_ → split" heuristic is practitioner guidance; the description-listing
character cap and metadata-budget specifics are `[verify-at-use]` — Claude Code's
skill-loading mechanics evolve.

---

_Last reviewed: 2026-07-09 by `claude`_
