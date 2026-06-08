---
description: "Build an end-to-end tax-season operating plan for a CPA firm: return inventory, capacity model, review-tier matrix, document-chase calendar, extension strategy, and e-file tracking protocol."
argument-hint: "[context, e.g. '120 1040s, 30 1120s, 20 1065s; 3 staff, 2 seniors, 1 manager, 1 partner; UltraTax; last year 85% realization']"
---

You are running `/accounting-firm-cpa:plan-tax-season`. Use the `tax-workflow-strategist`
discipline and the `tax-season-workflow` skill.

## Steps

1. **Return inventory.** From the context provided, catalogue returns by type (1040, 1120, 1065,
   1041, 990) and assign a complexity tier (simple / standard / complex) to each bucket based on
   typical characteristics for that entity type.

2. **Capacity model.** For each return type × complexity tier, apply average charge-hour estimates.
   Multiply by count to get total demand hours. Compare against available staff hours by level
   (applying a realistic utilization target, not 100%). Identify gaps and recommend levers
   (overtime, outsourcing, extensions, workflow efficiency). Use `scripts/firm_calc.py` for
   the utilization calculation.

3. **Review-tier matrix.** Using the review-tier routing tree in
   `knowledge/cpa-firm-decision-trees.md`, assign preparer and reviewer levels to each return
   complexity tier. Define escalation triggers (items requiring the next tier up).

4. **Seasonal deadline calendar.** Map all original and extended filing deadlines for the
   current tax year. Note payment deadlines for extensions. Flag state deadlines that may differ
   from federal `[verify-at-use]`.

5. **Document-chase calendar.** Build the document-chase program: organizer send date, reminder
   1, reminder 2, extension trigger, and final notice date for each return type. Define the
   escalation path (portal → email → phone → extension).

6. **Extension strategy.** Define extension decision criteria (missing docs, complexity, capacity).
   Draft a client communication template for extension notification including estimated payment
   obligation. Build the second-deadline capacity plan for extended returns.

7. **E-file tracking protocol.** Define the submission → acknowledgment → acceptance workflow.
   Include a rejection triage matrix (top rejection types and resolution steps).

8. **Output.** Fill in a complete tax-season operating plan. Emit the Structured Output block
   with handoffs: `firm-practice-lead` for capacity economics; `firm-advisory-lead` for client
   scope conversations.
