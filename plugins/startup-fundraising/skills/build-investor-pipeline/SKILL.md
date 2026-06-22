---
name: build-investor-pipeline
description: Build a tiered, stage-fit investor pipeline and a warm-intro-first outreach sequence for a founder running a round. Produces a target list scored by stage-fit + thesis-fit + check-size, a warm-path map for each target, and a sequenced outreach plan that builds momentum. Reach for this when the user asks "who should I pitch?", "build my investor list", or "how do I run outreach?". Used by `fundraising-strategist` (primary); coordinated with `pitch-and-narrative-coach`.
---

# Skill: build-investor-pipeline

> **Invoked by:** `fundraising-strategist` (primary). Coordinated with `pitch-and-narrative-coach` (the narrative must fit each target's thesis).
>
> **When to invoke:** "who should I raise from?"; "build my investor list"; "how do I sequence outreach?"; any time a founder is about to start (or is mid-) a raise.
>
> **Output:** a scored target list + a warm-intro path per target + a sequenced outreach plan + the CRM fields to track.

## Procedure

1. **Confirm the round shape first.** Pull stage, instrument, and target raise from the `fundraising-strategist` (or the stages decision tree, [`../../knowledge/fundraising-stages-decision-tree.md`](../../knowledge/fundraising-stages-decision-tree.md)). The pipeline is shaped by *who writes checks at this stage and size* — a Series A lead is noise in a pre-seed.
2. **Build the target universe.** Source from: existing network, angels/operators in the space, stage-appropriate funds, accelerator/syndicate networks, and "who funded comparable companies" (look up recent rounds for adjacent startups). Capture each as a CRM row.
3. **Score each target on three axes.**
   - **Stage-fit** — do they lead/follow at this stage and check size?
   - **Thesis-fit** — does the company match a stated thesis, sector, or recent investment pattern?
   - **Warm-path strength** — is there a strong intro, a weak intro, or only a cold path?
   Tier into **A / B / C** from the combined score.
4. **Map the warm path for every A and B target.** For each, name the best mutual connection and the specific ask of that connection. Warm intros convert far better than cold outreach — spend social capital deliberately.
5. **Sequence for momentum, not volume.** Open with a small "practice" tier (friendly, lower-stakes) to refine the pitch, then move to the highest-conviction A targets while the round has energy. Avoid burning all top targets simultaneously before the pitch is tight. Aim to create a sense of an active, time-boxed process.
6. **Define the CRM fields + cadence.** Minimum columns: firm/partner, tier, stage-fit, thesis-fit, warm path, status (not-contacted → intro-requested → intro'd → meeting → diligence → committed/passed), next action, next-action date, check-size, notes. Set a weekly review cadence; track the *funnel*, not just the list.
7. **Gate outreach on data-room readiness.** Don't go wide before the data room exists — drive [`../prepare-data-room/SKILL.md`](../prepare-data-room/SKILL.md) first so a "send me the deck/data" reply doesn't stall.

## Worked example

> Founder raising a $1.5M pre-seed on a post-money SAFE.

- Target universe → ~40 names: 12 angels/operators in the space, 18 pre-seed funds, 6 accelerator-network connections, 4 syndicate leads.
- Scored & tiered → 8 A (strong thesis-fit + warm path), 18 B, 14 C.
- Sequence → week 1: 3 friendly angels (refine pitch); week 2-3: all 8 A targets via warm intros in parallel to build a time-boxed feel; B tier as A-tier responses come in; C tier as cold backup only if needed.

## Guardrails

- **Stage-fit is the first filter** — a fund that only leads Series A is a waste of a warm intro at pre-seed.
- **Never go wide before the data room and deck are ready** (a stalled "send me materials" kills momentum).
- **Track the funnel, not the list** — a 40-name list with no status column is not a pipeline.
- **The narrative must fit each target's thesis** — coordinate with `pitch-and-narrative-coach`; one generic deck under-converts.
- **This is outreach/pipeline strategy, not legal or financial advice** — instrument terms route to `fundraising-strategist`; binding review to `legal-ops-clm`.
