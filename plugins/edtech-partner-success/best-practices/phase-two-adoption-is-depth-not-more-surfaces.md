# Phase two adoption is depth, not more surfaces

**Status:** Pattern
**Domain:** EdTech partner adoption
**Applies to:** `edtech-partner-success`

---

## Why this exists

After a K-12 partner survives the settling window (Stage 1, weeks 1–8) and has basic adoption underway, the next PSM instinct is often to introduce more product features and surfaces. This is the Stage 1 error repeated in Stage 2: feature breadth before depth. A district in Stage 2 (first-year-sustaining) needs to get better at the core workflow they've already started, not to add a second workflow they haven't yet mastered. Premature feature expansion dilutes teacher attention, creates confusion about what the product actually does, and generates "we're using too many different tools" feedback that signals overwhelm, not engagement. The Stage 2 goal is measurable depth in the core use case — not a wider product footprint.

## How to apply

At the transition from Stage 1 to Stage 2 (approximately week 9–12 post go-live), define a depth metric for the core use case and set a threshold before introducing any new surface.

```
Stage 2 depth-before-breadth protocol:

  1. Define the core-use-case depth metric:
     — What does "using it well" look like for this product's primary workflow?
     — Example: "75% of enrolled teachers have completed >= 2 sessions in the platform"
     — Example: "Average session depth (pages visited / session) is above the product's P50 benchmark"

  2. Set the depth threshold before introducing Feature B:
     — Do not demo Feature B until the depth metric is above the threshold.
     — Threshold guideline: >= 60% of active users meeting the core-use-case success criterion
       [ESTIMATE — calibrate to the product and partner]

  3. In Stage 2 QBRs and check-ins:
     — Lead with "how is the core workflow going?" not "have you tried Feature X?"
     — The adoption diagnostic (see the adoption-diagnostic worksheet template) applies here.

  4. Common Stage 2 trap: partner admin asks about Feature B.
     — Acknowledge it: "That feature is there and we will walk you through it when you're ready."
     — Gate it: "I'd like to see [depth metric] reach [threshold] first so your team has capacity."
```

**Do:**
- Define the core-use-case depth metric for each product and each partner segment at the start of Stage 2.
- Gate Feature B introductions on a measurable depth threshold, not on the calendar.
- Use the adoption diagnostic worksheet when Stage 2 depth is lagging to find the root cause.

**Don't:**
- Introduce new product surfaces in Stage 2 to generate engagement signals — it generates noise, not signal.
- Conflate breadth (more features touched) with depth (core workflow used well).
- Accept "they've tried 6 features" as evidence of successful Stage 2 adoption.

## Edge cases / when the rule does NOT apply

If a partner's contract explicitly includes a Phase 2 product scope with a specific feature set, the breadth-vs-depth balance must respect the contractual scope. For multi-site implementations where different schools are in different stages simultaneously, apply stage-appropriate guidance per site, not per district overall.

## See also

- [`../agents/learning-analytics-analyst.md`](../agents/learning-analytics-analyst.md) — designs and monitors the adoption depth metrics that gate Stage 2 expansion.
- [`./onboarding-sequence-depth-before-breadth-in-stage-one.md`](./onboarding-sequence-depth-before-breadth-in-stage-one.md) — the Stage 1 companion rule that establishes the depth-first principle from day one.

## Provenance

Codifies the adoption-sequencing discipline from the plugin's `adoption-sequencing-k12` skill and `k12-adoption-arc-fall-spring-summer.md` knowledge file. The Stage 2 feature-breadth error is the most common PSM mistake after successful Stage 1 activation.

---

_Last reviewed: 2026-06-05 by `claude`_
