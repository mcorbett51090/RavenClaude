# Waste disposal is a compliance event with a real cost — track and account for it

**Status:** Absolute rule
**Domain:** Cannabis operations / compliance / cost accounting
**Applies to:** `cannabis-operations`

---

## Why this exists

Cannabis waste (unusable plant material, contaminated product, expired inventory, failed-test batches) is tightly regulated in every state: it must be rendered unusable and unrecognizable before disposal, the destruction must be witnessed (by a regulator or internal witness depending on state), and the event must be logged in the track-and-trace system before the physical disposal occurs. Operators who dispose of waste informally — without a logged destruction event — create a phantom discrepancy between the system record (product still exists) and physical reality (product is gone). That discrepancy is, by definition, a seed-to-sale compliance violation. Separately, waste-disposal cost is a real production cost that belongs in the batch cost record, not in a general overhead line.

## How to apply

Execute every waste event through this procedure:

```
Waste disposal log — [date] — [entity] — [state]

Track-and-trace package IDs to be destroyed:   ____
Total weight (gross):                          ____
Reason for disposal:
  [ ] Expired / unsaleable
  [ ] Failed mandatory lab test — analyte: ____
  [ ] Damaged / contaminated
  [ ] Trim / plant waste (ongoing)
  [ ] Other: ____

Rendering method (as required by state):       ____
Witness name / title / license #:              ____
Date/time of physical destruction:             ____
Track-and-trace destruction logged (ID):       ____
Disposal cost:                                 $____
```

Log the destruction event in the track-and-trace system before the physical disposal begins. Archive this log with the batch cost record.

**Do:**
- Confirm the required rendering method with the state's current rules — methods vary (grinding + mixing with soil, incineration, composting) and are state-specific.
- Record the witness credential (regulator license number or internal role) — some states require a regulatory witness for destruction of failed-test batches above a threshold quantity.
- Charge waste-disposal cost to the batch cost record for the originating batch, not to a general overhead line; it is a direct production cost.

**Don't:**
- Log the destruction event after the physical disposal has occurred — the order (log first, destroy second) is a regulatory requirement in every major state system.
- Dispose of failed-test product as agricultural or municipal waste without first rendering it unusable per the state's method — this is a separate violation from the track-and-trace logging failure.
- Omit trim weight from the waste log because it is "just plant material" — trim and other agricultural waste is within the scope of the track-and-trace record requirement in most states.

## Edge cases / when the rule does NOT apply

- De minimis quantities of unusable material (dust, residue) that cannot practically be weighed may be handled under a state's minor-waste exemption — confirm the threshold and exemption procedure; do not assume it applies.
- Waste generated during an active regulatory inspection may have a modified procedure — follow the inspector's instructions and document the deviation.

## See also

- [`../agents/seed-to-sale-compliance-specialist.md`](../agents/seed-to-sale-compliance-specialist.md) — owns the track-and-trace logging and witness protocol.
- [`../agents/cannabis-finance-analyst.md`](../agents/cannabis-finance-analyst.md) — accounts for waste disposal cost in the production cost model.
- [`./seed-to-sale-traceability-is-the-license-reconcile-it-daily.md`](./seed-to-sale-traceability-is-the-license-reconcile-it-daily.md) — a logged destruction event is part of daily reconciliation.

## Provenance

Derived from state cannabis waste-disposal regulations, track-and-trace destruction logging requirements, and cannabis manufacturing cost-accounting practice. `[unverified — training knowledge]` — validate the rendering method and witness requirements against the current applicable state rules.

---

_Last reviewed: 2026-06-05 by `claude`_
