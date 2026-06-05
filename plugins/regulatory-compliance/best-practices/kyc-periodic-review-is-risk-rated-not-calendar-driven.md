# KYC Periodic Review Frequency Is Driven by Risk Rating, Not a Fixed Calendar

**Status:** Absolute rule
**Domain:** AML / KYC
**Applies to:** `regulatory-compliance`

---

## Why this exists

Many firms run KYC periodic reviews on a uniform annual or triennial calendar regardless of the customer's risk profile. A high-risk PEP reviewed every three years receives the same cadence as a low-risk domestic retail customer reviewed annually — which means neither is calibrated correctly. FATF Recommendation 10, and most national AML rules implementing it, require that CDD be ongoing and proportionate to risk; a fixed calendar that ignores the risk rating is a program design deficiency, not just a process inefficiency. Regulators also look at whether adverse-media hits, transaction-pattern changes, or material life events trigger an out-of-cycle review — a pure calendar approach misses all of those.

## How to apply

Set review frequency as a function of the customer's risk rating, with explicit trigger-based out-of-cycle escalation.

```
Periodic Review Schedule — Risk-Calibrated
────────────────────────────────────────────
Risk Rating     | Standard review cycle | Out-of-cycle triggers
────────────────|───────────────────────|──────────────────────
High            | Annual (12 months)    | Adverse media hit; OFAC/sanctions designation;
                |                       | unexplained transaction pattern; material
                |                       | change in ownership/control; senior-level
                |                       | regulatory inquiry
Medium          | Every 2 years         | Same triggers as high risk
Low             | Every 3–5 years       | Same triggers; use EDD escalation procedure
                |                       | if trigger elevates to medium or high

Out-of-cycle review:
  Trigger documented → assigned to reviewer → completed within 30 days of trigger
  (or within 5 business days for a sanctions-related trigger)
  Result: maintain rating | escalate rating | exit relationship
```

**Do:**
- Document the risk-rating basis at the point of review, not just the outcome — the review record must show why the rating changed (or didn't).
- Include an adverse-media search as a standard step in every periodic review, regardless of risk tier; log the search date and source.
- Feed transaction-monitoring anomalies and compliance-team alerts directly into the out-of-cycle trigger workflow.
- Retain the completed periodic review record for the full retention period applicable in the jurisdiction.

**Don't:**
- Run periodic reviews solely on calendar date without re-rating the customer as part of the review — a review that does not re-assess the risk rating is a document-gathering exercise, not a risk-management control.
- Batch schedule all high-risk reviews for the same month every year — this creates a peak-load failure where reviews are rubber-stamped to clear the queue.
- Allow the periodic review to be completed by the same relationship manager who onboarded the customer without a second-line QA step.

## Edge cases / when the rule does NOT apply

- **Dormant accounts** with no activity and no product permitting activity — the regulator's position varies; document the firm's policy for dormant-account review timing and get it approved by the CCO.
- **Exit-relationship customers** — the review cycle stops at exit; retain the final file in compliance with the retention schedule.

## See also

- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — owns the KYC periodic review and EDD trigger disciplines.
- [`./aml-risk-rate-before-you-choose-cdd-depth.md`](./aml-risk-rate-before-you-choose-cdd-depth.md) — the upstream rule; the risk rating set at onboarding is the denominator the periodic review re-validates.

## Provenance

Codifies the AML/KYC periodic review discipline from the CLAUDE.md house opinion on ongoing CDD and the `kyc-edd-review` skill. The risk-rated frequency tiers and out-of-cycle trigger framework reflect FATF Recommendation 10 implementation standards and standard BSA/AML examination expectations.

---

_Last reviewed: 2026-06-05 by `claude`_
