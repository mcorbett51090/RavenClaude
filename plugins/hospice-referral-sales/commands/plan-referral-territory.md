---
description: "Plan or re-plan a hospice referral territory — segment the referral sources, prioritize by volume × eligibility density × relationship gap, and build a per-segment outreach + in-service plan. Patient-access-led; every value exchange routes to compliance."
argument-hint: "[territory + sources, e.g. '3 hospitals, 8 SNFs, 5 cardiology + 2 oncology practices in north county']"
---

# Plan a referral territory

You are running `/hospice-referral-sales:plan-referral-territory`. Build a territory plan for the sources the user gave (`$ARGUMENTS`), using this plugin's `referral-development-strategist` discipline and the `referral-territory-development` skill.

## Steps

1. **Segment the sources** — hospitals (discharge planning / case management / hospitalists / palliative / units), SNF/ALF, physician practices (PCP / cardiology / pulmonology / oncology / nephrology), dialysis, ACOs, family networks. Name each segment's driver.
2. **Prioritize** — rank by **volume potential × eligibility density × relationship gap** (traverse `## Decision Tree: Referral-source prioritization`). Convenience is a tie-breaker, not the sort key. Flag where eligibility density is an estimate to confirm.
3. **Per-segment plan** — the trigger event, the first-value offer, the in-service topic (clinical content from `hospice-eligibility-educator`), and the multi-touch cadence.
4. **In-service calendar** — recurring education to keep producing referrals; flag any meal/refreshment/sponsorship for compliance clearance.
5. Emit the plan in the Output Contract format + the Structured Output JSON block.

## Guardrails

- Lead with patient access and the source's pressures, never the agency's admit count.
- Prioritize by eligibility density, not by who's easiest to visit.
- **Any meal, gift, sponsorship, or arrangement in the plan → flag it for `hospice-sales-compliance-advisor` before it happens.** Never embed an un-cleared value exchange.
- No patient-identifying data anywhere in the plan.
