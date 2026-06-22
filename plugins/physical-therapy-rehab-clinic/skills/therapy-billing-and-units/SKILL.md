---
name: therapy-billing-and-units
description: "Calculate PT/rehab billable units correctly: separate timed (time-based, 15-min) from untimed (service-based) CPT codes, apply the 8-minute rule to total timed units, and place GP/KX/59 modifiers — confirming the payor's rule variant before billing."
---

# Therapy Billing & Units

Get the units right before anything else; the modifier and the claim ride on them.

## Step 1 — timed vs untimed

- **Untimed (service-based)** codes bill **one unit per session** regardless of minutes (e.g. an evaluation, some modalities).
- **Timed (time-based)** codes bill in **15-minute units** under the 8-minute rule.

## Step 2 — the 8-minute rule (timed codes)

- A single timed service needs **≥ 8 minutes** to bill 1 unit.
- Total all timed minutes, then map cumulative minutes to units by the bracket table:

| Total timed minutes | Units `[verify-at-use payor variant]` |
|---|---|
| 8–22 | 1 |
| 23–37 | 2 |
| 38–52 | 3 |
| 53–67 | 4 |
| +15 min | +1 |

- **Mixed timed codes:** total minutes → total units, then allocate units to codes (largest-remainder logic). The **payor variant** (CMS cumulative vs the per-service "rule of eights" some commercials use) decides edge cases — confirm it.

## Step 3 — modifiers

| Modifier | When |
|---|---|
| **GP** | Service under a **PT** plan of care (OT → GO, SLP → GN) |
| **KX** | Above the Medicare **therapy threshold**, attesting documented medical necessity |
| **59 / X{EPSU}** | A **genuinely distinct** service against an NCCI edit — never to force a bypass |

## Verify-at-use

- The **8-minute-rule variant** and **NCCI/modifier edits differ by payor** and change — confirm against the specific payor before billing. The threshold dollar figure is `[ESTIMATE]` until checked — see [`../../knowledge/pt-clinic-reference-2026.md`](../../knowledge/pt-clinic-reference-2026.md).

Traverse the 8-minute-rule tree in [`../../knowledge/pt-clinic-decision-trees.md`](../../knowledge/pt-clinic-decision-trees.md).
