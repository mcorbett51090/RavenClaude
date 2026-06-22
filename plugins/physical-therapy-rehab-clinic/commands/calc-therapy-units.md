---
description: "Calculate PT/rehab billable units under the 8-minute rule from timed/untimed minutes, then name the GP/KX/59 modifiers — flagging the payor-variant items to verify before billing."
argument-hint: "[timed/untimed minutes + codes + payor, e.g. 'ther-ex 22m, manual 10m, eval; Medicare']"
---

You are running `/physical-therapy-rehab-clinic:calc-therapy-units`. Use `billing-and-revenue`.

> Advisory only — not billing/coding advice. The 8-minute-rule variant, modifier edits, and threshold figure are `[verify-at-use]`. No patient PII.

## Steps
1. Separate **timed** from **untimed** codes (untimed = 1 unit/session).
2. Total timed minutes; require ≥8 min for the first unit; map cumulative minutes to units (8–22=1, 23–37=2, 38–52=3, 53–67=4, +15=+1). Allocate units across mixed timed codes by largest remaining minutes.
3. Name the modifiers: GP/GO/GN by discipline, KX if above threshold, 59 only if genuinely distinct.
4. **Flag the payor variant** (CMS cumulative vs per-service eights) and the threshold figure `[ESTIMATE]` as verify-at-use.
5. Traverse the 8-minute-rule tree in [`../knowledge/pt-clinic-decision-trees.md`](../knowledge/pt-clinic-decision-trees.md). Emit the Structured Output block.
