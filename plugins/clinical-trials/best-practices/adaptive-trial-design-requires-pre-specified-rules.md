# Adaptive Trial Design Requires Pre-Specified Rules

**Status:** Absolute rule
**Domain:** Clinical trial design / regulatory
**Applies to:** `clinical-trials`

---

## Why this exists

Adaptive designs — interim analyses, sample-size re-estimation, seamless phase transitions — offer genuine efficiency gains, but every adaptation rule must be locked in the statistical analysis plan (SAP) before unblinded data are touched. A post-hoc adaptation invalidates the trial's Type I error control and will draw a complete response letter or refusal to file. The cost of a retroactive fix (protocol amendment, re-analysis, re-submission) dwarfs the cost of pre-specifying correctly.

## How to apply

Treat each adaptation as a named rule with four locked elements before interim analysis begins:

```
Adaptation rule:   <name>
Trigger condition: <observable threshold — e.g., "interim futility if P(success) < 0.05">
Decision boundary: <action taken at each branch — continue / stop / modify>
Alpha allocation:  <O'Brien-Fleming / Lan-DeMets / other — cite the method>
SAP section:       <version, date, and section number where this rule is documented>
```

**Do:**
- Lock all adaptation rules in the SAP before any interim analysis begins.
- Assign an independent Data Safety Monitoring Board (DSMB) or Data Monitoring Committee (DMC) to execute interim reviews.
- Pre-specify the alpha-spending function and document it in the SAP with the version date.
- Log every interim analysis in the trial master file with the blind-break date and personnel.

**Don't:**
- Add or modify an adaptation rule after unblinded data have been seen by anyone with a financial interest.
- Treat "the sponsor asked for a sample-size look" as a minor protocol deviation — it is a protocol amendment requiring IRB/EC review and regulatory notification.
- Conflate operational data reviews (safety only, by a blinded team) with statistical adaptations.

## Edge cases / when the rule does NOT apply

Pre-specification applies to all adaptive elements. Even purely operational changes (e.g., adding a site) require protocol amendment, but they do not require SAP amendment if they carry no statistical consequence. This rule does not apply to fixed-design trials with no pre-planned interim analyses.

## See also

- [`../agents/protocol-design-specialist.md`](../agents/protocol-design-specialist.md) — owns feasibility and protocol operability, including adaptive design review.
- [`../agents/regulatory-submissions-specialist.md`](../agents/regulatory-submissions-specialist.md) — owns SAP and submission documentation integrity.
- [`./the-submission-is-built-throughout-not-at-the-end.md`](./the-submission-is-built-throughout-not-at-the-end.md) — SAP is a submission document, assembled throughout, not at filing.

## Provenance

Codifies FDA Guidance for Industry "Adaptive Design Clinical Trials for Drugs and Biologics" (2019) and ICH E9(R1) Addendum on Estimands and Sensitivity Analysis. Standard regulatory practice for adaptive design control.

---

_Last reviewed: 2026-06-05 by `claude`_
