---
name: design-developer-funnel
description: Map a product's developer journey onto the AAARRP pirate funnel (Awareness → Acquisition → Activation → Retention → Revenue/Referral → Product-feedback), define each stage, attach one metric per stage (TTFHW, activation rate, retention), and locate the leak. Reach for this when the user asks "where does our developer funnel leak?" or "map our developer journey". Used by `devrel-strategist` (primary).
---

# Skill: design-developer-funnel

> **Invoked by:** `devrel-strategist` (primary). Consulted by `developer-advocate` to know which stage a piece of content serves.
>
> **When to invoke:** "map our developer journey"; "where do we leak developers?"; "what should we measure at each stage?"; standing up DevRel measurement.
>
> **Output:** an instrumented AAARRP funnel — a definition + one metric per stage, the suspected leak stage, and the experiment to test the fix.

## Procedure

1. **Restate the goal in funnel terms.** Is the problem awareness (no one knows), activation (they try but don't succeed), or retention (they succeed but leave)? Traverse [`../../knowledge/devrel-strategy-decision-tree.md`](../../knowledge/devrel-strategy-decision-tree.md) first.
2. **Lay out the AAARRP stages** for this product (see [`../../knowledge/devrel-metrics.md`](../../knowledge/devrel-metrics.md)):
   - **Awareness** — developers who encounter the product (talk views, content reach).
   - **Acquisition** — they take a first step (signup, repo clone, doc visit).
   - **Activation** — they reach **first hello-world** (the leveraged event; measure **TTFHW**).
   - **Retention** — they come back and build (week-2 / week-4 active).
   - **Revenue / Referral** — they convert or advocate (paid, contributor, ambassador).
   - **Product-feedback** — their friction reaches PM/eng (the loop most teams skip).
3. **Define every stage** with an observable boundary — when is a developer "activated"? Vague stages can't be instrumented.
4. **Attach exactly one metric per stage**, anchored in developer success, not reach. Run the vanity-metric screen: no stage's headline metric is a bare follower/star/view count.
5. **Locate the leak** — the stage with the steepest drop-off relative to benchmark. State it explicitly.
6. **Name the experiment** to test the fix (e.g., "halve TTFHW by removing the API-key step → measure activation-rate lift").

## Worked example

> User: "We get tons of signups from our conference talks but nobody sticks around. Where do we leak?"

- Funnel terms: strong Awareness + Acquisition, weak Activation/Retention — a classic **activation leak**, not an awareness problem.
- Likely cause: a high **TTFHW**. Signups arrive motivated, hit a 40-minute setup, and bounce before first hello-world.
- Metric to instrument: signup → activation rate, with TTFHW as the lever.
- Experiment: cut TTFHW (remove the manual API-key step; ship a one-command quickstart from `author-quickstart-and-sample-app`), measure activation-rate lift over two weeks.
- Motion: this is an **education** problem (golden path), not more **advocacy** (more talks would pour water into a leaky bucket).

## Guardrails
- Never attach a bare vanity metric (followers / stars / views) as a stage's headline — pair it with an activation/retention metric or cut it (see [`../../best-practices/close-the-product-feedback-loop.md`](../../best-practices/close-the-product-feedback-loop.md) and [`../../knowledge/devrel-metrics.md`](../../knowledge/devrel-metrics.md)).
- A stage with no observable definition is not instrumentable — define the boundary before assigning a metric.
- Don't prescribe "more advocacy" for an activation/retention leak; match the motion to the stage via the decision tree.
