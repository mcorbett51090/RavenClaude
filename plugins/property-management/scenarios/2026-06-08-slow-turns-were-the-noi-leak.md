---
scenario_id: 2026-06-08-slow-turns-were-the-noi-leak
contributed_at: 2026-06-08
plugin: property-management
product: turns
product_version: "n/a"
scope: likely-general
tags: [unit-turn, vacancy-loss, maintenance, backlog]
confidence: medium
reviewed: false
---

## Problem

A property reported acceptable maintenance spend but missed NOI, and leadership looked at rent first. The risk: slow unit turns convert into vacancy loss that never appears on a maintenance cost line — the rent simply never bills, so a turn problem masquerades as a revenue problem (§3 #3).

## Context

- Asset class: urban mid-rise with heavy turnover.
- Constraint: lost rent during turn = vacant units × turn days × daily rent (§3 #3).
- The team reasoned from the maintenance expense line, which looked fine.

## Attempts

- Tried: **quantified lost rent during turns** (`property_management_calc.py turn-time`). Outcome: the annualized vacancy loss from slow turns dwarfed the maintenance under-spend it came from.
- Tried: **aged the work-order backlog.** Outcome: make-readies were stuck behind a backlog of occupied-unit orders, stalling turns (§3 #3).
- Tried: **framed the backlog as a renewal risk** too. Outcome: occupied residents waiting on orders were a renewal flight risk, not just a queue (§3 #6).

## Resolution

The fix was a **dedicated make-ready crew and a backlog triage**, justified by the recovered rent — not a rent increase. The output was the lost-rent quantification, the backlog aging, and the NOI recovery estimate.

**Action for the next consultant hitting this pattern:** **quantify lost rent in turns before blaming rent for soft NOI.** Slow turns drain NOI as vacancy loss that no cost line shows; cut median turn days and triage the backlog. See Tree 1 and the `property_management_calc.py` `turn-time` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
