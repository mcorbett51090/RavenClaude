# Know your real churn rate

**Status:** Absolute rule
**Domain:** Retention
**Applies to:** `fitness-studio-operations`

---

## Why this exists

Every downstream number — average lifetime months, LTV, the CAC ceiling, the keep-vs-acquire call — depends on the churn rate. A churn number computed inconsistently (or guessed) propagates error into every decision that rests on it. The classic error is mishandling freezes: counting a freeze as a cancel overstates churn, and ignoring a never-returning freeze understates it.

## How to apply

- Compute **monthly logo churn = members lost in the period ÷ members active at the start of the period**, the same way every month.
- **Define the freeze/pause treatment up front** and apply it consistently; track freeze-to-return rate separately so unreturning freezes surface as the churn they really are.
- Report the trend over 6-12 months, not a single month, and read it by cohort and membership type, not blended.

**Do:** document the formula and the freeze rule so the number is reproducible.
**Don't:** quote a churn rate you can't reconstruct from the roster.

## Edge cases / when the rule does NOT apply

Very small studios will see noisy month-to-month rates — use a rolling window, but still compute it the same way each period.

## See also

- [`./retention-is-the-economic-engine.md`](./retention-is-the-economic-engine.md)
- [`../skills/analyze-retention-and-churn/SKILL.md`](../skills/analyze-retention-and-churn/SKILL.md)

## Provenance

Standard SaaS/membership churn accounting, adapted to studio freezes. Codifies the `member-retention-analyst` discipline.

---

_Last reviewed: 2026-06-25 by `claude`_
