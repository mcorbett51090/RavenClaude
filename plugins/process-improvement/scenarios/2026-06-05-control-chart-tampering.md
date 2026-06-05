---
scenario_id: 2026-06-05-control-chart-tampering
contributed_at: 2026-06-05
plugin: process-improvement
product: spc-capability
scope: likely-general
tags: [spc, tampering, common-cause, over-adjustment, deming]
confidence: medium
reviewed: false
---

## Problem

A call-center operations manager reviewed average-handle-time (AHT) every morning and adjusted staffing or coaching whenever the prior day was "bad." Despite constant intervention, AHT variation was *getting worse*, not better, and the team felt whipsawed. The request: "why does reacting fast make it worse?"

## Context

- Sector: shared-services / BPO; AHT was a contractual SLA with the client, reported daily.
- Constraint: the manager was rewarded for "responsiveness" — reacting to every dip was the cultural expectation, so "do nothing today" felt like negligence.
- There was a daily AHT table but **no control chart** — every reaction was to a single day's raw number, with no way to tell signal from noise.

## Attempts

- Tried: built an I-MR control chart of daily AHT (the control-chart-selection tree → individuals data, one reading per day → I-MR). Computed ±3σ limits from the data, not the SLA target. Outcome: the day-to-day swings the manager had been reacting to were **all inside the control limits** — common-cause noise. `[ESTIMATE]` data, illustrative.
- Tried: mapped the manager's reactions onto Deming's **funnel experiment**. Adjusting staffing in response to common-cause variation is "Rule 2/3" tampering — it provably *adds* variation. The alternating over-correct pattern (Nelson rule 4: 14 points alternating up/down) was visible in the chart's history. Outcome: named the mechanism — the manager's own reactions were the special cause.
- Tried (the move that worked): instituted a **reaction plan** — act only when a stated Western Electric / Nelson rule fires; otherwise leave the process alone and work the *system* (the common-cause level) via a proper improvement project if the stable average itself missed the SLA. Outcome: AHT variation tightened within weeks once the tampering stopped; the stable mean was then addressed as a system-level project, not a daily reaction.

## Resolution

The manager was **tampering** — treating common-cause variation as if it were special — which Deming identifies as the most common and costly process-management mistake. The fix was not a new staffing model; it was *reacting to signals, not to individual points*, and addressing an unacceptable stable level as a system change rather than a daily scramble.

**Action for the next consultant hitting this pattern:** when someone reacts to a metric's every movement, traverse the **common-cause-vs-special-cause** tree in [`../knowledge/spc-response-decision-trees.md`](../knowledge/spc-response-decision-trees.md). Step 0 is "is there a control chart at all?" — without limits you cannot tell signal from noise. If the movements are inside the limits, the right action is *no action* (and a system-level project if the stable level is wrong). Cross-reference [`../best-practices/separate-common-cause-from-special-cause.md`](../best-practices/separate-common-cause-from-special-cause.md).

**Sources for facts cited:** tampering / the funnel experiment — [The W. Edwards Deming Institute: The Funnel Experiment](https://deming.org/explore/the-funnel-experiment/) and [SPC for Excel: Over-controlling a Process](https://www.spcforexcel.com/knowledge/variation/overcontrolling-process-funnel-experiment/) (retrieved 2026-06-05); the WE/Nelson rules are in [`../knowledge/six-sigma-statistics-and-spc.md`](../knowledge/six-sigma-statistics-and-spc.md) §4. Figures are illustrative `[ESTIMATE]`; validate against the operation's actual data.
