---
name: mrp-and-production-planning
description: "Turn demand into a buildable plan: run MPS/MRP and net through the BOM, reconcile the forecast against finite capacity in S&OP, choose lot sizes on an honest setup-vs-holding trade, and build a finite schedule that respects the bottleneck — never infinite-capacity planning."
---

# MRP & Production Planning

## Start from the constraint, not the forecast
The bottleneck sets the plant's rate (Theory of Constraints). A master schedule that loads beyond the constraint's finite rate, or assumes unavailable material, is a wish. Load the constraint to its real sustainable rate, subordinate everything else, and reconcile demand vs supply in S&OP before releasing the MPS.

## MPS → MRP → BOM
The MPS states what end items, what quantity, in what bucket. MRP nets those requirements against on-hand + on-order through the BOM into planned orders and exception messages. The BOM is the spine — a bill drifted from as-built generates phantom shortages and wrong material plans. Validate BOM integrity before trusting the MRP run.

## S&OP reconciliation
The forecast is an input, not a fact. Lay the demand plan against the supply/capacity plan, name the gaps (capacity, material, labor), and offer options (overtime, second shift, lot-size change, date push) with the trade each makes. An accepted forecast with no reconciliation is a future stockout or a warehouse of WIP.

## Lot sizing
EOQ / fixed-period / lot-for-lot each trade setup cost against holding cost. On a constrained resource, every setup is throughput you don't get back — name the trade, don't default to big batches or to lot-for-lot. Size safety stock to demand/lead-time variability and a stated service level, not to feel.

## Produce to takt
Match output to takt (available time ÷ demand), not to max machine speed. Building ahead of takt makes inventory, not money.

## Output
A production-plan brief: the demand-vs-capacity reconciliation, the constraint it plans to, the time-phased MPS, the lot-sizing logic, the BOM assumptions, and the S&OP gaps. Hand SMED/changeover reduction to `process-improvement`, the forecast-model rigor to `applied-statistics`, and material lead-time gaps to `procurement-sourcing`.
