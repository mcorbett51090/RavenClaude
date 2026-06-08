---
description: "Document, price, and package a construction change order: identify the change-order trigger, price direct cost (labor/material/equipment/sub) with contract-specified markup, quantify schedule impact, assemble the CO package, and update the CO log and SOV."
argument-hint: "[change description and trigger, e.g. 'Owner added 500 SF of flooring scope per field direction email dated June 5 — need pricing and time impact']"
---

You are running `/construction-general-contractor:manage-change-order`. Use the
`submittal-rfi-coordinator` discipline and the `submittals-rfis-change-orders` skill.

## Steps

1. **Identify the change-order trigger.** Determine the source: owner-directed scope change,
   RFI response that changed design, differing site condition, design error/omission, or
   regulatory change. Document the written record that authorizes pricing (owner letter, RFI
   response, architect's SI, meeting minutes).

2. **Verify documentation before pricing.** Confirm there is a written directive before
   work starts. If the work has already begun without written authorization, flag this as
   a risk and draft a retroactive PCO with the direction as backup.

3. **Price the change.** Coordinate with `estimating-and-takeoff-analyst`:
   - Direct labor: hours × loaded rate (source and date required)
   - Material: quote or unit-price book (source and date required)
   - Equipment: owned or rental quote
   - Sub scope: reviewed quote + GC markup per contract terms
   - GC OH&P: apply contract-specified markup rates explicitly (state markup % and basis)
   - Bond if contractually required on CO amounts

4. **Quantify schedule impact.** Coordinate with `scheduling-engineer`: does this change
   affect critical-path activities? State the number of excusable/compensable days.
   If no schedule impact, document that explicitly.

5. **Assemble the CO package.** Cover letter (CO number, description, contract value before/
   after, time impact) + cost breakdown + supporting documentation + schedule impact narrative.

6. **Update the CO log and SOV.** Once approved, add the CO to the project SOV as a new line
   item (or roll into an existing line). Update the CO log with status (approved / pending /
   disputed). Flag approved-but-unbilled COs to `gc-project-lead` for inclusion in the next
   pay application.

7. **Emit the Structured Output block** with: CO amount, time impact (days), CO log balance
   (total approved / pending), SOV impact, and handoffs (gc-project-lead for billing inclusion;
   scheduling-engineer for schedule update).
