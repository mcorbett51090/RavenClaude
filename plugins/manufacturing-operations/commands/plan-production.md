---
description: "Turn demand into a buildable plan: MPS/MRP, demand-vs-capacity reconciliation (S&OP), BOM check, lot sizing, and a constraint-respecting finite schedule."
argument-hint: "[demand/forecast + the line/resources + known bottleneck + BOM/material status]"
---

You are running `/manufacturing-operations:plan-production`. Use `production-planner` + the `mrp-and-production-planning` skill.

## Steps
1. State the demand/forecast and the planning horizon + bucket. If the forecast was never reconciled against supply, reconcile it (S&OP) before planning.
2. Identify the binding constraint and its real sustainable rate (route to shop-floor-and-oee-analyst if unknown). Plan to it — never to infinite capacity.
3. Check BOM integrity against as-built; flag phantom-shortage risk before trusting MRP.
4. Build the time-phased MPS; net through the BOM (MRP); choose lot sizes with the setup-vs-holding trade named.
5. Name the S&OP gaps (capacity / material / labor) and the options (overtime, shift, lot change, date push) with each trade.
6. Route the deep work: SMED/changeover → process-improvement; forecast-model rigor → applied-statistics; material lead-time → procurement-sourcing.
7. Emit the production-plan brief + the Structured Output block (with `Constraint respected:` and `Handoff to method teams:`).
