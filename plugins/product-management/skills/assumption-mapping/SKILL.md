---
name: assumption-mapping
description: "Structured playbook for surfacing and ranking the riskiest assumptions behind a product initiative, then designing the cheapest test for each — the core of continuous discovery before building."
---

# Assumption Mapping

## When to Use This

Before committing to a PRD or a sprint, when the team has a solution idea but hasn't pressure-tested whether it rests on beliefs that could be wrong. Use it to identify which assumptions, if false, would kill the initiative — and test those first.

## The Four Assumption Categories (Teresa Torres Framework)

| Category | Question it answers | Example assumption |
|---|---|---|
| **Desirability** | Do users want this? | "Users are frustrated enough with step 2 to switch tools if we fix it" |
| **Viability** | Is it worth building (business)? | "This segment will pay $20/mo more for this feature" |
| **Feasibility** | Can we build it? | "We can process uploads in < 2 seconds with our current stack" |
| **Usability** | Can users use it? | "Users will discover the new entry point without a tooltip" |

## Step 1 — Brain-Dump Assumptions

Give each team member 10 minutes with sticky notes (physical or FigJam) to write one assumption per note. Prompt: "What must be true for this initiative to succeed?"

Include assumptions the team takes for granted — those are often the riskiest because nobody is checking them.

## Step 2 — Place on the 2×2

Plot each assumption on a grid:

```
              HIGH IMPORTANCE
                    |
    Low confidence  |  Low confidence
    High importance |  Low importance
                    |
  ──────────────────┼──────────────────
                    |
    High confidence |  High confidence
    High importance |  Low importance
                    |
              LOW IMPORTANCE
         LOW CONFIDENCE ←→ HIGH CONFIDENCE
```

**Riskiest assumptions = top-left quadrant** (high importance + low confidence). These are the ones that, if wrong, crater the initiative and that you don't yet have evidence for.

## Step 3 — Design Cheap Tests

For each top-left assumption, ask: "What is the cheapest evidence that would change my confidence?"

| Assumption | Test type | Minimum evidence |
|---|---|---|
| Users are frustrated enough to switch | 5 user interviews; listen for unprompted pain | 3 of 5 describe the problem spontaneously |
| Willingness to pay $20 more | Landing page with pricing variant; measure click-to-upgrade rate | > 8% click-through on upgrade CTA |
| Upload in < 2s is feasible | Prototype with real file size; benchmark | p95 < 2s on a dev environment with prod-scale files |
| Users discover new entry point | Usability test: task completion without guidance | ≥ 4 of 5 complete the task unaided |

**The test is cheap when:** it can be run in < 1 week with < 1 person-week of effort, and its result would genuinely change the decision to build.

## Step 4 — Prioritize Tests

Rank tests by: (importance of assumption) × (1 − current confidence). Run the highest-ranked tests before writing a PRD or committing engineering time.

## Step 5 — Update the Assumption Map

After each test, move assumptions based on evidence. If a high-importance assumption turns out false, revisit the solution — don't push forward and hope.

## PRD Integration

The assumption map becomes the "Riskiest Assumptions" section of the PRD:

```markdown
## Riskiest Assumptions

| Assumption | Category | Current confidence | Planned test | Test owner | Due |
|---|---|---|---|---|---|
| Users will pay for bulk export | Viability | 40% | Pricing page variant | @alice | 2026-06-15 |
| Bulk export < 5s for 10k rows | Feasibility | 60% | Backend spike | @bob | 2026-06-12 |
```

## Pitfalls

- Stopping at "we've talked to customers" without mapping which assumptions those conversations tested — some of the riskiest assumptions are never asked about because the team is too in love with the solution.
- Treating feasibility assumptions as unimportant — a technically infeasible feature has a 0% success rate regardless of desirability.
- Running tests that can't change the decision — if the team would build it regardless of the test result, the test is theater. Ask: "What result would make us NOT build this?"
- Mapping assumptions once and never updating — new evidence should move assumptions; a stale map is decoration.

## See Also

- [`../../agents/product-discovery-lead.md`](../../agents/product-discovery-lead.md) — continuous discovery and riskiest-assumption testing
- [`../../agents/product-metrics-analyst.md`](../../agents/product-metrics-analyst.md) — judging test outcomes with real evidence
