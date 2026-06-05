# HCC Capture Is a Documentation and Revenue Integrity Obligation

**Status:** Pattern
**Domain:** Medical coding / value-based care
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

For practices with Medicare Advantage (MA) patients and value-based care contracts using risk adjustment, Hierarchical Condition Category (HCC) codes drive the per-patient risk-adjustment factor (RAF) that determines the practice's and payer's prospective payment. Under-coding HCCs — failing to document and code chronic conditions that are present and being managed — results in an artificially low RAF, which underestimates the patient population's actual acuity and can reduce capitation or quality bonus payments. This is not a billing optimization game; HCC capture is a documentation accuracy obligation — coding HCCs that are not present and being managed is fraud, but failing to capture HCCs that are documented and managed is leaving legitimate revenue uncollected.

## How to apply

Integrate HCC review into the annual wellness visit and problem-management documentation workflow.

```
HCC capture workflow:

Pre-visit (for established MA patients):
  [ ] Pull the patient's prior-year HCC list from the MA encounter data or care-gap tool
  [ ] Flag: any HCC documented last year that has not been coded yet this year
      (HCCs must be re-confirmed annually — they do not roll forward automatically)
  [ ] Flag: care gaps that suggest an undocumented chronic condition
      (e.g., multiple A1c checks without a diabetes diagnosis; beta blocker on the med list
      without a documented CAD or CHF diagnosis)

At the visit (clinical documentation standard):
  [ ] Each chronic condition being managed: documented as active in the assessment
      (not in the past history only — active problems must be in the assessment)
  [ ] MEAT criteria satisfied for coded chronic conditions:
      Monitor, Evaluate, Assess, Treat — at least one applies for each coded condition
  [ ] All conditions addressed in the visit's assessment, not just the chief complaint

Post-visit (coding):
  [ ] Coder reviews assessment for HCC-eligible ICD-10 codes
  [ ] Unspecified codes used only when specificity is unavailable (avoid default to unspecified)
  [ ] HCC capture rate tracked: % of MA patients with at least one HCC coded per year

Annual HCC reconciliation:
  - Compare prior-year HCC list to current-year coded encounters
  - Gap = conditions that should have been re-confirmed but weren't → outreach for follow-up
  - Track: HCC capture rate per provider; variation > 20% between providers → coding and
    documentation review
```

**Do:**
- Educate providers that HCC capture starts with clinical documentation — a chronic condition managed but not mentioned in the assessment is invisible to the coder.
- Use a pre-visit HCC gap report as a clinical workflow tool, not just a billing prompt — it is also a care quality reminder.
- Track annual HCC capture rate per provider for MA patients as part of the value-based care performance dashboard.

**Don't:**
- Code an HCC without clinical documentation that the condition was evaluated or managed at that encounter — MEAT criteria compliance is required for code justification.
- Confuse HCC capture improvement with upcoding — accurate capture of documented, managed conditions is compliance-compliant; adding codes for conditions not mentioned in the encounter documentation is fraud.
- Apply this workflow only to the annual wellness visit; high-acuity patients should have their conditions re-confirmed at any qualifying visit.

## Edge cases / when the rule does NOT apply

Fee-for-service Medicare without a value-based care arrangement does not have risk-adjustment payments and HCC capture does not affect payment directly. The documentation and accuracy principles still apply for continuity of care and for any future payer-mix changes.

## See also

- [`../agents/medical-coding-specialist.md`](../agents/medical-coding-specialist.md) — owns HCC coding accuracy as part of the value-based care coding portfolio.
- [`../agents/rcm-analytics-analyst.md`](../agents/rcm-analytics-analyst.md) — HCC capture rate and RAF analytics belong in the value-based care scorecard.

## Provenance

Grounded in CMS HCC Risk Adjustment Model documentation and Medicare Advantage risk-adjustment rules; MEAT criteria framework from CMS risk-adjustment training; OIG guidance on HCC coding compliance.

---

_Last reviewed: 2026-06-05 by `claude`_
