---
name: commission-split-and-cap-economics
description: "Model brokerage commission economics: compare split, cap, and fee models at an agent's expected GCI, compute company dollar per agent and the cap crossover point, and weigh the recruiting/retention trade-off. Commission rates and fees are business-agreement- and market-specific — verify-at-use. Not legal or tax advice."
---

# Commission Split & Cap Economics

The commission model is the brokerage's biggest recurring recruiting lever. Model it on **take-home and company dollar**, not the headline split.

## The loop

1. **Start from the agent's expected GCI.** Gross commission income per agent per year is the input everything else derives from. Model a realistic band, not a best case.
2. **Lay the models side by side.** Traverse the split-vs-cap tree in [`../../knowledge/residential-brokerage-decision-trees.md`](../../knowledge/residential-brokerage-decision-trees.md):
   - **Split** — house takes a percentage of every deal (company dollar scales with production).
   - **Cap** — agent pays the split until a cap, then keeps ~100% (minus fees) for the rest of the year; company dollar plateaus at the cap.
   - **Fee / desk** — flat monthly or per-transaction fee; company dollar is roughly fixed per agent.
   Rates, caps, and fees are `[verify-at-use]` against the brokerage's agreements and the market.
3. **Compute the crossover.** Find the GCI at which the cap model's company dollar equals the split model's. Below it the split earns the house more; above it the cap does — which is exactly why high producers prefer a cap and want it.
4. **Weigh recruiting vs retention.** A model that pencils only for the house loses producers; one that pencils only for the agent starves the brokerage. Recruit and retain on the whole value stack, not the split alone (see [`../../best-practices/recruit-and-retain-on-economics-and-support.md`](../../best-practices/recruit-and-retain-on-economics-and-support.md)).

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Company dollar per agent | house share after split/cap/fees | The brokerage's real revenue line |
| Cap crossover GCI | where cap company-dollar = split | Below it split wins the house; above it, cap |
| Agent retention rate | agents retained year over year | Falling -> the model or support is losing to a competitor |

## Anti-patterns

- Recruiting on a headline split the P&L can't sustain.
- Ignoring fees/desk costs when comparing take-home.
- Putting every agent on one model regardless of production tier.

## See also

- [`../transaction-timeline-management/SKILL.md`](../transaction-timeline-management/SKILL.md).
- Best practice: [`../../best-practices/recruit-and-retain-on-economics-and-support.md`](../../best-practices/recruit-and-retain-on-economics-and-support.md).
- Reference: [`../../knowledge/residential-brokerage-reference-2026.md`](../../knowledge/residential-brokerage-reference-2026.md) (commission norms, verify-at-use).
