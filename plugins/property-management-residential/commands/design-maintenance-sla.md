---
description: "Design a tiered work-order SLA matrix (emergency/urgent/routine) for a residential property or portfolio, with response and resolution commitments, habitability-first triage rules, escalation triggers, and a vendor notification protocol."
argument-hint: "[context, e.g. '150-unit apartment complex, 3 in-house techs, 5 preferred vendors, AppFolio PM software']"
---

You are running `/property-management-residential:design-maintenance-sla`. Use the
`maintenance-operations-analyst` discipline and the `maintenance-and-work-orders` skill.

## Steps

1. **Establish tiers** — define the three priority tiers for this property/portfolio:
   - **Emergency** — habitability, health, or safety items. List 8–10 examples specific to the
     property type (single-family vs. apartment). Response ≤1h, resolution ≤24h.
   - **Urgent** — significant comfort or property impact but not habitability. Response ≤4h,
     resolution ≤72h.
   - **Routine** — non-urgent repairs and cosmetic work. Response ≤24h, resolution ≤7d.

2. **Write triage rules** — the questions a maintenance coordinator asks to assign a tier:
   (a) Does this affect heat, cooling, plumbing, electrical safety, or structural safety? → Emergency
   (b) Does this significantly affect the resident's ability to use the unit? → Urgent
   (c) Everything else → Routine. When in doubt, assign higher.

3. **Design the vendor notification protocol** — how a vendor is notified for each tier:
   - Emergency: PM software dispatch + direct phone call; vendor confirms ETA within 30 minutes
   - Urgent: PM software dispatch + text; vendor confirms within 1 hour
   - Routine: PM software dispatch; vendor confirms next-business-day

4. **Build the escalation triggers** — when does a routine become urgent or an urgent become
   emergency? (e.g., resolution SLA missed, resident escalates, habitability concern emerges)

5. **Output the SLA matrix** — fill in `templates/work-order-sla-matrix.md` with the values
   designed above.

6. **Identify KPIs to track** — SLA compliance rate by tier, days-to-close average, callback rate.
   Confirm these are capturable in the PM software in use.

7. **Flag habitability-legal seam** — note that any emergency work order involving HVAC, plumbing,
   or habitability that is not resolved within the SLA should be flagged to `pm-compliance-advisor`
   for constructive eviction risk assessment.

8. **Emit the Structured Output Protocol block** with `handoff_recommendation` to
   `maintenance-operations-analyst` (implementation + vendor onboarding).
