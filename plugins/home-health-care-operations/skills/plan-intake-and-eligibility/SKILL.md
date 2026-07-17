---
name: plan-intake-and-eligibility
description: "Take a home-health / home-care referral through intake by traversing the home-health decision tree (referral → service-line class: skilled home health vs non-medical home care → eligibility & benefit verification: Medicare homebound + skilled need / Medicaid-waiver authorization / private-pay → the physician-order + face-to-face + certification gate → initial plan of care), then return the verified eligibility, the cleared order gate, the start-of-care date, and the initial plan of care. Reach for this when the user asks 'get this referral through intake', 'is this patient eligible for home health?', 'do we have the physician order / face-to-face?', or 'set up the plan of care'. Used by home-care-operations-specialist (primary) and home-health-agency-lead."
---

# Skill: plan-intake-and-eligibility

> **Invoked by:** `home-care-operations-specialist` (primary, for the intake + eligibility + order build) and `home-health-agency-lead` (to ground the service-line/payer strategy in a real eligibility model).
>
> **When to invoke:** "get this referral through intake"; "is this patient eligible for skilled home health?"; "verify their benefits / authorization"; "do we have the physician order and the face-to-face?"; "set up the initial plan of care"; any "can we start care and get paid" question.
>
> **Output:** the verified eligibility & benefits (per payer) + the cleared physician-order/certification gate + the start-of-care date (gated on the order) + the initial plan of care + the 1-2 conditions that would delay or deny the start.

## Procedure

1. **Classify the service line first — skilled home health vs non-medical home care.** **Skilled home health** = intermittent skilled nursing / therapy under a physician's plan of care (typically Medicare / Medicaid / managed care). **Non-medical / private-duty home care** = personal care, ADLs, homemaking, companionship (typically private pay / Medicaid waiver / long-term-care insurance). The class drives the eligibility gate and the payer path — get it right before verifying anything.
2. **Verify eligibility against the payer's gate.** Traverse the eligibility branch in [`../../knowledge/home-health-care-decision-tree.md`](../../knowledge/home-health-care-decision-tree.md):
   - **Medicare skilled home health** — confirm **homebound status**, a **skilled need** (skilled nursing, PT/OT/SLP), **intermittent** care, a **Medicare-certified** agency, and that a **physician/allowed practitioner** is managing care. All four gates, not just one.
   - **Medicaid waiver** — confirm the **waiver program**, the **service authorization** (approved units, service type, effective dates), and any managed-care plan.
   - **Private pay / LTC insurance** — confirm the **agreement, rate, and hours**, and any insurance benefit/elimination period.
3. **Verify benefits and coverage before the visit, not after.** Check active coverage, the benefit period, prior-authorization requirements, any patient responsibility (copay/coinsurance), and — for Medicare — that the episode isn't already open with another agency (transfer rules). A benefit surprise after care starts is an uncompensated visit.
4. **Clear the physician-order + face-to-face + certification gate.** For skilled home health this is the hard gate: a **signed physician order**, a **face-to-face encounter** (within the required window, related to the primary reason for home health), and the **certification** of eligibility. **The start-of-care date is gated on the signed order** — you may perform the initial assessment, but billing and the certified plan turn on the order. Missing/late orders are the top denial and survey-finding source.
5. **Set up the initial plan of care.** Build the physician-ordered plan of care: diagnoses, the skilled services and **visit frequency/duration** per discipline, goals, the OASIS-driven start-of-care assessment (for skilled HH), and the authorized units/schedule (for waiver/private pay). The plan of care is what the schedule and the claim are built against.
6. **Set the start-of-care date and confirm it's defensible.** Establish SOC on the cleared order and the completed assessment — and confirm the whole chain (eligibility verified, benefits confirmed, order/F2F/certification signed, plan of care set) is documented, because the intake packet is the first thing a surveyor or a payer audits.
7. **State the delay/deny conditions** — the 1-2 facts that would hold or deny the start (e.g., "the face-to-face is outside the window → re-obtain before certifying"; "the waiver authorization is for fewer units than the ordered frequency → reconcile before scheduling").

## Worked example

> User: "Hospital discharge referral — 78-year-old post-CHF-exacerbation, needs skilled nursing and PT at home. Get them through intake."

- **Service line:** **skilled home health** (skilled nursing + PT under a physician plan) — Medicare primary.
- **Eligibility:** confirm **homebound** (leaving home requires taxing effort / assistance), the **skilled need** (CHF management, medication teaching, PT for deconditioning), **intermittent** care, and a **Medicare-certified** agency — all four gates clear.
- **Benefits:** Medicare Part A/B active, no open episode with another agency (hospital-to-home transfer, not a conflict).
- **Order gate:** obtain the **signed physician order** and confirm the **face-to-face** encounter (the CHF hospitalization qualifies, within the window); **certification** of eligibility signed → **SOC date set on the order**, not the discharge date.
- **Plan of care:** SN 2-3x/wk tapering, PT 2x/wk, medication/diet teaching, weight monitoring; OASIS start-of-care assessment completed → drives the PDGM case mix.
- **Delay condition:** if the face-to-face documentation doesn't tie to the primary home-health reason, certification is at risk → re-obtain before billing.

## Guardrails

- **Classify the service line first** (skilled HH vs non-medical home care) — it drives the eligibility gate and the payer path.
- **Verify eligibility and benefits before the first visit** — a coverage surprise after care starts is an uncompensated visit.
- **The physician order + face-to-face + certification is the hard gate** for skilled home health — the **start-of-care date is gated on the signed order**, not the referral date.
- **Match the plan of care to the authorization** — an ordered frequency that exceeds the waiver's authorized units is unpaid work; reconcile before scheduling.
- Verifying eligibility is **execution** (the operations specialist); the **payer-mix strategy** that decides which referrals to take is **policy** (the `home-health-agency-lead`) — keep the seam clean.
- This is **not** hospital/physician-group RCM — that's `medical-revenue-cycle`; this plugin owns the **home-health agency's** intake.
- Volatile specifics (Medicare homebound/face-to-face criteria, certification windows, waiver authorization rules) carry a **retrieval date** and are re-verified before certifying or billing. See [`../../knowledge/home-health-care-patterns-2026.md`](../../knowledge/home-health-care-patterns-2026.md). **Not medical, legal, or reimbursement advice.**
