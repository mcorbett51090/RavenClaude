---
name: design-membership
description: "Design the studio's membership model and pricing: pick drop-in / packs / unlimited / founding-member on cash-flow and retention shape, then compute revenue per member, LTV, and the CAC ceiling."
argument-hint: "[studio format + market + current pricing + member count]"
---

You are running `/fitness-studio-operations:design-membership`. Use `fitness-studio-operations-lead` + the `design-membership-model` and `compute-studio-unit-economics` skills.

## Steps
1. Traverse the pricing-model tree in `knowledge/fitness-studio-operations-decision-trees.md`.
2. Choose the membership model(s) on cash-flow and retention shape; set founding-member cohort cap + sunset if used.
3. Get the churn rate / avg lifetime months from `member-retention-analyst` (or flag the assumption if pre-launch).
4. Compute revenue per member (net), LTV, the CAC ceiling, and payback.
5. Note front-desk/experience and any retail call.
6. Emit using `templates/membership-model-and-pricing.md` + the Structured Output block, handing the CAC ceiling to marketing-operations.
