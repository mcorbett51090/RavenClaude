---
description: "Design a lead scoring model and lifecycle stage framework — traverse the lead-score design tree, produce a scored attribute table with decay rules, the MQL threshold, and the bilateral handoff SLA."
argument-hint: "[context, e.g. 'B2B SaaS, ACV $30K, HubSpot MAP, Sales team of 8 AEs, current no scoring']"
---

You are running `/marketing-operations-demand-gen:design-lead-scoring`. Use the
`marketing-ops-lead` and `marketing-automation-engineer` disciplines and the
`lead-scoring-and-lifecycle` skill.

## Steps

1. Traverse the Lead-score design decision tree in
   `knowledge/marketing-ops-decision-trees.md` top-to-bottom using the context provided.
   Name the leaf you land on.

2. Design the lifecycle stage model (Subscriber → Lead → MQL → SAL → SQL → Opportunity) with
   entry criteria, exit criteria, and bypass rules. Document the rejection taxonomy Sales will
   use when sending an MQL back.

3. Build the scoring attribute table:
   - Demographic/firmographic fit score (who they are) — max 50 points.
   - Behavioral engagement score (what they did) — pricing-page, demo request, content downloads,
     email engagement, web activity.
   - Negative scoring — inactivity decay, unsubscribe signals, competitor domain.
   - Recency decay rules for behavioral points.

4. Recommend the MQL threshold (composite score) with the rationale. Flag that this is a bilateral
   negotiation with Sales and must be jointly agreed.

5. Define the speed-to-lead SLA target and the notification/routing trigger when a contact
   hits the MQL threshold.

6. Output the scoring configuration document, the lifecycle stage model, and a MAP implementation
   summary (HubSpot Workflow / Marketo Smart Campaign / Pardot Automation Rule — based on the
   MAP named in context). Fill `templates/campaign-brief.md` if a campaign trigger is in scope.
   Emit the Structured Output block with handoffs (marketing-automation-engineer to implement,
   demand-gen-strategist to align programs to the lifecycle model).
