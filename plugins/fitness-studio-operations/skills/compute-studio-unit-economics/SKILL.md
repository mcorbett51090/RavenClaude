---
name: compute-studio-unit-economics
description: "Compute the studio's unit economics: revenue per member, average lifetime months, LTV, CAC, payback period, and the CAC ceiling to spend against — with the formulas, from your own data rather than industry averages."
---

# Compute Studio Unit Economics

The numbers that say whether a member is worth acquiring and what you can spend to do it. Compute from *your* billing, not benchmarks.

## The formulas

```
Revenue per member (RPM)   = monthly net membership revenue / active members
                             (net of discounts, freezes, failed payments)

Avg lifetime (months)      = 1 / monthly churn rate        (from member-retention-analyst)

LTV                        = RPM × avg lifetime months × contribution margin

CAC                        = total acquisition spend / new members acquired
                             (in the same period)

Payback (months)           = CAC / (RPM × contribution margin)

CAC ceiling                = LTV / target LTV:CAC ratio     (e.g. LTV / 3)
```

## Rules
- **Net, not gross.** Strip discounts, freezes, and failed/declined payments out of RPM, or you'll overstate LTV and overspend on acquisition.
- **Lifetime comes from churn.** Average lifetime months = 1 / monthly churn — get the churn rate (and its method) from `member-retention-analyst`; don't guess it.
- **Apply contribution margin.** LTV is a margin number, not a revenue number — subtract the variable cost to serve the member (instructor pay attributable, processing fees, consumables).
- **Payback is the cash-flow test.** A great LTV:CAC with a 14-month payback can still starve a studio's cash. Watch both.
- **The CAC ceiling is the hand-off.** That single number is what `fitness-studio-operations-lead` passes to `marketing-operations` to spend against.

## Worked example
RPM $140, monthly churn 5% → lifetime 20 months. Margin 60% → LTV = 140 × 20 × 0.6 = **$1,680**. Target LTV:CAC 3:1 → **CAC ceiling $560**. CAC actual $300 → payback = 300 / (140 × 0.6) = **~3.6 months**. Healthy. (`[verify-at-use]` — illustrative.)

## Anti-patterns
- Quoting an industry LTV instead of computing yours.
- LTV on gross revenue (ignoring margin).
- Spending to a CAC with no payback check.

Traverse the pricing-model tree in [`../../knowledge/fitness-studio-operations-decision-trees.md`](../../knowledge/fitness-studio-operations-decision-trees.md); benchmarks (dated) live in [`../../knowledge/fitness-studio-operations-reference-2026.md`](../../knowledge/fitness-studio-operations-reference-2026.md).
