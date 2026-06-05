---
description: "Prepare a referral-partner business review — an outline led by patient and family OUTCOMES (timely admits, symptom relief, avoided readmissions, family support), not the agency's referral count, with an honest assessment and a joint action plan."
argument-hint: "[partner + data, e.g. 'Memorial SNF, Q2: 18 referrals, 14 admits, 1.4-day avg time-to-admit, 1 complaint resolved']"
---

# Prep a referral-partner review

You are running `/hospice-referral-sales:prep-referral-review`. Build a partner review for the partner/data the user gave (`$ARGUMENTS`), using this plugin's `referral-account-manager` discipline and the `referral-account-planning` skill.

## Steps

1. **Gather the inputs** — period, referrals received, admits, time-to-admit, service incidents, the partner's goals. Flag which numbers are real vs placeholder. **Program-level data only — no patient-identifying data.**
2. **Build the 5-part review outline:**
   - Patient-access recap (factual, one slide).
   - **Outcomes delivered** — tied to the partner's pressures (readmission avoidance, length-of-stay relief, family satisfaction, after-hours responsiveness). Lead here.
   - Honest assessment — what was hard, owned plainly.
   - Shared goals — the **partner's** objectives and how you support them.
   - Joint action plan — actions with **named owners + dates**, both sides.
3. **Surface whitespace** — units/physicians/service lines not yet referring, and the earlier-referral opportunity, as a growth thread.
4. **Flag any service-recovery item** to address head-on; run the declined-referral root-cause tree if referrals dropped.
5. Emit in the Output Contract format + the Structured Output JSON block.

## Guardrails

- Lead with patient/family outcomes, never the agency's referral count.
- A review without a joint action plan (owners + dates) is a status meeting — don't ship one.
- **Any gift/meal/sponsorship to retain or grow the partner → route to `hospice-sales-compliance-advisor` first.**
- No patient-identifying data; use counts and rates.
