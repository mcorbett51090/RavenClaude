---
description: "Run a compliance-gated F&I review: PVR decomposition, product penetration vs benchmark, menu-process assessment, compliance gate checklist (no payment packing, OFAC, Red Flags, RISC accuracy), lender mix, and a ranked PVR improvement plan."
argument-hint: "[context, e.g. 'F&I PVR $1,050, VSC 28%, GAP 22%, 180 units retailed, menu-selling not documented, one primary lender']"
---

You are running `/automotive-dealership:review-fni-compliance`. Use both the `fni-advisor`
discipline (performance) and the `dealership-compliance-advisor` discipline (compliance gate),
plus the `fni-and-compliance` skill.

## Steps

1. **Gather F&I inputs.** Request (or read from context): total F&I gross, units retailed,
   finance reserve, product gross by type (VSC, GAP, maintenance, tire/wheel, appearance),
   chargebacks, lender mix. If inputs are partial, state assumptions.

2. **Decompose PVR.** Calculate total PVR, reserve PVR, and product PVR. Compare to
   benchmark (mark [verify-at-use]).

3. **Run compliance gate FIRST.** Check all items in the compliance checklist from
   `skills/fni-and-compliance/SKILL.md` step 3. **If any payment-packing check fails,
   STOP and report the violation before any PVR recommendation.** Route to
   `dealership-compliance-advisor` for remediation.

4. **Calculate product penetration rates.** For each product: penetration % and average
   front. Compare to benchmark ranges (mark [verify-at-use]). Rank products by
   `(target penetration − actual) × average front × monthly units` = PVR opportunity.

5. **Assess menu process.** Score each element (presentation rate, simultaneous full
   disclosure, payment structure, documentation) on a 3-point scale.

6. **Analyze lender mix.** Check concentration risk, reserve opportunity by tier,
   approval rate vs stip patterns, CIT aging.

7. **Output improvement plan.** Compliance gate result (pass/fail per item), product
   penetration gap table, menu process score, lender mix summary, ranked PVR
   improvement actions with monthly dollar estimates.
   Emit the Structured Output JSON block with handoffs
   (`dealership-compliance-advisor` for any compliance gap, `inventory-and-desking-analyst`
   for deal-structure context, `dealership-ops-lead` for F&I contribution to P&L).
