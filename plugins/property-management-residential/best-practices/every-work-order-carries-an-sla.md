# Every work order carries an SLA

**Status:** Pattern
**Domain:** Maintenance operations
**Applies to:** `property-management-residential`

---

## Why this exists

A work order without a committed response and resolution timeline is a double liability: a habitability
risk (deferred repair can escalate to a constructive eviction claim) and a retention risk (residents who
wait indefinitely for repairs leave and tell others why). An SLA matrix makes the maintenance operation
manageable — the priority tier assigned at intake determines the vendor, the timeline, and the
escalation path.

Without SLAs, maintenance coordinators optimize informally (loudest resident, easiest fix, whoever
calls back first), and the results are unpredictable. With SLAs, the operation is auditable, vendors
are accountable, and the PM can report compliance rates to owners.

## How to apply

1. **Assign a priority tier at intake.** Every work order received — portal, phone, email — is
   triaged and assigned Emergency / Urgent / Routine before dispatch. The tier determines the SLA.
2. **Communicate the SLA to the resident.** Residents should receive an automated acknowledgment
   (via PM software) with the expected response window. "We received your request and will follow up
   within X hours" is the minimum.
3. **Track SLA compliance in the PM software.** Every platform (AppFolio, Buildium, Yardi) can report
   open work orders by age. Run a weekly aging report. Any Emergency or Urgent item past SLA is an
   immediate escalation.
4. **Use `templates/work-order-sla-matrix.md`** to document the tier definitions, response windows, and
   escalation triggers for your property.

**Do:**

- Triage every incoming work order within 1 business hour of receipt.
- Assign Emergency to any item affecting heat, cooling, plumbing function, electrical safety, gas,
  structural safety, or active pest infestation.
- When in doubt between tiers, assign the higher tier.
- Track SLA compliance monthly and share the report with vendors.

**Don't:**

- Let a work order sit in the queue without a tier assignment.
- Allow habitability items (HVAC failure, sewage, active leak, mold) to be triaged as Routine.
- Close a work order as "complete" without vendor confirmation and resident follow-up.
- Accept a vendor's word that an emergency is resolved without a photo and a signed work order.

## Edge cases / when the rule does NOT apply

- **Pre-scheduled work (preventive maintenance, make-ready scopes):** these are planned events with
  their own scheduling discipline, not reactive work orders. They don't carry emergency SLAs, but
  they should still be tracked in the work-order system with a "PM" type tag.
- **Owner-requested capital improvements:** capital projects (roof replacement, major renovation)
  are scoped and scheduled separately from reactive maintenance. They go through `skilled-trades-
  contracting` for scope and contract; the SLA matrix governs day-to-day reactive work.

## See also

- [`./the-turn-is-where-noi-is-won-or-lost.md`](./the-turn-is-where-noi-is-won-or-lost.md)
- [`./document-everything-in-the-tenant-file.md`](./document-everything-in-the-tenant-file.md)
- [`../templates/work-order-sla-matrix.md`](../templates/work-order-sla-matrix.md)
- [`../agents/maintenance-operations-analyst.md`](../agents/maintenance-operations-analyst.md)

## Provenance

Grounded in implied warranty of habitability doctrine (Javins v. First National Realty Corp. and its
progeny), which requires timely repair of conditions affecting habitability. SLA discipline is the
operational mechanism that makes the legal obligation measurable and defensible.

---

_Last reviewed: 2026-06-08 by `claude`._
