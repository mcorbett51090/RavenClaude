---
description: "Build a self-service deflection plan — identify the highest-ROI deflectable intents from ticket data, estimate deflection ROI, design the content roadmap, and produce an intent taxonomy for AI-deflection coverage."
argument-hint: "[context, e.g. 'B2C e-commerce, top categories: order status 40%, returns 25%, account access 15%, current deflection rate 18%']"
---

You are running `/customer-support-cx-operations:plan-deflection`. Use the
`knowledge-and-deflection-strategist` discipline and the `deflection-and-knowledge-strategy` skill.

## Steps

1. Map contact volume to content coverage: list the top contact categories by volume (30-day window
   minimum). For each: does a KB article exist? Is it findable in self-service? Does it fully
   resolve the contact without an agent?

2. Score deflectability for each gap category: is the resolution scripted (high deflectability)
   or judgment-intensive (low deflectability)? Rank by `volume × deflectability score`.

3. Traverse the `Deflect-vs-staff` tree in `knowledge/cx-ops-decision-trees.md` to confirm the
   high-priority intents are genuinely deflectable (not complexity-masked or policy-constrained).

4. Estimate deflection ROI using `scripts/cx_calc.py deflection-roi` — inputs: deflectable volume,
   cost per contact, expected containment rate. Produce the financial case for the content investment.

5. Build the content roadmap: for each high-priority gap, write an article brief (title, intent,
   resolution steps, not-covered scope, owner, review cadence). Prioritize by ROI estimate.

6. Design the AI-deflection intent taxonomy (if an AI bot is in scope): classify intents into
   fully automatable, semi-automatable, and must-escalate tiers. Write the handoff spec for each
   tier (trigger condition, routing target, context handoff format). Note: bot build goes to
   `claude-app-engineering`; this command produces the design spec.

7. Emit the Structured Output block with: top deflectable intents + ROI estimates, content roadmap
   (ordered backlog), intent taxonomy (if in scope), and handoffs to `contact-center-workforce-analyst`
   for staffing-impact modeling and to `support-quality-analyst` if the same intents are driving CSAT drops.
