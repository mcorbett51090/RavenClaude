# Shrink has a root cause — find it

**Status:** Pattern
**Domain:** Loss prevention, inventory management
**Applies to:** `retail-store-operations`

---

## Why this exists

A blended shrink rate of 2% is not a fact — it is a symptom. The response to 2% shrink driven
by receiving errors is process redesign. The response to 2% shrink driven by organized retail
crime is physical deterrence and law-enforcement coordination. The response to 2% shrink driven
by employee theft is exception-based reporting and internal investigation. These are completely
different programs. A shrink-reduction initiative that starts with "buy EAS tags" or "add
cameras" without a root-cause decomposition will:

1. Spend capital on the wrong intervention.
2. Fail to reduce shrink — because the cameras don't fix receiving errors.
3. Generate compliance risk if internal-theft indicators are acted on without investigation.

The three buckets are: **Operational** (receiving errors, damage, paperwork, process gaps),
**Internal** (employee theft, fraud, sweethearting), **External** (customer shoplifting, ORC).
A fourth bucket — **Unknown / Unresolved variance** — is a measurement failure, not a category.

## How to apply

**Do:**

1. Before recommending any shrink-reduction program, require a decomposition into the
   three buckets. If data to decompose is unavailable, the first step is an audit to produce it.
2. Match interventions to root causes:
   - Operational: receiving audits, damage documentation, inter-store transfer accuracy,
     process redesign.
   - Internal: exception-based POS reporting, dual-control on cash, investigation protocol.
   - External: EAS tagging of hot items, display placement, store layout, ORC coordination.
3. Treat exception-based reporting as a triage tool — it produces patterns to investigate,
   not verdicts. Human investigation precedes any disciplinary action.
4. Audit before assuming. Operational shrink is the most common and most under-diagnosed
   category; most retailers focus on external theft and miss receiving and process errors.

**Don't:**

- Recommend cameras, EAS, or physical-security investment before a root-cause decomposition.
- Act on exception-based reporting patterns without an investigation step.
- Accept a blended shrink % as a KPI target without decomposing it — the target for each bucket
  differs.
- Treat "shrink unknown" as acceptable — unknown variance is an accuracy and measurement problem.

## Edge cases / when the rule does NOT apply

- **Emergency response:** if an active ORC event or an in-progress theft is identified, physical
  safety and immediate response take priority over root-cause analysis. Analysis follows the event.
- **New store / first inventory:** an initial physical inventory establishes the baseline and will
  have high unknown variance. This is a measurement baseline, not a signal to triage.

## See also

- [`./gmroi-not-just-gross-margin.md`](./gmroi-not-just-gross-margin.md)
- [`./omnichannel-inventory-is-one-pool.md`](./omnichannel-inventory-is-one-pool.md)
- [`../agents/loss-prevention-advisor.md`](../agents/loss-prevention-advisor.md)
- [`../knowledge/retail-store-operations-decision-trees.md`](../knowledge/retail-store-operations-decision-trees.md)

## Provenance

Shrink root-cause decomposition into operational / internal / external is the standard taxonomy
used by NRF (National Retail Federation) annual retail security surveys and by loss prevention
practitioners. The three-bucket framework is the foundation of any defensible shrink-reduction
program design.

---

_Last reviewed: 2026-06-08 by `claude`._
