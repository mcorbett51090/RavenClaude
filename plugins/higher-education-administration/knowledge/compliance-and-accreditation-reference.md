# Compliance & accreditation — reference

Deep reference for the `academic-operations-and-compliance-coordinator` and
`institutional-research-and-analytics-analyst`. Companion to
[`higher-ed-decision-trees.md`](higher-ed-decision-trees.md).

> **Compliance note:** FERPA, Title IV, IPEDS, and accreditation rules change and vary by
> jurisdiction, accreditor, and institution. This is operational orientation, not legal advice — flag
> specifics for verification against current regulation and institutional counsel.

---

## FERPA as a design constraint

The decision procedure for any student-data flow or dashboard:

```
Is the data an "education record" (personally identifiable, maintained by the institution)?
├─ No (de-identified / aggregate) → lower constraint; verify aggregation thresholds
└─ Yes → who is accessing it?
     ├─ Legitimate educational interest → permitted; scope access to that interest
     └─ No legitimate educational interest → not permitted without consent/exception
```

Design access **before** building. Directory information, disclosure exceptions, and parental-access
rules carry their own conditions — flag for counsel.

## IPEDS / mandated reporting

- Cohorts (entering full-time first-time) and completion windows (150% time) have precise definitions
  that must be reproduced exactly for comparability.
- The canonical data definitions (census date, headcount vs. FTE) underpin every mandated figure;
  pin them once, institution-wide.
- Treat any specific IPEDS definition as `[verify against current IPEDS reporting definitions]`.

## Accreditation — continuous, not event-driven

- Map each standard to the artifact(s) that demonstrate it; a standard with no artifact is a gap.
- The assessment loop must **close**: define outcomes → measure → analyze → **act** → re-measure. The
  most common finding is assessment that measures but never acts.
- Maintain the evidence map year-round with owners; a review becomes assembly, not archaeology.

## Title IV

Federal financial-aid packaging, disclosure, return-of-funds, and threshold rules change frequently
and carry real compliance risk. State the mechanic, date it, and flag it for verification against
current federal regulation and financial-aid counsel. Never assert a Title IV rule from memory in a
durable deliverable.

## The standing reminder

Per the core Claim-Grounding protocol, any regulation-, aid-, or accreditation-specific claim is dated
and verified before it gates a decision. This plugin is decision-support, not compliance or legal
advice.
