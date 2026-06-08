# Measurement-based care improves outcomes

**Status:** Pattern
**Domain:** Clinical quality and documentation
**Applies to:** `behavioral-mental-health-practice`

---

## Why this exists

Measurement-based care (MBC) — the systematic use of validated patient-reported outcome instruments
at defined intervals — has a strong evidence base for improving clinical outcomes in behavioral
health. Practices that use MBC report higher rates of patient improvement, earlier detection of
treatment non-response, and lower rates of early dropout. It also has operational and compliance
benefits: MBC scores provide longitudinal, quantified documentation of clinical progress that
supports continued medical-necessity determinations at authorization renewals.

Despite the evidence, MBC adoption in outpatient behavioral health remains inconsistent. The barrier
is usually operational, not clinical — clinicians don't have a workflow for it in their EHR. This
rule is about operationalizing MBC, not about clinical decision-making.

## How to apply

**Do:**

- Select instruments from the publicly validated, widely accepted set for the practice's population
  (PHQ-9 for depression, GAD-7 for anxiety, PCL-5 for trauma, BASIS-24 for general severity).
  Instrument selection for clinical use is the clinician's decision; this plugin advises on commonly
  used instruments and their public scoring frameworks.
- Build MBC into the EHR workflow as a standardized, recurring task — not a one-time intake screen.
- Capture scores at a defined cadence (every session for PHQ-9/GAD-7; every 2–4 weeks for others).
- Display scores as a trend over time in the provider's chart view.
- Include the current score and trend in every progress note.
- Use scores at authorization renewals to document continued medical necessity (or treatment response).

**Don't:**

- Administer an MBC instrument at intake and never again.
- Capture scores but never display or discuss them with the patient.
- Use MBC scores as the sole determinant of clinical decision-making — they are one input.
- Select instruments outside the clinician's scope of practice or training.

## Edge cases / when the rule does NOT apply

- Some patient populations or presentations may not be appropriate for standard self-report
  instruments (e.g., patients with severe cognitive impairment, active psychosis, or very young
  children). Instrument adaptation or alternative measures are the clinician's determination.
- Group therapy settings may require different instruments or protocols than individual therapy.
- The specific instruments appropriate for a given patient type are a clinical determination;
  this plugin advises only on which instruments are commonly used in outpatient BH.

## See also

- [`./document-medical-necessity-for-every-service.md`](./document-medical-necessity-for-every-service.md)
- [`../skills/clinical-documentation-and-treatment-planning/SKILL.md`](../skills/clinical-documentation-and-treatment-planning/SKILL.md) — MBC instrument table and EHR workflow
- [`../knowledge/bh-practice-decision-trees.md`](../knowledge/bh-practice-decision-trees.md) — the 2026 MBC tools capability map

## Provenance

Codifies the MBC evidence base from the behavioral health outcomes literature (Fortney et al., Trivedi
et al., and the measurement-based care research base) and SAMHSA's recommendations for quality
measurement in outpatient behavioral health services. Instrument descriptions from public-domain
instrument documentation (PHQ-9: Spitzer/Kroenke, GAD-7: Spitzer/Kroenke, PCL-5: National Center
for PTSD). Clinical adoption decisions remain with the licensed clinician.

---

_Last reviewed: 2026-06-08 by `claude`._
