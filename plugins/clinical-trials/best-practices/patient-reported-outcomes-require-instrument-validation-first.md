# Patient-Reported Outcomes Require Instrument Validation First

**Status:** Absolute rule
**Domain:** Protocol design / endpoints
**Applies to:** `clinical-trials`

---

## Why this exists

Patient-reported outcome (PRO) instruments that have not been validated for the target population, language, and disease state are not accepted by FDA or EMA as primary or key secondary endpoints. The FDA PRO Guidance (2009) and EMA Reflection Paper on PROs both require evidence that the instrument measures what it claims to measure (validity) in the specific context of use. A trial that reaches completion with an unvalidated PRO as its primary endpoint faces rejection of the endpoint entirely — not a request for more data, but a structural deficiency that cannot be remediated post-hoc.

## How to apply

Before locking a protocol that includes a PRO endpoint, complete a three-step validation check:

```
PRO instrument validation checklist:
Step 1 — Identify the instrument's regulatory qualification status
  [ ] Has the instrument been reviewed/qualified by FDA (e.g., FDA Drug Development Tool)?
  [ ] Has EMA issued a qualification opinion for this indication and population?
  [ ] If not formally qualified: is there peer-reviewed published psychometric validation
      in the specific disease area and patient population?

Step 2 — Check linguistic validation for all trial languages
  [ ] Is a linguistically validated version available for each study country/language?
  [ ] Has back-translation been completed and reviewed by the rights holder?
  [ ] Is a license agreement in place with the instrument copyright holder?

Step 3 — Align administration mode with the validation basis
  [ ] Is the administration mode (paper vs. ePRO) the same as in the validation studies?
  [ ] Has mode-of-administration equivalence been established if different?
  [ ] Is the recall period (e.g., "past 7 days") identical to the validated version?
```

**Do:**
- Discuss PRO instrument selection with the FDA/EMA early in the development program, not at protocol finalization.
- Use the exact validated version — do not modify items, response options, or recall periods without re-validation.
- Pre-specify the PRO analysis plan (handling of missing data, responder thresholds) in the statistical analysis plan before unblinding.

**Don't:**
- Use a PRO instrument because it is "widely used" without verifying its regulatory qualification status in your specific indication.
- Assume an instrument validated in adults is appropriate for pediatric populations.
- Change the PRO administration mode (paper → ePRO) mid-trial without equivalence data.

## Edge cases / when the rule does NOT apply

Exploratory PRO endpoints in early-phase trials (phase I, pilot feasibility) where the instrument is used to inform later-phase design, not as a regulatory endpoint, are outside this rule's strictest application — but the same instrument should be planned for later phases using a compliant version.

## See also

- [`../agents/protocol-design-specialist.md`](../agents/protocol-design-specialist.md) — owns endpoint selection and protocol operability assessment.
- [`../agents/regulatory-submissions-specialist.md`](../agents/regulatory-submissions-specialist.md) — PRO qualification status affects submission structure and labeling claims.

## Provenance

Grounded in FDA Guidance for Industry: Patient-Reported Outcome Measures (2009); EMA Reflection Paper on the Regulatory Guidance for the Use of Health-Related Quality of Life Measures in the Evaluation of Medicinal Products; ICH E9(R1) estimand framework as applied to PRO endpoints.

---

_Last reviewed: 2026-06-05 by `claude`_
