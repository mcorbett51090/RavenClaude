---
scenario_id: 2026-06-08-margin-looked-fine-until-DIR
contributed_at: 2026-06-08
plugin: pharmacy-operations
product: margin
product_version: "n/a"
scope: likely-general
tags: [margin, dir-fees, reimbursement, specialty]
confidence: medium
reviewed: false
---

## Problem

An operations leader read sticker reimbursement and concluded margin was healthy. The risk: the sticker overstates margin because DIR/clawback fees hit retroactively — a script profitable at fill can go negative after DIR, and the book's real margin only shows once DIR is netted (§3 #3).

## Context

- Setting: retail-chain pharmacy with growing specialty volume.
- Constraint: real margin = reimbursement − acquisition cost − DIR fee; specialty carries distinct economics (§3 #3 #6).
- The leader reasoned from the at-fill reimbursement.

## Attempts

- Tried: **recomputed margin net of DIR** (`pharmacy_operations_calc.py margin`). Outcome: several drug classes went negative once DIR was applied — invisible at the sticker.
- Tried: **separated specialty/340B/refrigerated** and priced them distinctly (§3 #6). Outcome: the specialty economics were materially different from standard retail fills.
- Tried: **flagged the negative-margin classes** for contract renegotiation or mix change (§3 #3). Outcome: a concrete target list, not a blanket 'cut costs.'

## Resolution

The response was a **real-margin read net of DIR with the negative classes flagged and specialty handled distinctly** — not a sticker-based comfort. The output was the per-script real margin, the negative-class list, and the specialty breakout, with no patient PHI in the deliverable.

**Action for the next consultant hitting this pattern:** **always net DIR before calling a book profitable, and price specialty distinctly.** The sticker hides retroactive clawbacks; read real margin and flag the negative classes. See Tree 2 and the `margin` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
