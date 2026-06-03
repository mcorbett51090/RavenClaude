---
name: renewal-workflow-design
description: "Design the renewal-risk workflow and save-play triggers from a health tier plus renewal proximity: the risk = proximity × engagement rule, the renewal watchlist surface, the trigger-to-play mapping, the expand/maintain/recover decision, and the who-do-I-call-today actionability bar. Reach for this skill when designing how at-risk renewals surface and what fires when, or when a renewal that should be safe shows no movement. Domain-neutral — generalized from the EdTech renewal-play-design pattern; no vertical assumptions."
---

# Skill: Renewal-Workflow Design

A renewal is earned in the months before the date, not negotiated in the final week. This skill designs the **workflow** that surfaces at-risk renewals early and the **triggers** that fire a save motion while there's still time to act — keyed off the health tier and renewal proximity.

This is the **domain-neutral** generalization of the renewal-play-design pattern — the reusable renewal-risk mechanics, with vertical specifics (K-12 budget cycles, academic calendars, segment overlays) stripped out. Used by `cs-analytics-architect` (designs the renewal surface into the model) and `churn-signal-analyst` (defines the triggers). Pairs with [`../health-tier-design/SKILL.md`](../health-tier-design/SKILL.md).

## The core opinion this skill encodes

> **Renewal proximity alone is not risk. Risk = proximity × engagement.**

Every account eventually reaches 90 days to renewal — that, alone, is not a signal. Proximity is the **gate** that sets urgency; **engagement** (usage trend, health-score trend, support/escalation signal, champion presence) is what turns proximity into risk. The workflow keys off the *product* of the two, never proximity by itself.

A renewal you have to *convince* at T-7 is one you already lost the narrative on. The workflow exists to make the misses visible at T-90 — sponsor never confirmed, value-evidence missing, single-threaded relationship — while there's still runway.

## Step 1 — The renewal watchlist surface

The workflow starts with a surface: accounts whose renewal is inside the watch window, sorted by **risk × proximity**.

- **Entry:** an account enters the watchlist when `days_to_renewal` crosses the watch threshold (default ~180 days).
- **Sort:** by `(health_tier, days_to_renewal)` — Red-and-soon at the top.
- **Per row:** the health tier + **why** (its driving signals), days to renewal, renewal-opportunity stage, recommended next action, and a trend sparkline.
- **The actionability bar:** a CS leader sorts by `(tier = Red AND days_to_renewal < 90)` and gets an actionable call list in under two minutes, every Red showing why. If the surface needs mental computation or shows an unexplained Red, it fails the bar.

## Step 2 — The workflow stages (health-gated)

| Stage | Default timing | The health-gated check |
|---|---|---|
| **Watch** | enters ~180-day window | baseline health tier recorded; account on the watchlist |
| **Confirm** | ~120 days | named decision-maker / sponsor still in role + engaged? value-evidence assembled + sourced? |
| **Multi-thread** | ~90 days | single-threaded to one champion (a single point of failure) or multi-threaded? |
| **Decide** | ~90-60 days | the expand / maintain / recover call (Step 4) |
| **Close** | ~30-7 days | "no surprises" — the account already knows the posture + pricing |

> The day-counts are the default SaaS clock. A vertical overlay (a budget-build window that decides the renewal months early) shifts the *clock*; the stages and their health-gates stay the same. Overlays live in a vertical plugin, not here.

**Missed stages are the leading indicator.** Don't march forward as if a missed milestone happened — a missed confirm / multi-thread is itself a risk flag that should re-tier the account.

## Step 3 — Trigger-to-play mapping (save-play triggers)

Map health-tier states *and* independent red-flag triggers to a save motion. The tier drives the scheduled cadence; the independent triggers fire immediately, regardless of tier color.

| Trigger | Fires |
|---|---|
| Tier = Red AND `days_to_renewal < 90` | Top-of-list save play; frequent review until cleared or resolved |
| Tier flips Green→Yellow | Investigate which signals dropped; light-touch recovery; tighten cadence |
| **Champion / sponsor departs** (independent) | Immediate re-confirm-and-multi-thread motion — don't wait for the next QBR |
| **Active-user collapse** (independent) | Immediate diagnostic + outreach |
| **Account says "evaluating alternatives"** (independent) | Immediate recovery motion + escalation |
| Sponsor skips 2 consecutive reviews (ghost sponsor) | Re-confirm decision-maker; feed silence back into the tier |

Independent triggers run **alongside** the tier, not inside it — a composite reacts too slowly to a sudden champion departure.

## Step 4 — The expand / maintain / recover decision

At the Decide stage the CSM makes an internal call from three inputs — health tier, adoption trajectory, organizational readiness:

| Input | Expand | Maintain | Recover / exit |
|---|---|---|---|
| Health tier | Top, stable/rising | Mid, stable | Bottom or declining |
| Adoption | Broad + room to grow | Steady at target | Narrow or declining |
| Org readiness | New budget / sponsor energy | Status quo | Org change against us / sponsor lost |

- **Expand** → trigger the grow motion *after* the renewal closes, never bundled into it.
- **Maintain** → renew and continue at the standard cadence.
- **Recover** → the renewal motion *is* the recovery; fire the save play immediately.

**Anti-pattern:** running an expansion motion on a Yellow/Red account during the renewal window. It conflates the relationship, burns the renewal, and signals the CSM is on quota. (CS is not sales — expansion fires when the account has earned value, not on a calendar quota.)

## Step 5 — Touch-cadence by tier

The tier drives how often, not just who:

| Tier | Cadence |
|---|---|
| **Green** | Standard rhythm (quarterly QBR + light monthly pulse); watch for expansion readiness |
| **Yellow** | Tighter (monthly sync + weekly signal review); light-touch recovery |
| **Red** | Recovery cadence — *not* "wait for the next QBR"; frequent review until cleared |

## Step 6 — QBR discipline (the recurring checkpoint between renewals)

- A QBR with no commitments is a status meeting. Every QBR ends with named action items, owners, and dates — tracked *between* QBRs.
- QBR attendance is a signal: a sponsor skipping two reviews is a ghost sponsor (feeds the tier).
- Provenance on every QBR claim — "usage up 18%" needs source, range, baseline.

## What this skill does NOT cover

- The health tier itself (signal selection, weighting, thresholds, explainability) → [`../health-tier-design/SKILL.md`](../health-tier-design/SKILL.md)
- Building the pipeline / warehouse / BI surface that renders the workflow → `data-platform`
- Segment-specific renewal overlays (K-12 budget cycle, academic calendar, board approval) → a vertical plugin (e.g. `edtech-partner-success`)
- The partner-facing comms / play *execution* in a vertical → a vertical CS-motion plugin

## References

- Knowledge: [`../../knowledge/renewal-and-account-lifecycle.md`](../../knowledge/renewal-and-account-lifecycle.md)
- Companion skill: [`../health-tier-design/SKILL.md`](../health-tier-design/SKILL.md)
- Template: [`../../templates/cs-health-data-model.md`](../../templates/cs-health-data-model.md)
- Generalized from: [`../../../edtech-partner-success/skills/renewal-play-design/SKILL.md`](../../../edtech-partner-success/skills/renewal-play-design/SKILL.md)
