---
scenario_id: 2026-06-05-design-coordination-clash-rework
contributed_at: 2026-06-05
plugin: architecture-aec
product: construction-documents
product_version: "n/a"
scope: likely-general
tags: [coordination, clash, constructability, rework, mep, 50-95-review]
confidence: medium
reviewed: false
---

## Problem

A project reached the field and the same problem kept recurring: ductwork, structure, and ceiling heights collided in the field, generating a wave of RFIs, change orders, and rework — all in areas where the disciplines hadn't been coordinated against each other before the set went out. The firm was treating each clash as an isolated field issue (answer the RFI, move on), missing that they shared a root cause: discipline coordination had happened late and incompletely, and the drawing set looked finished without *being* coordinated.

## Context

- Segment: institutional, multi-discipline (architectural + structural + MEP via subconsultants), design-bid-build.
- Constraint: subconsultant drawings were overlaid for the first time near the end of CDs, so conflicts surfaced after the architectural design had hardened — the most expensive moment to find them. The spec sections and the drawing notes had also drifted in a couple of areas, sending mixed signals to the field.
- The set was "beautiful" — well-rendered, well-organized — which masked that it wasn't *constructable* in the collision zones (§3 #5: coordination beats drawing beauty).

## Attempts

- Tried: read the RFI/change-order pattern as a coordination signal (§3 #3) rather than as isolated field questions. Clustered the RFIs by location and discipline pair and found a small number of collision zones (a few MEP-vs-structure-vs-ceiling conflicts) generated a disproportionate share of the field issues and rework. Outcome: reframed "lots of RFIs" as "a few uncoordinated details," which is fixable.
- Tried: checked spec-to-drawing alignment in the problem areas and found the note/spec drift that was compounding the confusion (§3 anti-pattern: spec sections must match drawing notes). Outcome: a quick wins list to reconcile the documents.
- Tried (the move that worked): instituted structured **discipline-coordination reviews at ~50% and ~95% CDs** — overlay all disciplines, walk the collision-prone zones, reconcile spec-vs-drawing — so conflicts surface while the design is still soft and cheap to fix, not in the field. Owner sign-off captured at the phase gates so the team wasn't drawing ahead of approval (§3 #6).

## Resolution

The recurring field clashes weren't bad luck or a difficult contractor — they were **late, incomplete discipline coordination** showing up where it always shows up: in the field, as RFIs and rework. Moving coordination to scheduled 50%/95% reviews (and reconciling spec-to-drawing) caught the next project's conflicts on paper. The RFI/change-order load on the following job dropped because the document quality — coordination, not rendering — improved (§3 #5).

**Action for the next consultant hitting this pattern:** when field clashes and rework recur, **cluster the RFIs/COs by location + discipline pair before treating them as isolated** — a few collision zones usually drive most of the load (§3 #3). The durable fix is *scheduled* discipline-coordination reviews at ~50% and ~95% CDs (overlay every discipline, walk the conflict-prone zones, reconcile spec-vs-drawing) so conflicts surface on paper while the design is soft, plus owner sign-off at each phase gate (§3 #5, #6). Constructability and coordination are the document's real quality, not the rendering. See the "CA Deficiency" tree and the coordination discipline in [`../knowledge/aec-decision-trees.md`](../knowledge/aec-decision-trees.md) and the [`../skills/coordinate-the-set/SKILL.md`](../skills/coordinate-the-set/SKILL.md) playbook.

**Sources (retrieved 2026-06-05):**
- Layer App — *The Complete Guide to RFIs in Construction Administration* (coordination-driven RFIs, cost per RFI): https://layer.team/blog/the-complete-guide-to-rfis-in-construction-administration
- SubmittalLink — *RFI Best Practices* (root-cause classification of RFIs): https://www.submittallink.com/post/rfi-best-practices

Figures are illustrative for this scenario; coordination-review cadence and the RFI/rework reduction are firm- and project-dependent — validate against the project's actual data before a deliverable (§3 #8). Code/life-safety determinations in any collision zone route to the engineer/architect of record (§3 #7).
