---
description: "Model the DTC-vs-wholesale channel mix on net margin per channel (built on a defensible COGS per unit) against the demand each channel can absorb — DTC keeps full margin but is demand-limited, wholesale scales but gives margin to the distributor and retailer; every licensing/excise specific flagged and routed (verify-at-use)."
argument-hint: "[COGS per unit + DTC net + wholesale price and distributor/retailer take + absorbable demand per channel]"
---

You are running `/craft-beverage-operations:model-channel-mix`. Use `craft-beverage-operations-lead` + the `production-planning-and-cogs` and `three-tier-and-self-distribution-economics` skills.

> Operations decision-support, not legal, tax, or regulatory advice. Any three-tier / self-distribution eligibility / licensing / excise specific is jurisdiction-specific — flag it `[verify-at-use]` and route it to `beverage-distribution-compliance-advisor` and a professional. No PII.

## Steps

1. Confirm a **defensible COGS per unit** exists (raw material + yield loss + packaging + overhead) — if not, nail it first; channel margin is meaningless without it.
2. Traverse the **channel mix (DTC vs wholesale)** tree in `knowledge/craft-beverage-decision-trees.md`.
3. Compute **net** margin per channel: DTC net vs wholesale net **after** distributor and retailer take.
4. Read the **absorbable demand** per channel (DTC via tasting-room/club/e-commerce capacity; wholesale via reach) — DTC is usually demand-limited, wholesale volume-rich.
5. Allocate production on net margin × absorbable demand; name the trade (DTC margin vs wholesale scale).
6. Flag every licensing/excise/eligibility specific `[verify-at-use]` and route to the compliance advisor.
7. Emit using `templates/channel-margin-and-cogs-worksheet.md` + the Structured Output block, with the recommended mix and the two things that would change it.
