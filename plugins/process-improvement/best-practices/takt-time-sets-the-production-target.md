# Takt Time Sets the Production Target, Not the Machine Rate

**Status:** Pattern
**Domain:** Process Improvement — Lean / flow design
**Applies to:** `process-improvement`

---

## Why this exists

Teams designing a future-state process often aim to maximize the speed of their fastest step, or match output to internal capacity. Neither produces flow. **Takt time** is the rate at which the customer consumes output, and it is the only correct target for each process step. A step faster than takt produces overproduction (waste). A step slower than takt is the constraint. Designing to machine rate or maximum throughput without knowing takt is the most common cause of overproduction and WIP accumulation.

## How to apply

**Formula:**

```
Takt Time = Available Production Time ÷ Customer Demand Rate
```

**Example:**
- 8-hour shift with 30 min breaks → 450 minutes available
- Customer demand: 90 invoices per day
- Takt time = 450 ÷ 90 = **5 minutes per invoice**

Every process step's *cycle time* is then compared to takt:

| Step | Cycle time | vs Takt (5 min) | Action |
|---|---|---|---|
| Data entry | 3 min | Under takt — capacity slack | Combine with next step or re-balance |
| Approval | 8 min | **Over takt — bottleneck** | This is the constraint; improve here first |
| Filing | 2 min | Under takt | Combine or add to approval step |

**Design rules:**
- **Cycle time ≤ Takt** at every step is the future-state design goal.
- The pacemaker step (the one closest to but not exceeding takt) controls the pull signal.
- If demand rate changes seasonally, recalculate takt and rebalance — a takt calculation is not a one-time artifact.

**Do:**
- Express takt in the same time unit as cycle times (seconds for high-volume, minutes or hours for complex transactional work).
- Recompute takt when demand planning changes the daily rate.
- Use takt as the sizing input for staffing and cell design.

**Don't:**
- Design to average throughput of the current process — that embeds the current waste.
- Conflate takt time with the *target cycle time* for the constraint step (the constraint step should run *at* takt, not faster).
- Ignore takt for knowledge-work processes where demand is irregular — calculate a weekly or monthly takt and smooth the load.

## Edge cases / when the rule does NOT apply

- **Highly irregular demand** (e.g., year-end financial close): takt fluctuates too much to design to a single number. Use a capacity buffer and a load-leveling heijunka approach instead.
- **One-of-a-kind or project work**: takt does not apply as a step-level target; use critical-path scheduling instead.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — the agent that designs future-state flow using takt
- [`./value-stream-map-the-whole-not-a-slice.md`](./value-stream-map-the-whole-not-a-slice.md) — the VSM that identifies the pacemaker step takt sizing targets

## Provenance

Standard Lean flow-design principle (Rother & Shook, "Learning to See"; Toyota Production System). Takt-time formula is textbook Lean Enterprise Institute practice. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
