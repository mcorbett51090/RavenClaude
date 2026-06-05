# Spec Sections Must Match Drawing Notes — Not Diverge

**Status:** Absolute rule
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

A contractor who finds a conflict between a specification requirement and a drawing note will price the more expensive interpretation or ask for an RFI — and both outcomes cost the owner money. More seriously, if the spec specifies a material or product that contradicts the drawing detail, a claim can result from a contractor who built to the drawing rather than the spec (or vice versa). The contract documents must speak with one voice; the spec is not a separate document written in isolation from the drawings.

## How to apply

Run a spec-to-drawing consistency check as part of every CD coordination review:

```
Spec-Drawing Consistency Check
─────────────────────────────────
CSI Division:  ________________
Reviewer:      ________________
Date:          ________________

For each spec section in scope:
  [ ] All materials/products specified match drawing keynotes and schedules
  [ ] Section references in drawing notes (e.g., "See Spec 07 9200") exist in the spec
  [ ] Product substitution language in spec is consistent with drawing "or approved equal" notes
  [ ] Execution requirements in spec are achievable per the detail shown
  [ ] Warranty/performance requirements don't conflict with drawing-level detail intent

Conflicts identified:
  | Spec section | Drawing sheet/note | Conflict description | Resolution |
  |-------------|-------------------|---------------------|------------|
```

**Do:**
- Check spec-to-drawing consistency at both 50% and 95% CDs — spec sections written at 50% are often outdated by drawing changes at 95%.
- When a conflict exists, the spec governs over the drawing under most standard construction contracts (AIA A201 §1.2.1), but the contractor may price whichever is more favorable; confirm the priority language in the project's general conditions.
- Require the spec writer to participate in the 95% CD coordination review — spec sections written by a consultant who has not seen the current drawings are a coordination risk.

**Don't:**
- Use generic master-spec sections without verifying they match the project's specific products and details — a spec section pulled from a prior project and not updated is a conflict factory.
- Write "per manufacturer's recommendations" in both the spec and the drawing detail without verifying the recommendations are the same — they sometimes conflict between products.
- Let drawing notes reference a spec section that doesn't exist in the project manual.

## Edge cases / when the rule does NOT apply

Performance specifications (where the spec defines an outcome and the contractor selects the means and materials) intentionally give the contractor more latitude; the consistency check focuses on outcome metrics and testing requirements rather than material-by-material matching.

## See also

- [`../agents/construction-documents-specialist.md`](../agents/construction-documents-specialist.md) — owns spec writing and coordination.
- [`./discipline-coordination-review-at-50-and-95-percent-cds.md`](./discipline-coordination-review-at-50-and-95-percent-cds.md) — the companion rule on the two-stage CD coordination review where this check runs.

## Provenance

Codifies CLAUDE.md §3 #5 (constructability and coordination beat drawing beauty) applied to spec-drawing consistency. The spec-governs-over-drawings priority rule is standard in AIA A201 §1.2.1 and is a common source of contractor claims when the two documents conflict [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
