---
name: rice-prioritization
description: "Worked RICE scoring playbook for evidence-based backlog prioritization — covers calibrating each factor, avoiding common scoring errors, and using the output to run a defensible prioritization meeting."
---

# RICE Prioritization

## When to Use This

You have 5+ competing initiatives and need a transparent, arguable ranking that isn't driven by whoever speaks loudest. RICE produces a single comparable score so trade-offs are explicit. Use it at quarterly planning or when the backlog needs a defensible cut.

## The Formula

```
RICE score = (Reach × Impact × Confidence) / Effort
```

## Calibrating Each Factor

### Reach (users or events per time period)

- Use a consistent time window across all items — usually per quarter.
- Source from actual data: DAU/MAU, segment size from your analytics tool, support ticket volume.
- Estimate the users who will encounter the feature, not total user base.

| Example | Reach |
|---|---|
| Affects all checkout users (10,000/qtr) | 10,000 |
| Affects users on mobile only (2,000/qtr) | 2,000 |
| Internal tool for 15 ops staff | 15 |

### Impact (per user/event)

Use a fixed scale — never raw numbers:

| Impact level | Score |
|---|---|
| Massive (core job done) | 3 |
| High | 2 |
| Medium | 1 |
| Low | 0.5 |
| Minimal | 0.25 |

Force-rank impact before scoring: if everything is "High," your scale is broken.

### Confidence (how certain are you about the estimates)

| Evidence level | Confidence |
|---|---|
| Strong data + user research | 100% |
| Partial data or limited interviews | 80% |
| Hunch / analogous market data | 50% |
| Pure guess | 20% |

Confidence is the error-correction term. Use it — the team's natural optimism bias means 80% should be the ceiling for most items without hard data.

### Effort (person-months)

Use the same unit for all items. Person-months is more stable than story points across items. Round to 0.5 increments for small work.

## Worked Example

| Initiative | Reach | Impact | Confidence | Effort | Score |
|---|---|---|---|---|---|
| Streamline onboarding step 2 | 4,000 | 2 | 80% | 1 | 6,400 |
| Add bulk export | 500 | 3 | 100% | 0.5 | 3,000 |
| New dashboard widget | 8,000 | 0.5 | 50% | 2 | 1,000 |
| API rate-limit increase | 200 | 3 | 80% | 0.5 | 960 |

Onboarding wins — high reach, meaningful impact, reasonable confidence, low effort.

## Running the Prioritization Meeting

1. **Score individually first** — have each participant score before the meeting; reveal together to surface disagreements.
2. **Debate outlier gaps** — if estimates diverge by > 2× on any factor, that factor needs more information, not more negotiation.
3. **Flag forced items** — contractual commitments, compliance deadlines, and strategic bets that won't move regardless of score. Put them in a separate list; don't let them pollute the scored ranking.
4. **The output is a ranked list with explicit assumptions** — publish scores with the reasoning, not just the rank order, so future teams can re-score with updated data.

## When RICE Breaks Down

- **When items aren't comparable in type** — scoring a regulatory compliance item against a growth feature doesn't work; use separate tracks.
- **When the team can't agree on reach** — invest in instrumentation first; scoring without data produces confident nonsense.
- **When the horizon is too short** — RICE is a quarterly/roadmap tool; for a two-day sprint, just pick the highest-value unblocked item.

## Pitfalls

- Inflating Confidence to avoid uncomfortable trade-offs — 100% confidence means you have data, not that you feel strongly.
- Scoring Effort in story points while comparing across teams with different velocity — normalize to a common unit.
- Treating the score as final without flagging dependencies — a high-score item blocked by another item still can't be started first.
- Skipping the "debate outlier gaps" step — the value of RICE is the forced calibration conversation, not the number itself.

## See Also

- [`../../agents/product-metrics-analyst.md`](../../agents/product-metrics-analyst.md) — evidence-based prioritization and funnel analysis
- [`../../agents/product-strategist.md`](../../agents/product-strategist.md) — roadmap as a set of bets; strategic override items
