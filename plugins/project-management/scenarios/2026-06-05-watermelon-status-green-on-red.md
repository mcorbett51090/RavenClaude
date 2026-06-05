---
scenario_id: 2026-06-05-watermelon-status-green-on-red
contributed_at: 2026-06-05
plugin: project-management
product: stakeholder-governance
product_version: "n/a"
scope: likely-general
tags: [status, watermelon, rag, earned-value, spi, governance]
confidence: medium
reviewed: false
---

## Problem

A ~9-month predictive systems-integration project had reported **green** RAG for five consecutive weekly cycles. In week 18 the sponsor was blindsided when a milestone slipped two weeks with no prior warning. The PM's instinct was that the slip was "sudden". It was not — the status had been a **watermelon** (green skin, red flesh) for over a month, and the question was how to make the reporting honest without turning the next steering meeting into a blame session.

## Context

- Track: predictive (PMBOK), fixed-scope/fixed-date SOW, steering committee monthly + weekly written status.
- Constraint: the weekly status template led with a **RAG table**, not a narrative, and the RAG was set by the PM's judgment ("we'll catch up"), not from the schedule or earned value. There was a baseline but no one was computing SPI against it.
- The team had been quietly burning its critical-path float for three weeks; by the time the float was gone there was no buffer left to recover the milestone.

## Attempts

- Tried: reconstructed earned value from the baseline. SPI had been **~0.88 for three weeks** before dropping to ~0.82 the week the milestone slipped `[ESTIMATE — illustrative]`. Per the Status-RAG decision tree, an SPI in the 0.80–0.95 band is **AMBER**, not green — the project had been mis-reported amber-as-green for the whole window. Outcome: established that the slip was knowable three weeks earlier from the numbers already in hand.
- Tried: rewrote the status template to **lead with a narrative** and put the RAG *after* the numbers, with a hard rule that the RAG cannot contradict SPI/CPI (the `status-leads-with-narrative-and-matches-the-numbers` best-practice). Outcome: removed the surface where judgment silently overrode the data.
- Tried (the move that worked): instrumented SPI/CPI weekly off the baseline (the `evm` mode of `scripts/evm_calc.py` does the arithmetic) and pre-wired the sponsor before the steering pack rather than letting the pack deliver the bad news cold. Outcome: the next two cycles reported amber honestly with a named recovery plan; the sponsor approved a contingency draw rather than being ambushed.

## Resolution

The slip was not sudden — it was a **reporting-discipline failure**: a RAG set by hope instead of by the numbers, on a template that led with colour instead of narrative. Fixing the *process* (narrative-first status, RAG derived from SPI/CPI, weekly earned-value, sponsor pre-wire) surfaced future slips while they were still recoverable.

**Action for the next PM hitting this pattern:** when a project has been green for a suspiciously long run on a fixed-scope predictive baseline, **compute SPI/CPI before you trust the colour.** A green RAG sitting on an SPI in the amber band (0.80–0.95) is a watermelon, not optimism — route it through the Status-RAG decision tree in [`../knowledge/pm-decision-trees.md`](../knowledge/pm-decision-trees.md), set the colour from the numbers, and handle the slip via the [`../knowledge/pm-recover-vs-escalate-slip-decision-tree.md`](../knowledge/pm-recover-vs-escalate-slip-decision-tree.md). Watch critical-path float as a finite resource — silent float burn is the early watermelon signal.

**Sources for framings cited:** earned-value SPI/CPI and the EAC/TCPI forecasts are standard PMBOK framings (SPI = EV/PV, CPI = EV/AC), web-verified 2026-06-05 — see [PMCLounge EVM formulas](https://www.pmclounge.com/all-pmp-cost-management-formulas/) and the [BrainBOK EVM guide](https://www.brainbok.com/guide/pm-study-notes/cost/earned-value-management). The 0.80/0.95 RAG thresholds are this plugin's conventions (Status-RAG tree), not a PMBOK constant — calibrate to the engagement. SPI values are illustrative for this scenario; validate against the project's actual baseline before a deliverable.
