---
description: "Build or apply a consistent, documented, fair-housing-aware residential applicant-screening standard — applied identically to every applicant, with protected-class and legal questions flagged to counsel."
argument-hint: "[the property + current criteria (if any) + the applicant/situation]"
---

You are running `/property-management-residential:screen-applicant`. Use `leasing-and-tenant-ops` + the `leasing-and-screening` skill.

## Steps
1. If no written standard exists, draft one: income multiple, credit history, prior eviction/judgment history, rental references, occupancy standard — the SAME criteria for every applicant. Document it before applying it.
2. FLAG every protected-class-adjacent or legally-constrained element (criminal-history use, source-of-income, accommodation requests, ad language) and route it to counsel — do not adjudicate.
3. If applying the standard to an applicant, record which criterion each decision (approve / conditional / deny) rests on; never a per-applicant ad-hoc judgment.
4. Keep tenant PII (SSNs, screening reports, bank data) out of the output — reference it, never quote it.
5. Emit the screening standard / decision + the Structured Output block (with `Fair-housing / habitability flags:` and `Handoff:` — legal calls to counsel, books to finance).
