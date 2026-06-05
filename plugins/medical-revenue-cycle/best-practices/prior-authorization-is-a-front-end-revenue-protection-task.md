# Prior Authorization Is a Front-End Revenue Protection Task

**Status:** Absolute rule
**Domain:** Prior authorization / front-end operations
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

Prior authorization (PA) requirements have increased substantially — a 2023 AMA survey found that 94% of physicians reported care delays from PA requirements, and prior-authorization denials are one of the fastest-growing denial categories. [unverified — training knowledge] A claim for a service that required PA and did not have one will be denied, and the window to obtain retro-authorization (if it exists at all) is narrow. The PA workflow is a front-end task — it must be completed before the service is delivered, not after. Practices that treat PA as the billing team's problem after the claim denies are paying a rework cost and a denial rate that was entirely preventable.

## How to apply

Build PA as an upstream workflow step in scheduling and registration, not a billing-office rescue.

```
Prior authorization front-end workflow:
Step 1 — At scheduling:
  - Check payer's PA requirement for the CPT code(s) planned
  - Sources: payer portal, provider line, or integrated PA tool (e.g., Availity, Olive, Infinitus)
  - If PA required: initiate PA request at scheduling, not at check-in

Step 2 — PA submission:
  - Clinical documentation attached at submission: must match payer's criteria
  - Turnaround time tracked: standard PA = 72 hours; urgent/expedited = 24–72 hours (payer-specific)
  - PA reference number logged in the scheduling/PM system before the date of service

Step 3 — Pre-service confirmation:
  - Confirm PA number is in the system before the patient arrives
  - If PA pending or denied at T-48 hours: contact payer for status, initiate peer-to-peer if denied
  - PA for procedures ≥$500 patient cost: notify patient of pending PA before the appointment

Step 4 — Claims pairing:
  - Attach PA number to the claim on submission (Box 23 on CMS-1500; field varies for UB-04)
  - Denial management: PA-related denial → verify PA number was attached before appealing

PA tracking metrics (monthly):
  - PA approval rate: target ≥85% first submission [unverified — training knowledge]
  - PA-related denial rate: track as a separate denial category
  - PA turnaround time average: flag if >5 business days (impacting scheduling)
```

**Do:**
- Maintain a payer-specific PA requirement matrix (updated quarterly) so staff don't have to look up requirements from scratch at each request.
- Peer-to-peer appeal every PA denial before accepting it — physician peer-to-peer reversal rates are significantly higher than administrative appeal rates. [unverified — training knowledge]
- Log PA expiration dates and set a 30-day-out reminder for scheduled services approved far in advance.

**Don't:**
- Assume last month's approval for the same code applies to this patient — PA is patient-specific and payer-specific.
- Submit a claim for a PA-required service without a PA number and then blame the payer for the denial.
- Wait for the denial to learn that a PA was required — payer portal and provider line checks are free and immediate.

## Edge cases / when the rule does NOT apply

Medicare fee-for-service traditionally has limited prior-authorization requirements (though this is expanding for certain services and select plans). Medicaid and Medicare Advantage PA requirements are program-specific and must be checked individually.

## See also

- [`../agents/denials-management-specialist.md`](../agents/denials-management-specialist.md) — PA-related denials are a top-category denial; root cause is front-end process, not billing.
- [`./front-end-errors-are-back-end-denials-fix-them-upstream.md`](./front-end-errors-are-back-end-denials-fix-them-upstream.md) — PA is the most common front-end failure type by denial dollar volume.

## Provenance

Codifies the front-end-errors-are-back-end-denials principle (CLAUDE.md §3 #6) for the PA use case; grounded in AMA Prior Authorization Physician Survey (2023) and CMS PA transparency rule; standard RCM operations practice.

---

_Last reviewed: 2026-06-05 by `claude`_
