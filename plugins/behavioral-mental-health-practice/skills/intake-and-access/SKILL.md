---
name: intake-and-access
description: "Design or audit the end-to-end intake and access workflow for an outpatient behavioral health practice: inquiry capture, clinical screening, scheduling, insurance verification, intake-packet delivery, and the no-show/waitlist management protocols that protect access."
---

# Intake and Access

**Purpose:** give the practice a repeatable, drop-off-minimizing pathway from first inquiry to first
appointment — and a waitlist and no-show protocol that keeps the schedule filled and access timely.

---

## The intake operating loop

1. **Capture every inquiry.** Phone, web form, referral, warm handoff — every channel must log the
   inquiry in the EHR/scheduling system within one business day. Uncaptured inquiries are invisible
   drop-offs.

2. **Screen for fit and urgency.** At first contact: confirm the practice serves the presenting
   concern, check payer/geography, and screen for clinical urgency (active suicidal ideation, crisis,
   high acuity) — if urgent, route immediately; do not put on a waitlist.

3. **Verify insurance before scheduling the first appointment.** Check: (a) eligibility and coverage
   dates, (b) behavioral health benefits (outpatient session limit, deductible, copay/coinsurance),
   (c) whether a prior authorization is required before the first session. If auth is required, start
   the request before the first appointment is scheduled. Escalate to `behavioral-billing-compliance-
   advisor` if Part 2 consent or authorization complexity is present.

4. **Schedule with intent.** Match the patient to a provider by modality, population, availability,
   and caseload capacity. Use the **intake slot type** (longer, assessment-focused) not a follow-up
   slot. Confirm the appointment at scheduling and set the reminder cadence (72h, 24h minimum).

5. **Deliver the intake packet.** Send before the first appointment: (a) consent for treatment,
   (b) HIPAA notice of privacy practices, (c) financial agreement, (d) ROI / consent-to-disclose
   form (Part 2-compliant if SUD services are offered), (e) demographic and intake questionnaire.
   Confirm receipt.

6. **Manage the waitlist actively.** A passive waitlist is a liability (clinical urgency may change).
   Re-confirm interest and clinical urgency at 2-week intervals. Offer a referral-out if wait exceeds
   a defined threshold (typically 4–6 weeks for non-urgent outpatient).

7. **Fill no-show slots from the waitlist.** A same-day cancellation is an access opportunity.
   Have a defined fill protocol: contact the top 3–5 active waitlist patients who can come in on
   short notice.

---

## No-show policy design

A no-show policy must be:

- **Documented** — in the intake packet and the financial agreement, signed at intake.
- **Communicated** — verbally at scheduling and in the reminder messages.
- **Consistently enforced** — inconsistent enforcement is worse than no policy (undermines trust
  and fills the schedule unevenly).

**Recommended components:**

| Element | Guidance |
| --- | --- |
| Cancellation window | 24–48 hours before appointment; 24h is the community standard |
| No-show fee | Optional; must comply with payer contracts (Medicaid typically prohibits). Disclose in financial agreement |
| Three-strike protocol | After 3 no-shows without notice, send a "re-engage or close slot" letter |
| Fill protocol | Contact waitlist on same-day cancel; build 1–2 buffer slots per provider per day |
| Safety exception | Document when a no-show fee is waived for a documented clinical reason |

Use `scripts/bh_calc.py no-show-rate` to calculate current rate and model the impact of a 5-point
reduction on effective capacity.

---

## Insurance verification checklist

Before the first appointment:

- [ ] Eligibility confirmed (active coverage on DOS)
- [ ] Behavioral health benefits confirmed (outpatient, individual, telehealth if applicable)
- [ ] Session limit (if any) noted and communicated to patient
- [ ] Deductible status and copay/coinsurance amount noted and communicated to patient
- [ ] Prior authorization requirement confirmed
- [ ] If auth required: auth request submitted before first session
- [ ] In-network vs. out-of-network status confirmed
- [ ] Document verification in EHR with date, verifier, and payer call reference number

---

## Anti-patterns

- An intake workflow with no insurance verification before the first session.
- A waitlist with no urgency re-screen or active confirmation cadence.
- A no-show policy stated in paperwork but never communicated verbally or enforced.
- Scheduling a patient without first confirming payer authorization requirements.
- Using a follow-up slot length for an intake appointment.

---

## Output

A documented intake workflow SOP (standard operating procedure) with: step-by-step flow, responsible
roles, EHR documentation standards, the no-show policy text, the waitlist protocol, and the
insurance verification checklist. Reference `templates/intake-packet.md` for the intake documents.
