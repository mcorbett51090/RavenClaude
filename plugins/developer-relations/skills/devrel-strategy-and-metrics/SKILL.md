---
name: devrel-strategy-and-metrics
description: Design a DevRel program and the metric set that tracks it honestly — segment the developer audience, place the goal in the awareness→activation→advocacy funnel, choose the bets per stage, and pick the activation/time-to-first-success/community-health metrics (not stars/followers). Reach for this on "what should our DevRel program be?" or "which metrics matter?". Used by `devrel-strategist` (primary).
---

# Skill: devrel-strategy-and-metrics

> **Invoked by:** `devrel-strategist` (primary).
>
> **When to invoke:** "what should our DevRel program be?"; "which metrics should we report?";
> "is this a vanity metric?"; designing or course-correcting a DevRel scorecard.
>
> **Output:** a funnel-framed program recommendation + the metric per stage (activation, not vanity)
> + the §6 Output Contract block.

## Procedure

1. **Segment the audience.** Who exactly — what role, what problem, what stack, and *where in the
   funnel* are most of them today? Awareness-heavy vs. activation-leaky vs. advocacy-ready programs
   look completely different.
2. **Place the goal in the funnel.** Use [`../../knowledge/devrel-funnel-and-metrics.md`](../../knowledge/devrel-funnel-and-metrics.md):
   awareness → acquisition → activation → retention → advocacy. Name the stage you're moving.
3. **Pick the bets per stage**, traversing the content/channel trees
   ([`../../knowledge/devrel-strategy-decision-trees.md`](../../knowledge/devrel-strategy-decision-trees.md)).
   Default the spend toward the **activation** stage unless data says it's already healthy.
4. **Choose the metric set** — for each bet, the real metric it moves:
   - activation headline: **time-to-first-success** + activation rate,
   - retention: returning developers (WAU/MAU of the SDK/API),
   - community: resolution rate / unanswered-question rate.
   Demote stars/followers/registrations to *context*. Apply the vanity-vs-real table.
5. **Run the honesty screen** (CLAUDE.md §4): is any headline a vanity metric? Is any artifact
   marketing-at-developers? Is any demo unmaintained?
6. **Frame as a one-page brief** using [`../../templates/devrel-strategy-brief.md`](../../templates/devrel-strategy-brief.md).

## Worked example

> User: "Leadership wants a DevRel program. We have an API and 8k GitHub stars."

- Audience: backend devs integrating the API; most are *aware* (the stars) but few activate.
- Stage to move: **activation** — the gap is sign-up → first working call, not awareness.
- Bets: a runs-as-shipped quickstart sample (activation), a TTFS instrumentation pass, office hours
  for the first integrators (retention).
- Metrics: TTFS median + activation rate as the headline; stars demoted to context.
- Honesty screen: "8k stars" was the old headline — flagged and demoted.

## Guardrails

- A program with no named funnel stage and no real metric is a budget line waiting to be cut — don't ship one.
- If the headline metric can't go *down*, it isn't measuring anything (vanity tell).
- Metrics diagnose the *program*, never stack-rank an advocate (house opinion #7).
