---
scenario_id: 2026-06-08-capa-that-was-just-scrap
contributed_at: 2026-06-08
plugin: manufacturing-operations
product: capa
product_version: "unknown"
scope: likely-general
tags: [capa, ncr, root-cause, preventive-action, spc, control-plan]
confidence: high
reviewed: false
---

## Problem

A molded-part line had the same dimensional defect resurface every few weeks for over a year. Each time, the team raised a nonconformance, sorted and scrapped the bad parts, closed the NCR, and moved on. The quality records showed dozens of "closed" NCRs for what was visibly the same failure — containment was excellent and the cause was never touched. Scrap cost was climbing and a key customer had started asking for a corrective-action response.

## Constraints context

- The control chart on the critical dimension had its limits set to the print's spec limits, not derived from the process — so operators adjusted the machine on nearly every part that drifted toward a spec edge (textbook tampering).
- "CAPA" in their system was a single free-text field that most people filled with the containment ("sorted and scrapped lot 4471").
- The real driver turned out to be a temperature-dependent shift correlated with a specific raw-material lot supplier change — invisible until the chart was read correctly.

## Attempts

- Tried: tightening final inspection to catch more of the defect at the dock. Failed — it caught more scrap but the defect rate didn't fall; inspection detects, it doesn't prevent, and it was the latest, leakiest control.
- Tried: re-deriving control limits from the process (not the spec) and stopping the per-part adjustments. This removed the tampering variation and, crucially, made the special-cause signal legible — the shift now stood out against stable process limits.
- Tried: a structured CAPA that separated corrective (sort this lot) from preventive (qualify incoming material temperature/lot, add the parameter to the control plan, add an in-process source check). This worked.

## Resolution

With process-derived control limits, the recurring defect showed as a clear special-cause signal tied to the material-lot change. The preventive action — an incoming-material control plus a source-detection check baked into the control plan — moved quality upstream of final inspection. The defect stopped recurring, scrap dropped, and the customer's corrective-action request was closed with a real root cause rather than another "sorted and scrapped."

## Lesson

Containment is not a CAPA — an NCR closed by scrapping the part with no root cause and no preventive action is scheduled to recur. Set control limits from the process, not the spec (or you tamper and hide the signal), separate corrective from preventive action, and push the fix upstream: prevention beats detection beats scrap.
