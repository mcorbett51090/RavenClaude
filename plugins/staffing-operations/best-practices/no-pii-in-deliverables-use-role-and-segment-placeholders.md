# No PII in Deliverables — Use Role and Segment Placeholders

**Status:** Absolute rule
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

Staffing data is dense with personally identifiable information: clinician names, license numbers, social security numbers, dates of birth, credential files, and in school-based work, student IEP data that carries FERPA and IDEA protections. A consultant's deliverable — a scorecard, a funnel analysis, a benchmark report — does not need any of this information to be actionable. Including PII in a deliverable creates an unnecessary data-handling obligation, a breach risk, and in regulated contexts a potential HIPAA or FERPA violation. The rule is absolute: role and segment placeholders replace all identifying information.

## How to apply

Apply the following substitution table to every deliverable before it leaves the consultant's possession:

| Raw data field | Deliverable placeholder |
|---|---|
| Clinician name | `<travel RN>`, `<SLP>`, `<BCBA>`, `<school nurse>` |
| License number | omit entirely |
| Date of birth / SSN | omit entirely |
| Client / facility name | `<200-bed acute facility>`, `<suburban K-8 district>`, `<urban multi-site district>` |
| Recruiter name | `<Recruiter A>`, `<Recruiter B>` (sequential labels within the report) |
| Client employer of record name | `<MSP client>`, `<direct-hire district>` |
| Student / patient name | omit entirely — never included |
| IEP service details | aggregate only: `<15 SLP service hours ÷ 3 students>` |

**Do:**
- Apply the substitution table at the analysis stage, not at the final formatting stage — do not work with raw PII-identified data longer than necessary.
- When using named examples for illustration (e.g., "Recruiter A placed 12 assignments in Q1"), use the sequential label consistently throughout the deliverable.
- Confirm with the engagement lead whether the client has a named data-sharing agreement that permits specific facility or district names in deliverables.

**Don't:**
- Include license numbers, SSNs, or DOBs in any deliverable under any circumstances — they serve no analytical purpose.
- Use initials as a PII substitute — "J.S." is not anonymous when combined with role and location.
- Share de-identified aggregated data that has fewer than 5 individuals in a cell — re-identification risk is material at small n.

## Edge cases / when the rule does NOT apply

Internal performance dashboards used only within the staffing firm's own operations team, with appropriate access controls, may reference recruiter names for accountability tracking. Deliverables leaving the firm to a consultant, a board, or a third-party client apply the substitution rule without exception.

## See also

- [`../agents/staffing-engagement-lead.md`](../agents/staffing-engagement-lead.md) — owns engagement-level data-handling decisions and any data-sharing agreements.
- [`../agents/healthcare-staffing-specialist.md`](../agents/healthcare-staffing-specialist.md) — owns the HIPAA / credential data protocol for healthcare-segment work.

## Provenance

Codifies CLAUDE.md §3 #10 (no candidate or client PII in deliverables). The role-and-segment placeholder approach is the operational implementation of the de-identification principle under HIPAA Safe Harbor and FERPA aggregation standards [unverified — confirm with legal counsel for specific regulatory requirements].

---

_Last reviewed: 2026-06-05 by `claude`_
