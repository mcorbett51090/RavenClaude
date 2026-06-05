# Discipline Coordination Review at 50% and 95% CDs

**Status:** Absolute rule
**Domain:** Architecture/AEC
**Applies to:** `architecture-aec`

---

## Why this exists

Coordination conflicts between architecture, structural, MEP, and civil discovered in the field cost 5–15x more to resolve than conflicts caught in the document review. A single missed beam pocket, a mechanical duct that runs through a structural member, or a plumbing riser in a required egress path generates an RFI, a change order, a schedule impact, and a contractor claim — all traceable to a document set that wasn't coordinated before issue. Two formal coordination reviews — at 50% and 95% CDs — catch the conflicts while the drawings are still editable.

## How to apply

Conduct two structured inter-discipline coordination reviews during the CD phase:

```
CD Coordination Review Checklist (50% and 95%)
────────────────────────────────────────────────
Project:          ________________
Review stage:     [ ] 50% CDs   [ ] 95% CDs
Disciplines in review:  [ ] Arch  [ ] Struct  [ ] MEP-M  [ ] MEP-E  [ ] MEP-P  [ ] Civil  [ ] Spec

Coordination checks:
  [ ] Structural grid and arch plan agreement (column locations, beam depths)
  [ ] MEP routing vs. structural (no ducts/pipes through beams/joists without approval)
  [ ] Ceiling heights vs. MEP routing space (corridors, mechanical rooms)
  [ ] Plumbing verticals vs. egress and partition layout
  [ ] Electrical panels / switchgear vs. clearance requirements
  [ ] Civil grading vs. foundation design at grade transitions
  [ ] Spec sections matched to drawing notes and details

Conflicts identified:
  | # | Drawing ref | Conflict description | Assigned to | Resolve by |
  |---|-------------|---------------------|-------------|------------|

Conflict count:  ___   Resolved by issue date: ___
```

**Do:**
- Hold the 50% review as an in-person or live-share session — asynchronous mark-up exchange at 50% misses inter-discipline cascades.
- Require each discipline lead to sign off that their portion of the coordination checklist was reviewed before the 95% issue.
- Track conflict counts from the 50% to the 95% review — an increasing count is a document quality signal.

**Don't:**
- Substitute a single pre-bid review for the two-stage process; 95%-only reviews are too late to prevent rework on documents already coordinated to the 50% state.
- Count a "will coordinate in the field" note as a coordination resolution — it is a deferred conflict and a potential change order.
- Skip the review on fast-track projects; compress the schedule, not the coordination gate.

## Edge cases / when the rule does NOT apply

Simple single-discipline renovations (interior-only, no structural or MEP work) may not require an inter-discipline coordination review, but should still run a 95% spec-to-drawing consistency check.

## See also

- [`../agents/construction-documents-specialist.md`](../agents/construction-documents-specialist.md) — owns document coordination and the CD review process.
- [`./constructability-and-coordination-beat-drawing-beauty.md`](./constructability-and-coordination-beat-drawing-beauty.md) — the governing rule on coordination quality.

## Provenance

Codifies CLAUDE.md §3 #5 (constructability and coordination beat drawing beauty) with a specific two-gate review instrument. The 50%/95% review cadence is standard AEC QC practice as described in AIA, NIBS, and BIM coordination standards [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
