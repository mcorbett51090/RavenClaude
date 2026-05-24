---
name: variance-commentary
description: Write variance commentary that tells a story instead of restating a table — templates for revenue, GM, opex, EBITDA, FCF with named drivers + materiality threshold applied. Source-cite every number. Used by `fpa-analyst` (primary) + `board-pack-composer`.
---

# Skill: variance-commentary

**Purpose:** How to write variance commentary that tells a story instead of restating a table. Used by `fpa-analyst` (primary), `board-pack-composer`, and any agent that produces a variance walk.

## When to use

- Monthly / quarterly variance walks for management review
- Variance commentary inserts for board / investor packs
- Forecast accuracy reviews
- Pre-audit "explain the year" sessions

## The shape of good commentary

Bad commentary describes the variance:
> Revenue was $1.2M below plan, driven by lower new bookings.

Good commentary names the driver:
> Revenue was $1.2M below plan because two enterprise deals (Customer A, $600K; Customer B, $550K) slipped from Q3 to Q4. Both are on Q4 close lists with weighted probability >70%. Net impact: Q4 will overshoot if both close; FY guidance unchanged.

The bad version restates the table. The good version tells the reader *why*, *what's next*, and *what to do with the information*.

## The variance-commentary canvas

For each material variance, write:

1. **What happened.** One sentence with the size of the variance.
2. **Why it happened.** One or two sentences with the actual driver, named specifically. Not "lower bookings" — *which* bookings, *which* customers, *which* segment.
3. **Direction over time.** Is this a one-time event, a trend, or part of a normal seasonal pattern?
4. **Impact on the outlook.** Does this change the forecast for the next period? The full year? The strategy?
5. **What's being done.** Who owns the response, what's the next-action / next-decision-point.

## Variance walks for the canonical P&L lines

### Revenue

- **Rate vs volume vs mix vs FX** decomposition. State which moved.
- For ARR: new vs expansion vs churn vs FX (if multi-currency).
- For services: hours billed × rate × utilization, separate each driver.

### Gross margin

- Mix shift (higher- vs lower-margin product / segment)
- Pricing changes
- Direct cost movements (COGS line items)
- One-time items (inventory write-down, refund reserve true-up)

### Operating expense (by function)

- Headcount actual vs plan, ramp timing
- Comp & benefits true-ups (commission, bonus accrual, payroll tax)
- Discretionary spend (marketing programs, travel, professional services)
- One-time items (severance, legal settlements, restructuring)

### EBITDA bridge

- Show the bridge from prior period or plan: starting EBITDA + each material driver (signed) = ending EBITDA. Each step on the bridge tied to a P&L line and an owner.

### Free cash flow

- EBITDA → working capital change → capex → cash interest → cash tax → FCF
- Working capital drivers (AR aging, AP timing, inventory build)
- Capex commitments coming due vs deferring

## Materiality

Declare the threshold up front:
> Commentary covers variances ≥ $50K or ≥ 5% of the line, whichever is greater.

Without this, you waste hours on noise and miss real signal.

## Common pitfalls

- **Restating the table in prose.** "Revenue of $5M is $1M below the $6M plan." That's the table; that's not commentary.
- **Naming a driver too high.** "Lower demand" is not a driver. "Lower demand in vertical X due to [specific event]" is.
- **Anchoring on the variance, not the absolute number.** A 50% favorable variance on a tiny line is rarely worth commentary; a 2% unfavorable on the largest line might be.
- **Confusing timing with miss.** A deal that closes in October instead of September is timing; a deal that's not closing is a miss. They have different responses.
- **No outlook implication.** Commentary without a "what does this mean for next period" is half-finished.
- **Forecast revisions reported as "same as last month."** If the forecast didn't move when reality moved, the forecast is broken.

## The 80/20

Most board / management readers can't internalize more than 5-7 variances. Pick the largest by absolute dollar (not %), comment on those well, and put the rest in a table with one-liner explanations in an appendix.

## See also

- Template: [`../../templates/variance-commentary.md`](../../templates/variance-commentary.md)
- Agent: [`../../agents/fpa-analyst.md`](../../agents/fpa-analyst.md)
- Agent: [`../../agents/board-pack-composer.md`](../../agents/board-pack-composer.md)
- Skill: [`../board-pack-composition/SKILL.md`](../board-pack-composition/SKILL.md) — for how variance commentary fits into a board pack
