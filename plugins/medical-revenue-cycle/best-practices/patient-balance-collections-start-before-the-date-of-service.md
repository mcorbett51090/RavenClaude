# Patient Balance Collections Start Before the Date of Service

**Status:** Absolute rule
**Domain:** Patient financial experience / collections
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

Patient out-of-pocket responsibility has increased dramatically with the rise of high-deductible health plans (HDHPs) — the patient is now the third-largest payer for most practices. [unverified — training knowledge] Despite this, most practices still operate as if patient collections happen at or after checkout: they bill the insurance, receive the EOB, and then mail the patient a statement for the residual balance. This sequence is both slow (statements typically arrive 30–45 days after the date of service) and low-yield (collections drop sharply the longer the balance ages after service). Pre-service patient financial engagement — estimating and collecting at least the deductible or co-payment before the appointment — is the highest-yield patient collection strategy.

## How to apply

Build a pre-service patient financial engagement workflow for all scheduled appointments.

```
Pre-service patient financial workflow:
1. Pre-service benefit investigation (done at eligibility verification — see front-end rule):
   - Deductible: amount applied YTD, amount remaining
   - Out-of-pocket maximum: amount applied YTD
   - Co-pay or co-insurance for the planned service

2. Patient financial estimate:
   - Prepare a good-faith estimate for the planned service
     (ACA No Surprises Act requires a good-faith estimate for self-pay patients;
      best practice extends a similar estimate to all patients)
   - Estimate format: service, contracted allowed amount (or charge), expected insurance,
     expected patient responsibility

3. Pre-service collection:
   - Collect co-pay at or before check-in (before service is delivered)
   - For patients with known deductible remaining: request a deposit toward expected
     patient responsibility before or at check-in
   - For high-cost scheduled procedures (surgery, imaging): collect expected patient
     responsibility 3–5 business days before the date of service

4. Payment options at checkout:
   - Offer: card on file, payment plan, or payment portal
   - All staff trained: the question is not "do you want to pay today?" but "how would
     you like to pay today?"

5. Statement cycle for residual balances:
   - Issue statement within 5 business days of EOB receipt
   - Statement cycle: 1st statement, 14-day automated reminder, 30-day final notice,
     then collections decision (see A/R aging rule)
```

**Do:**
- Collect co-pays before service, not after — services already rendered create leverage loss.
- Train front-desk staff on patient financial conversations as a standard skill, not an uncomfortable exception.
- Offer a payment plan option at check-in for patients who report financial difficulty — a structured payment plan is better than a collection agency referral.

**Don't:**
- Refuse service to established patients because of an outstanding balance without following EMTALA and state law requirements — this is both a legal risk and a reputation risk.
- Present the patient financial estimate as a bill — it is an estimate; the statement comes after the EOB.
- Allow the pre-service workflow to depend solely on front-desk staff in the waiting room — it must begin before the patient arrives.

## Edge cases / when the rule does NOT apply

Emergency services are subject to EMTALA — patient financial conversations and collections cannot condition or delay emergency screening or stabilization. The pre-service workflow applies only to scheduled, non-emergency appointments.

## See also

- [`../agents/denials-management-specialist.md`](../agents/denials-management-specialist.md) — patient balance work-down is a component of the A/R management portfolio.
- [`./front-end-errors-are-back-end-denials-fix-them-upstream.md`](./front-end-errors-are-back-end-denials-fix-them-upstream.md) — pre-service financial engagement is the patient-responsibility analog of insurance front-end work.

## Provenance

Codifies the front-end-errors-are-back-end-denials principle (CLAUDE.md §3 #6) for the patient collections context; grounded in HFMA patient-friendly billing guidelines, ACA No Surprises Act good-faith estimate requirements, and standard patient financial engagement practice.

---

_Last reviewed: 2026-06-05 by `claude`_
