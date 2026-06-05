# Protect PHI at every step — minimum-necessary, HIPAA-safe boundary, never in an example

**Status:** Absolute rule
**Domain:** Privacy / HIPAA
**Applies to:** `hospice-referral-sales`

---

## Why this exists

A hospice liaison handles real protected health information — diagnoses, prognoses, names, facilities — constantly. HIPAA governs every list, message, CRM field, and deliverable. A patient name in an email to the wrong recipient, a diagnosis-plus-facility combination in a shared note, or a real case used as an "example" is a reportable breach. The discipline is simple and absolute: minimum-necessary, a HIPAA-safe boundary, and nothing patient-identifying in anything this plugin produces.

## How to apply

**Do:**
- Use only the minimum patient data necessary for the task, inside approved systems.
- De-identify before any screen, example, or scenario (no name, DOB, MRN, or identifying facility+diagnosis combination).
- Use counts and rates, not patient lists, in any funnel or partner read.
- Route anything beyond minimum-necessary framing to the privacy officer.

**Don't:**
- Put patient-identifying data in a CRM note shared out, an email, an example, or a scenario.
- Pass real patient data into the calculator or a deliverable.
- Assume a referral source sending you a chart authorizes you to forward or store it freely.

## Edge cases / when the rule does NOT apply

Properly authorized clinical data exchange inside the HIPAA-safe boundary for treatment/coordination is permitted — the rule governs *identifying data leaving the boundary* and *PHI in this plugin's deliverables*. The plugin's own outputs are always de-identified.

## See also
- [`../agents/hospice-sales-compliance-advisor.md`](../agents/hospice-sales-compliance-advisor.md)
- [`../knowledge/hospice-sales-compliance-reference.md`](../knowledge/hospice-sales-compliance-reference.md)

## Provenance

Codifies CLAUDE.md §3 #7 and §6 (the mandatory Patient-data / PHI note). Grounded in HIPAA (45 CFR 160/164).

---

_Last reviewed: 2026-06-05 by `claude`_
