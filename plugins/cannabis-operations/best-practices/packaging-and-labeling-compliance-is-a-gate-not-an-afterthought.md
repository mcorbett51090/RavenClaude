# Packaging and labeling compliance is a production gate, not an afterthought

**Status:** Absolute rule
**Domain:** Cannabis operations / manufacturing / compliance
**Applies to:** `cannabis-operations`

---

## Why this exists

Cannabis packaging and labeling requirements are among the most variable and most frequently revised rules across state regimes — child-resistant closure standards, required label disclosures, health warnings, potency format, serving size, and QR-code or scan requirements all differ by state and change with regulatory updates. Operators who treat packaging as a last step — finalizing labels after production is complete — routinely discover that a new requirement applies, or that a field is wrong, after product is already packaged. The cost is rework (re-labeling or re-packaging the entire run) or destruction (if re-labeling is not permitted for the failure type). Either outcome is magnified under 280E because the rework cost is partially non-deductible.

## How to apply

Build packaging and labeling compliance as an explicit production-planning gate:

```
Packaging compliance gate — [SKU] — [state] — [effective date of label version]

1. Pre-production label audit
   Applicable state rule (cite URL + effective date):  ____
   Required disclosures confirmed present:              Y/N
   Child-resistant closure standard met:               Y/N (standard: ____)
   Potency range within label claim tolerance (±____%): Y/N
   Health warning text matches current state language:  Y/N
   Net weight / volume format correct:                 Y/N
   License number(s) on label:                        Y/N
   Batch/lot ID format matches track-and-trace:        Y/N

2. Pre-release QC check (sample from each production run)
   Sample QC performed by:                            ____
   Date:                                              ____
   Deviations found:                                  Y/N → describe:

3. Label version archived in SOP system:               Y/N
   Version ID:                                        ____
```

Assign label compliance sign-off to a named role before production begins, not before shipment.

**Do:**
- Subscribe to the state cannabis regulator's update feed (email list, RSS, or periodic rule check); labeling rules change without the cadence of a full rulemaking.
- Archive every label version with its effective date, the rule citation it was built from, and the production runs it covers.
- Confirm the potency on the final COA falls within the label's stated tolerance before releasing the batch; an out-of-tolerance potency claim is a mislabeling violation.

**Don't:**
- Finalize labels before receiving the final COA — the label's potency claim must reflect the actual tested product, not the estimated potency.
- Assume a label that passed inspection in one state is valid in another — even multi-state operators must run a fresh label audit per state.
- Skip the pre-production audit on a re-run of an existing SKU; a rule change between runs can invalidate a previously compliant label.

## Edge cases / when the rule does NOT apply

- White-label / co-manufacturing arrangements where the licensed retailer or brand owner is contractually responsible for label compliance — confirm the contract explicitly assigns responsibility before treating this rule as the counterparty's obligation.

## See also

- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — owns state-rule tracking and label audit.
- [`../agents/cannabis-engagement-lead.md`](../agents/cannabis-engagement-lead.md) — frames the packaging-compliance gap in an operations review.
- [`./the-rules-change-at-the-state-line-never-generalize-a-state.md`](./the-rules-change-at-the-state-line-never-generalize-a-state.md) — the foundational rule; labeling is one of its most active areas.

## Provenance

Derived from state cannabis packaging and labeling regulatory requirements and manufacturing quality-gate practices. `[unverified — training knowledge]` — validate against the current version of the applicable state's packaging rules before using in a client deliverable.

---

_Last reviewed: 2026-06-05 by `claude`_
