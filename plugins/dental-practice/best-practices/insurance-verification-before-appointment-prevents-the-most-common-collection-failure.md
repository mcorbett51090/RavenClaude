# Insurance Verification Before Appointment Prevents the Most Common Collection Failure

**Status:** Absolute rule
**Domain:** Revenue cycle / front-end operations
**Applies to:** `dental-practice`

---

## Why this exists

The most common dental billing failure — presenting the wrong patient portion at checkout or filing a claim that returns underpaid — originates not at the billing desk but at the front desk before the appointment. When eligibility and benefits are not verified before the patient arrives, the treatment plan's financial presentation is based on guessed or outdated coverage. The result: surprise balances that patients dispute, payment delays, and write-offs the practice didn't budget. Insurance verification is the front-end action that protects the collection ratio the billing team is trying to defend at the back end.

## How to apply

Establish a verification workflow with a fixed lead time before every appointment.

```
Insurance verification workflow:
Timing:
  - New patients: verify 3–5 business days before appointment
  - Existing patients: verify at recare/recall or when treatment plan changes
  - High-value operative appointments ($1,000+): always verify regardless of recent coverage history

Verification checklist (per patient per appointment):
  [ ] Plan active and patient eligible on the date of service
  [ ] Annual maximum (individual): amount used YTD and remaining
  [ ] Deductible: individual and family — amount met YTD
  [ ] Coverage percentages by procedure category (preventive / basic / major)
  [ ] Waiting periods: any applicable for planned procedures?
  [ ] Missing tooth clause: applicable for implants or bridge?
  [ ] Frequency limitations: bitewings, perio, cleanings (date last completed)
  [ ] Pre-authorization required? If yes, submit before scheduling
  [ ] Network status: in-network with this plan under this group number?

Record:
  - Verification date, staff initials, and method (phone, online portal, EDI)
  - Attach to patient record in practice management software
```

**Do:**
- Build verification into the scheduling workflow, not as an afterthought — do it when the appointment is booked.
- Re-verify when a patient reports an insurance change at any point.
- Confirm with the patient at check-in that their insurance information is current — patients often change plans without notifying the practice.

**Don't:**
- Assume that because a patient was verified last month, they are verified for today's appointment — annual maximums, plan changes, and employment terminations happen between visits.
- Rely on the Explanation of Benefits (EOB) as a substitute for pre-visit verification — the EOB tells you what happened, not what will happen.
- Skip verification for "simple" prophylaxis appointments — missing tooth clause and frequency limitation denials happen on routine visits too.

## Edge cases / when the rule does NOT apply

Fee-for-service only practices (no insurance accepted) do not need insurance verification — but they should verify the patient's identity and confirm the financial policy is understood at each appointment.

## See also

- [`../agents/dental-rcm-specialist.md`](../agents/dental-rcm-specialist.md) — owns the downstream billing workflow that insurance verification feeds.
- [`./collections-not-production-pay-the-bills.md`](./collections-not-production-pay-the-bills.md) — verification protects the collection ratio by eliminating surprise-balance disputes.

## Provenance

Standard dental billing and front-office operations practice; grounded in ADA CDT coding guidance and dental billing best practices from organizations including the American Association of Dental Office Management (AADOM) and dental billing certifications.

---

_Last reviewed: 2026-06-05 by `claude`_
