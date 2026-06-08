---
scenario_id: 2026-06-08-tax-loss-harvest-tripped-the-wash-sale
contributed_at: 2026-06-08
plugin: wealth-management-ria
product: portfolio
product_version: "unknown"
scope: likely-general
tags: [tax-loss-harvesting, wash-sale, taxes, asset-location, after-tax-return]
confidence: high
reviewed: false
---

## Problem

A practice ran a year-end tax-loss harvesting sweep across client taxable accounts, selling positions at a loss to bank deductions. The harvested losses looked great on paper — until the next year's 1099s showed a chunk of them disallowed. The replacement buys had been the same fund repurchased inside the wash-sale window, and in several households an automatic dividend reinvestment (and in one case a purchase in the spouse's IRA of the identical fund) had silently tripped the rule. The "free" tax benefit partly evaporated, and the cleanup conversation with clients was worse than not having harvested at all.

## Constraints context

- Harvesting was run account-by-account with no view across the household (spouse accounts, IRAs).
- Dividend reinvestment was left on during the harvest window, quietly buying back the sold fund.
- The team treated "harvest a loss" as obviously good without modeling the wash-sale window or the client's actual bracket benefit.

## Attempts

- Tried: just harvesting more aggressively to "make up" the disallowed losses. Failed — it created more trades, more wash-sale exposure, and more tax-prep complexity, all for a benefit nobody had sized against the client's bracket.
- Tried: a 30-day "do nothing" cash gap to dodge the wash-sale rule. Helped on paper but left clients out of the market during the window — an uncompensated tracking-error/timing risk that could swamp the tax benefit.
- Tried: harvesting into a *non-substantially-identical* replacement (a different-index or different-issuer fund with similar exposure) to stay invested, turning off dividend reinvestment during the window, screening the *whole household* (including spouse + IRAs) for the wash-sale window, and routing the actual deduction value to the client's CPA. This worked.

## Resolution

Tracking the wash-sale window across every related account — not just the one being traded — stopped the disallowances, and the non-identical replacement kept the client invested so harvesting no longer meant a market-timing bet. Turning off reinvestment during the window closed the silent-repurchase hole. Sizing the benefit against the bracket (with the CPA owning the number) meant the practice only harvested where it actually paid, instead of trading for its own sake. After-tax return went up because the losses now survived to the return.

## Lesson

After-tax return is the return that matters, but the wash-sale rule gates tax-loss harvesting — and it spans the *household*, including the spouse's accounts and IRAs and any reinvestment. Stay invested with a non-substantially-identical replacement rather than going to cash, screen every related account for the window, and route the actual deduction value to a CPA. A harvested loss that gets disallowed was never a benefit; this is an educational framework, not tax advice.
