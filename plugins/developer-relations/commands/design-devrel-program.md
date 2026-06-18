---
description: "Design a DevRel program by segmenting the developer audience, placing the goal in the awareness→activation→advocacy funnel, choosing the bets per stage, and picking the activation/time-to-first-success metrics that track it — never vanity metrics."
argument-hint: "[the product + audience, e.g. 'an API for backend devs; we have 8k stars but low activation']"
---

# Design a DevRel program

You are running `/developer-relations:design-devrel-program`. Build a funnel-framed DevRel program
for `$ARGUMENTS` — the discipline the `devrel-strategist` agent enforces.

## When to use this

Leadership wants "a DevRel program," or an existing one is reported in vanity metrics and needs to be
re-anchored on activation. NOT for executing a single piece of content (that's `plan-sample-app` or
`draft-cfp-abstract`).

## Steps

1. **Segment the audience** — role, problem, stack, and *where in the funnel* most of them are today.
2. **Place the goal in the funnel** ([`../knowledge/devrel-funnel-and-metrics.md`](../knowledge/devrel-funnel-and-metrics.md)).
   Default the spend toward **activation** unless data shows it's already healthy.
3. **Choose the bets per stage**, traversing the content/channel trees
   ([`../knowledge/devrel-strategy-decision-trees.md`](../knowledge/devrel-strategy-decision-trees.md)).
4. **Pick the metric set** — time-to-first-success + activation rate as the headline; demote
   stars/followers/registrations to context (`measure-developer-activation-not-vanity-metrics.md`).
5. **Run the honesty screen** (CLAUDE.md §4) and frame the result as a one-page brief
   ([`../templates/devrel-strategy-brief.md`](../templates/devrel-strategy-brief.md)).

## Guardrails

- A program with no named funnel stage and no real metric is unshippable — don't produce one.
- If the headline metric can't go *down*, it's vanity — replace it.
- Metrics diagnose the program, never an advocate.
