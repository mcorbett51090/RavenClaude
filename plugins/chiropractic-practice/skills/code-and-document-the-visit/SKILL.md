---
name: code-and-document-the-visit
description: "Pick the CMT/E&M code for a chiropractic visit and structure the medical-necessity note: CMT by number of spinal regions treated, an E&M only when separately identifiable (with the correct modifier), and a PART-exam-based note (region + functional goal + progress) that supports the code and survives an audit. Reach for it per visit / when coding is unclear. Used by `chiro-billing-compliance-specialist` (primary). Not a coding certification — verify payer policy."
---

# Skill: code-and-document-the-visit

> **Invoked by:** `chiro-billing-compliance-specialist` (primary).
>
> **When to invoke:** coding a visit, or when CMT vs E&M / a modifier / necessity documentation is unclear.
>
> **Output:** a documentation-supported code path + a medical-necessity note structure. Payer-specific rules carry a retrieval date + `[verify-at-use]`.

## Procedure

1. **Place the visit first.** Traverse [`../../knowledge/billing-and-medical-necessity-decision-tree.md`](../../knowledge/billing-and-medical-necessity-decision-tree.md): acute/new complaint vs scheduled re-exam vs plateau/maintenance. Placement drives everything downstream.
2. **Count the spinal regions treated for the CMT code.** Spinal CMT is coded by regions (the 98940 / 98941 / 98942 family — 1-2 / 3-4 / 5 regions `[verify-at-use]`). The note must name the regions adjusted; code to what was documented, never up to a higher region count.
3. **Add an E&M only if it's separately identifiable.** A distinct, significant E&M service beyond the pre-adjustment assessment may be codeable with the appropriate modifier `[verify-at-use]` — most maintenance/established visits are not. Don't reflexively stack an E&M on every visit.
4. **Document medical necessity on the PART backbone.** Pain/tenderness, Asymmetry, Range-of-motion abnormality, Tissue/tone change — document the findings (commonly ≥2 `[verify-at-use]`) tied to the region coded, plus the functional goal and the progress since last visit. That triad — findings + goal + progress — is the necessity.
5. **Check the plateau.** If the patient has stopped improving toward the functional goal, care is likely supportive/maintenance → coverage changes → ABN + transition to cash (with the practice lead).
6. **Verify the payer's own policy.** Region definitions, modifier rules, documentation frequency, and covered-service definitions are payer- and state-specific and change — cite [`../../knowledge/chiro-payer-and-coding-reference-2026.md`](../../knowledge/chiro-payer-and-coding-reference-2026.md) with a date and flag anything needing a certified coder.

## Worked example

> Established patient, 3 regions adjusted (cervical, thoracic, lumbar), improving.

- Placement → active re-exam-window visit, still improving.
- CMT → 3 regions → 98941 `[verify-at-use]`; no separate E&M (routine follow-up).
- Necessity → PART: cervical tenderness + reduced ROM, lumbar asymmetry; goal: restore ROM; progress: +15° cervical rotation since last visit.
- Plateau check → still improving → active care continues; no ABN yet.

## Guardrails

- **Never up-code the region count or add an unsupported E&M** — the audit that closes practices.
- **If it isn't documented, it wasn't done** — the note is the claim.
- **Region/modifier/necessity rules are payer-specific** — verify, don't recall; certified-coder questions route out.
