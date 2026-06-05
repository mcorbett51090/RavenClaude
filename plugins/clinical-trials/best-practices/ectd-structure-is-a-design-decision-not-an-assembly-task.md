# eCTD Structure Is a Design Decision, Not an Assembly Task

**Status:** Absolute rule
**Domain:** Regulatory submissions / eCTD
**Applies to:** `clinical-trials`

---

## Why this exists

eCTD (electronic Common Technical Document) structure decisions — module hierarchy, document granularity, leaf-level naming, and hyperlink architecture — are nearly impossible to undo once a submission series opens with a regulatory authority. A poorly structured initial submission forces leaf replacements across all subsequent sequences and creates reviewer confusion that generates information requests. The cost of a bad structure compounds with every amendment and supplement filed over the trial's lifetime.

## How to apply

Treat the eCTD backbone as a binding architecture document. Before any sequence is lodged, agree the document-level granularity (one protocol per leaf vs. consolidated), the backbone namespace, and the cross-module hyperlink map with the regulatory lead.

```
eCTD design checklist (pre-first-sequence):
[ ] Module 5 study report leaf plan matches each study's reporting status
[ ] Protocol and amendments: single leaf with replace operations or separate leaves per version?
[ ] ISS/ISE scope defined — single integrated or rolling submission?
[ ] STF (Study Tagging File) attributes reviewed for each reportable study
[ ] Hyperlinks from 2.5/2.7 summaries to Module 5 source documents verified
[ ] Validation criteria (FDA/EMA) run against the test backbone before lodging
```

**Do:**
- Fix the leaf naming convention before sequence 0000 and enforce it for the lifetime of the dossier.
- Run the eCTD validator (FDA: ECTD Validation Criteria; EMA: NeeS/eCTD spec) against a test backbone before submitting any real sequence.
- Document the structure decisions in a dossier-level SOP so future CMC or safety updates follow the same architecture.

**Don't:**
- Defer structure decisions to the assembly vendor — the sponsor owns the backbone.
- Use free-text leaf titles that don't match the controlled vocabulary in the regional eCTD specifications.
- Split a single protocol across multiple leaves when replace operations would serve the same purpose.

## Edge cases / when the rule does NOT apply

For low-volume, single-sequence submissions (e.g., an IND initial submission with one study), structure risk is lower — but the convention still applies because every IND that advances will become a multi-sequence dossier.

## See also

- [`../agents/regulatory-submissions-specialist.md`](../agents/regulatory-submissions-specialist.md) — owns eCTD structure, validation, and submission-readiness assessment.
- [`./the-submission-is-built-throughout-not-at-the-end.md`](./the-submission-is-built-throughout-not-at-the-end.md) — the upstream principle this rule operationalizes.

## Provenance

Codifies the regulatory-submissions-specialist's operating principle that the submission is built throughout, not at the end (CLAUDE.md §3 #7), grounded in FDA eCTD Technical Conformance Guide and EMA eCTD Specification v4.x; standard CRO regulatory-operations practice.

---

_Last reviewed: 2026-06-05 by `claude`_
