---
name: three-tier-and-self-distribution-economics
description: "Model the go-to-market structure: self-distribution (margin kept, sales/logistics cost, eligibility limits) vs a distributor (reach and depletion, margin given away, franchise-law lock-in), plus the channel margin math (DTC net vs wholesale net after distributor/retailer take). Every TTB/state-licensing/excise specific is jurisdiction-specific — flag and route it."
---

# Three-Tier & Self-Distribution Economics

How product reaches the market is where craft producers get locked in or caught out. This skill models the economics of self-distribution vs the three-tier distributor system and maps the licensing/excise structure the choice touches — flagging every jurisdiction-specific rule and routing the determination to a licensed professional.

## The loop

1. **Model the channel margin honestly.** DTC keeps full retail margin; wholesale gives it away — distributor take **and** retailer take come off the top. Compute net margin per channel against the true COGS per unit (from the production/COGS skill).
2. **Weigh self-distribution vs a distributor.** Self-distribution keeps the distributor's margin but costs sales and logistics effort and has **eligibility limits** (jurisdiction-specific). A distributor buys reach and depletion support but takes margin and often comes with **franchise-law lock-in** you may not be able to leave. Traverse the **self-distribute vs distributor** tree in [`../../knowledge/craft-beverage-decision-trees.md`](../../knowledge/craft-beverage-decision-trees.md).
3. **Read the distributor on depletion.** A signed distributor that doesn't deplete is a shelf problem — read attention, portfolio priority, and pricing, and flag the franchise-law constraints on switching.
4. **Map the licensing/excise structure — flag, don't decide.** Federal TTB, state licensing, direct-ship permits, and excise are jurisdiction-specific legal/tax questions. Describe the *structure*; mark every specific `[verify-at-use]`; route it.

## What this skill does NOT do

- It does not state the three-tier, franchise-law, licensing, or excise rule for any jurisdiction.
- It does not decide self-distribution eligibility or a permit requirement.
- It does not render a tax determination.

Those are **determinations** — they route to a licensed attorney/accountant and the regulator. This skill models the economics and maps the structure; they make the call.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| DTC net margin per unit | price − COGS − DTC cost | The full-margin baseline |
| Wholesale net margin per unit | price − COGS − distributor & retailer take | Margin given away for reach |
| Depletion rate | units pulled through / period | The distributor's real metric |
| Self-distribution cost to serve | sales + logistics / units | The margin-kept trade-off |

## Anti-patterns

- Comparing channels on gross price instead of net margin after each tier's take.
- Signing a distributor without reading the franchise-law lock-in.
- Quoting a licensing/excise/eligibility rule as settled instead of flagging and routing it.
- Modeling wholesale margin without the true COGS per unit.

## See also

- [`../production-planning-and-cogs/SKILL.md`](../production-planning-and-cogs/SKILL.md) — channel margin needs the unit cost.
- Best practices: [`../../best-practices/three-tier-and-licensing-are-a-professional-call.md`](../../best-practices/three-tier-and-licensing-are-a-professional-call.md), [`../../best-practices/dtc-margin-beats-wholesale-but-doesnt-scale-like-it.md`](../../best-practices/dtc-margin-beats-wholesale-but-doesnt-scale-like-it.md).
- Command: [`/model-channel-mix`](../../commands/model-channel-mix.md).
