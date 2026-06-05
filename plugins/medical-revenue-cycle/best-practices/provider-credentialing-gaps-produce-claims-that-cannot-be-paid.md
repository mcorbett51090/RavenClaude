# Provider Credentialing Gaps Produce Claims That Cannot Be Paid

**Status:** Absolute rule
**Domain:** Provider credentialing / revenue cycle
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

A provider who is not credentialed with a payer cannot be paid by that payer for services rendered to that payer's patients — period. Claims submitted for an uncredentialed provider are either denied outright or adjudicated to $0 paid (depending on the payer). This is not a billing error or an appeal opportunity; the claim fails at the eligibility check before adjudication. Credentialing gaps are most common when a new provider joins the practice and begins seeing patients before credentialing is complete, and when a provider joins a new practice but the credentialing roster update is delayed. The revenue loss from a credentialing gap can exceed $50k per month for a full-time provider at a moderately productive practice. [unverified — training knowledge]

## How to apply

Build provider credentialing status into the scheduling and billing pre-service workflow.

```
Credentialing gap prevention:
1. New provider onboarding timeline:
   - Begin credentialing applications to all relevant payers ≥90 days before the provider's
     start date (Medicare initial enrollment can take 60–120 days; commercial payers vary)
   - Track application status weekly for each payer
   - Do not schedule the new provider with patients whose insurance requires credentialing
     until the effective date is confirmed

2. Credentialing roster (maintain and update monthly):
   - Column: Provider NPI
   - Column: Payer / Plan
   - Column: Effective credentialing date
   - Column: Re-credentialing due date (typically every 2–3 years)
   - Column: Current status (active / pending / expired)

3. Scheduling guard:
   - Configure PM system: when scheduling a patient, flag if the rendering provider is
     not credentialed with the patient's payer
   - For un-credentialed providers with pending applications: schedule only self-pay patients
     or refer to a credentialed colleague until the effective date is confirmed

4. Retroactive credentialing:
   - Some payers allow retroactive credentialing back to the application date
   - If services were rendered before the effective date: check for retroactive billing eligibility
     and refile as quickly as possible after the effective date is granted

5. Re-credentialing lapse alerts:
   - Set 90-day-out alerts for all provider re-credentialing due dates
   - A lapsed re-credentialing is equivalent to a new uncredentialed state for that payer
```

**Do:**
- Treat credentialing applications as time-sensitive operations work, not administrative paperwork — every week of delay is a week of lost revenue once the provider is seeing patients.
- Verify the effective credentialing date directly from the payer, not from the application acknowledgment — the acknowledgment is not an approval.
- Track the credentialing lag for each payer (application submitted to effective date) to improve planning for future hires.

**Don't:**
- Allow a new provider to see insured patients under a "group provider number" without confirming that the payer allows incident-to billing for this service type — incident-to billing rules are narrow and specialty-specific.
- Assume that credentialing with one plan means the provider is credentialed with all plans under that payer — individual plan credentialing requirements vary.
- File a retroactive claim without confirming the payer's retro policy in writing — verbal confirmation of retroactive billing rights is insufficient.

## Edge cases / when the rule does NOT apply

Self-pay patients and workers' compensation carriers often do not require credentialing in the same sense — they pay the provider directly under a different contractual or statutory framework. Confirm program-specific rules.

## See also

- [`../agents/rcm-engagement-lead.md`](../agents/rcm-engagement-lead.md) — credentialing gaps are a first-order scope item in an RCM engagement when a new provider is involved.
- [`./timely-filing-deadlines-are-hard-stops-not-soft-targets.md`](./timely-filing-deadlines-are-hard-stops-not-soft-targets.md) — credentialing gaps create timely filing risk when claims are held pending effective date.

## Provenance

Standard provider credentialing and RCM operations practice; grounded in Medicare enrollment processes (CMS 855 series forms), payer credentialing protocols, and CAQH ProView standard credentialing workflow; revenue loss estimates are [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
