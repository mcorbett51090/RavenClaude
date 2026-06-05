# IDEA Compliance Is a Fill-Rate KPI, Not a Legal Department Issue

**Status:** Pattern
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

An unfilled school-based therapy position is not just a recruiter miss — it may be a violation of a student's right to a Free Appropriate Public Education (FAPE) under IDEA. When an SLP or OT position goes unfilled for more than a brief period and IEP-mandated service hours are not delivered, the district faces compliance risk and the staffing firm faces a service failure. Treating IDEA-mandated position fill as a separate "compliance" matter that routes to legal rather than as a first-class operational KPI means that the urgency of the fill is underweighted in the operational priority stack. IDEA fill rate belongs on the operations dashboard, not in the legal-hold queue.

## How to apply

Flag IDEA-mandated positions in the fill-rate dashboard with elevated priority and track service-hours delivery alongside placement status:

```
IDEA-Mandated Position Tracker
────────────────────────────────
Period:  ________________
District:  ________________

Position | IEP mandate? | Students served | Service hrs/wk due | Days unfilled | Service hrs gap | Priority
─────────|--------------|----------------|---------------------|---------------|-----------------|──────────
SLP      | YES          | ___            | ___                 | ___           | ___             | URGENT
OT       | YES          | ___            | ___                 | ___           | ___             | URGENT
BCBA     | YES          | ___            | ___                 | ___           | ___             | HIGH
School psych | NO (eval queue) | ___     | —                   | ___           | —               | STANDARD

IDEA fill rate:  IEP-mandated positions filled ÷ IEP-mandated positions open = ___%
Service hours gap (this period):  ___ hours unfulfilled

Escalation threshold:
  [ ] Any IDEA position unfilled >5 days: notify district liaison + escalate to senior recruiter
  [ ] Service hours gap >10%: flag in executive readout
```

**Do:**
- Separate IDEA-mandated positions from non-mandated positions in the fill-rate dashboard — they carry different urgency and different compliance consequences.
- Calculate the service hours gap (how many hours of mandated service have not been delivered) as a compliance metric, not just a staffing metric.
- Include IDEA fill rate and service hours gap in the client readout to the district; districts are accountable for FAPE and they want to see this tracked.

**Don't:**
- Treat an unfilled IDEA-mandated position as equivalent to an unfilled general-education position in the priority queue — the legal and ethical stakes are different.
- Use teletherapy as an automatic substitute for in-person IDEA services without confirming that the student's IEP permits teletherapy delivery.
- Omit the IDEA fill rate from the scorecard on grounds that "compliance is legal's problem" — operations is accountable for delivering the service.

## Edge cases / when the rule does NOT apply

Evaluation-only positions (school psychologist referrals that do not yet have an IEP in place) are high priority but not technically IDEA-mandated service delivery. Track them separately; their urgency is high but the compliance clock runs differently.

## See also

- [`../agents/education-staffing-specialist.md`](../agents/education-staffing-specialist.md) — owns IDEA/IEP compliance mechanics and the service-hours gap calculation.
- [`./sell-school-based-on-compliance-not-headcount.md`](./sell-school-based-on-compliance-not-headcount.md) — the companion rule on positioning school-based services around IDEA compliance.

## Provenance

Codifies CLAUDE.md §3 #8 (compliance is not overhead — in these two segments it's the product) applied to IDEA-mandated position tracking. FAPE requirements under IDEA 2004 create an affirmative obligation for districts to deliver mandated services; unfilled positions that create service gaps are a compliance event [unverified — confirm interpretation with legal counsel for specific district situations].

---

_Last reviewed: 2026-06-05 by `claude`_
