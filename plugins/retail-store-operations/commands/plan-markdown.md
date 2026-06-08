---
description: "Build a sell-through-triggered markdown cadence for aged/seasonal inventory: read sell-through and weeks-of-supply, set the first-markdown trigger and depth, the step-down, and the terminal clearance — not a reflexive calendar markdown."
argument-hint: "[SKU/category + sell-through + weeks-of-supply + season/end-date + margin]"
---

You are running `/retail-store-operations:plan-markdown`. Use `merchandising-analyst` + the `merchandising-and-assortment` skill.

## Steps
1. Read sell-through % and weeks-of-supply for the SKU/category against where it should be in its life-cycle. State the window for each metric.
2. Decide markdown-vs-hold (see the knowledge decision tree): is it tracking to plan, is WOS above the terminal threshold, is it seasonal/terminal or replenishable?
3. If slow sell-through is an assortment problem (wrong SKU) not a price problem, route to assortment rationalization before discounting.
4. Set the markdown cadence: first-markdown trigger + depth (the first is the cheapest), the step-down schedule, the terminal-clearance point — with the margin-vs-carrying-cost trade.
5. Route the seams: demand/elasticity model → `applied-statistics`; clear the marked-down/overstock SKUs → `inventory-and-replenishment-planner`; floor execution → `store-operations-lead`.
6. Emit the markdown plan + the Structured Output block (with `P&L impact:` and `Handoff to neighbours:`).
