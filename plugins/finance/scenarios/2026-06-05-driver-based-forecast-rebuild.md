---
scenario_id: 2026-06-05-driver-based-forecast-rebuild
contributed_at: 2026-06-05
plugin: finance
product: fpa
product_version: "n/a"
scope: likely-general
tags: [fpa, driver-based, forecast, hardcodes, scenarios]
confidence: medium
---

## Problem

A company's revenue forecast was a single trend line — last year's revenue × a growth percentage typed into a cell — and it had missed three quarters running, alternating high then low, with no one able to say *why*. Leadership had lost trust in the number and was steering off gut. The ask was "make the forecast believable again," but the deeper problem was that the model exposed no levers: when an assumption was wrong, there was nothing to point at and fix.

## Context

- Segment: B2B company with a sales-led motion, enough operating history to calibrate drivers (≥ 6 quarters), one currency.
- Constraint: the existing model had the growth rate, a tax rate, and a headcount-cost factor **hardcoded inside formulas** (`=PriorRev*1.18`, `*0.21`) — so a reviewer couldn't see the assumptions, and a scenario meant editing formulas by hand. No documented assumption set, no scenario branches, no forecast-accuracy tracking.
- The line was material and its drivers were knowable and had history — the textbook case for driver-based, not trend.

## Attempts

- Tried: traversed the forecast-method tree before rebuilding. Material line + knowable drivers + operating history to calibrate → **driver-based**, not trend (trend is for immaterial/stable lines) and not zero-based (no cost-reset mandate). Outcome: chose the method deliberately instead of inheriting the trend by default.
- Tried: decomposed revenue into quantity × rate (pipeline → win-rate → ACV → ramp for new reps; installed base × NRR for expansion), with **every driver promoted to a labeled Inputs sheet** (§3 #2 — no hardcodes in mechanics). Outcome: the model now showed the levers; a wrong forecast pointed at a *specific* driver (win-rate had been assumed flat while it was actually declining).
- Tried: added **three scenarios from one switch** (base / upside / downside) and a forecast-accuracy (bias + MAPE) tracker against the locked budget held *beside* the forecast, not overwriting it. Outcome: the alternating miss turned out to be a calibration/bias problem — the trend model had no way to learn from its own error; the driver model did.

## Resolution

The rebuilt forecast was driver-based with a documented, labeled assumption set, one scenario switch driving base/upside/downside, and a bias/MAPE loop so the team could see whether they were systematically over- or under-calling. The first refresh attributed the prior misses to a declining win-rate the trend line structurally couldn't see. Leadership got a steering tool, not a number to defend.

**Action for the next analyst hitting this pattern:** **pick the method off the forecast-method tree before you build — a material line with knowable drivers and history is driver-based, not a trend cell.** Promote every assumption to a labeled Inputs sheet (no hardcodes buried in formulas), drive base/upside/downside from one switch, and hold the forecast *beside* the frozen budget with a bias/MAPE accuracy loop — a forecast that can't learn from its own error will keep alternating misses. Canonical references: the forecast-method tree in [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md), [`../knowledge/fpa-operating-model-and-planning.md`](../knowledge/fpa-operating-model-and-planning.md), and the [`driver-based-forecasting`](../skills/driver-based-forecasting/SKILL.md) skill.

**Sources (retrieved 2026-06-05):**
- CFO Advisors — forecast-accuracy KPIs, setting 2025 targets (MAPE, bias tracking): https://cfoadvisors.com/blog/forecast-accuracy-kpis_-setting-2025-targets-for-finance-teams
- Cube — automated variance analysis to improve forecasting accuracy: https://www.cubesoftware.com/blog/financial-variance-analysis

Forecast-accuracy targets (high performers under ~5% MAPE on quarterly revenue; ~8% average in inflation/energy-exposed sectors for FY2025) are dated benchmarks that move — `[verify-at-use]` against the entity's sector and the current period (§3 #1).
