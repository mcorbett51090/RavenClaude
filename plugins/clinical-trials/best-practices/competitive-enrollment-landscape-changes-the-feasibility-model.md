# Competitive Enrollment Landscape Changes the Feasibility Model

**Status:** Primary diagnostic
**Domain:** Enrollment feasibility / competitive intelligence
**Applies to:** `clinical-trials`

---

## Why this exists

A protocol feasibility model that ignores competing trials in the same indication at the same sites is systematically overoptimistic. When multiple sponsors are running trials in a therapeutic area, sites and eligible patients are shared resources — a patient already enrolled in a competitor trial is ineligible for yours by protocol (concurrent enrollment exclusions) or by practical IRB limits. Missing this competitive factor leads to feasibility estimates that look achievable in isolation but fail in the market. Enrollment shortfalls caused by competitive landscape are one of the most common and most preventable causes of trial delays.

## How to apply

Include a competitive landscape check as a standard step in the feasibility model before finalizing site selection and enrollment projections.

```
Competitive enrollment assessment:
1. Identify competing studies (ClinicalTrials.gov + EudraCT/CTIS search):
   - Same indication and phase
   - Overlapping eligibility criteria
   - Same site network or geographic region
   - Status: Recruiting or Not Yet Recruiting

2. Quantify the overlap:
   - Shared sites: how many of your planned sites are running a competing trial?
   - Patient pool overlap: what % of your target population would also be eligible for the competitor?
   - Typical concurrent enrollment exclusion clause check: does the competitor exclude your patients?

3. Adjust the enrollment model:
   - Apply a competitive dilution factor (commonly 15–40% reduction in site-level enrollment
     rate for shared sites in high-competition indications) [unverified — training knowledge]
   - Flag sites with ≥2 competing active trials as high-risk; consider replacing or adding backup sites

4. Monitor continuously:
   - Set ClinicalTrials.gov alerts for new studies in the same indication
   - Revisit the competitive model at each enrollment review (quarterly minimum)
```

**Do:**
- Run the competitive landscape check before the site identification list is finalized, not after activation.
- Inform sites of the competitive situation and ask them to report when a competing trial opens at their site.
- Model a "competitor opens at 50% of your sites" scenario as a risk case in the enrollment timeline.

**Don't:**
- Use "patients exist in this indication" as the only feasibility basis — available patients and enrollable patients are different numbers.
- Treat ClinicalTrials.gov as the only source; EudraCT/CTIS captures EU studies not always registered on the US registry.
- Ignore sponsor pipeline databases — a competitor that has not yet opened but is in the activation pipeline can still affect your recruitment window.

## Edge cases / when the rule does NOT apply

Orphan disease / ultra-rare disease trials where no competing study exists or the patient population is globally unique — the competitive overlay is less material, though patient advocacy groups may still represent a shared resource.

## See also

- [`../agents/protocol-design-specialist.md`](../agents/protocol-design-specialist.md) — owns the feasibility model where the competitive adjustment is applied.
- [`../agents/trials-engagement-lead.md`](../agents/trials-engagement-lead.md) — competitive landscape framing belongs in the engagement scope.
- [`./enrollment-is-a-rate-not-a-count-track-the-funnel.md`](./enrollment-is-a-rate-not-a-count-track-the-funnel.md) — competitive dilution reduces the rate, not just the ceiling.

## Provenance

Standard sponsor/CRO feasibility practice; grounded in recurring IQVIA, Medidata, and Tufts CSDD analyses of enrollment delay causes; competitive overlap as a delay factor is consistently in the top-five findings across published enrollment analyses.

---

_Last reviewed: 2026-06-05 by `claude`_
