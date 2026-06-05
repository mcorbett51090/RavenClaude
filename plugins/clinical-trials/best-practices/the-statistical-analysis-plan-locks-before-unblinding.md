# The Statistical Analysis Plan Locks Before Unblinding

**Status:** Absolute rule
**Domain:** Biostatistics / regulatory
**Applies to:** `clinical-trials`

---

## Why this exists

The Statistical Analysis Plan (SAP) is the pre-specified contract between the trial and the regulator for how the primary and key secondary endpoints will be analyzed. Any analysis decision made after unblinding — subgroup definitions, multiplicity adjustments, missing data handling, sensitivity analysis selection — is potentially data-driven and therefore not pre-specified. Post-unblinding analysis changes are a red flag for data dredging in FDA and EMA review. A confirmatory trial that reaches NDA/BLA/MAA submission with a post-unblinding SAP amendment faces scrutiny that can delay or kill approval.

## How to apply

The SAP must be finalized and version-locked (sponsor QA signature + date) before the blind is broken. For interim analyses, the SAP for that interim must lock before the unblinding event for that interim.

```
SAP lock checklist:
[ ] Primary endpoint analysis: model, covariates, estimand (ICH E9(R1)) specified
[ ] Multiplicity control strategy documented (e.g., hierarchical testing, Bonferroni, gatekeeping)
[ ] Missing data handling: primary approach (e.g., MMRM, MI) and sensitivity analyses specified
[ ] Subgroup analyses: pre-specified subgroups listed with analysis method
[ ] Interim analysis(es): alpha spending function, stopping rules, DMC charter reference
[ ] Analysis populations defined: ITT/mITT, PP, safety — with exact inclusion/exclusion criteria
[ ] SAP version control: version number, date, sponsor QA signature before unblinding
[ ] Blinded data review documented: any SAP change after blinded data review must be dated
     and justified in the SAP revision history
```

**Do:**
- Conduct a formal blinded data review (checking data distributions without breaking the blind) before SAP lock to validate that model assumptions are supported.
- Document the blinded data review outcome and any resulting SAP changes with dates and rationale.
- Align the SAP with the ICH E9(R1) estimand framework — define the target estimand before specifying the analysis method.

**Don't:**
- Finalize subgroup definitions or sensitivity analysis sets after looking at unblinded data, even informally.
- Allow the database lock and SAP lock to be treated as simultaneous events — the SAP must lock first.
- Omit the analysis population definitions; ambiguous "intent-to-treat" language without exact criteria is a reviewable deficiency.

## Edge cases / when the rule does NOT apply

Exploratory phase I PK/PD analyses where no confirmatory endpoint exists and no regulatory labeling claim is sought have more flexibility. Adaptive trial designs with pre-specified adaptation rules (per the written adaptive design plan) also permit pre-planned SAP updates at adaptation points — but the adaptation rules themselves must be pre-specified and locked.

## See also

- [`../agents/regulatory-submissions-specialist.md`](../agents/regulatory-submissions-specialist.md) — SAP lock status is a key submission-readiness checkpoint.
- [`./adaptive-trial-design-requires-pre-specified-rules.md`](./adaptive-trial-design-requires-pre-specified-rules.md) — adaptive designs that touch the SAP require pre-specified adaptation rules.

## Provenance

Grounded in ICH E9 Statistical Principles for Clinical Trials and ICH E9(R1) Addendum on Estimands; FDA Guidance for Industry: Adaptive Designs for Clinical Trials (2019); standard regulatory-statistics practice for confirmatory trials.

---

_Last reviewed: 2026-06-05 by `claude`_
