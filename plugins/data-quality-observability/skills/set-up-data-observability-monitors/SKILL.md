---
name: set-up-data-observability-monitors
description: Stand up the observability monitors that watch for the unknown over time — freshness, volume, schema-drift, and distribution/anomaly monitors — each anchored to a baseline and a tolerance (not a hard-coded magic number), then wire owner-routed alerting and link a data-incident runbook. Reach for this when the user asks "set up freshness/volume monitors", "alert us before a stakeholder notices bad data", or "detect schema drift and distribution anomalies". Used by `data-quality-engineer` (primary).
---

# Skill: set-up-data-observability-monitors

> **Invoked by:** `data-quality-engineer` (primary). Also consulted by `data-quality-architect` to confirm the chosen platform covers the pillars in scope.
>
> **When to invoke:** "Set up freshness / volume monitors"; "alert us before a stakeholder finds bad data"; "detect schema drift"; "flag distribution/anomaly shifts"; any move from "we assert known rules" to "we watch for the unknown over time".
>
> **Output:** freshness / volume / schema-drift / distribution monitors — each with a baseline + tolerance — plus owner-routed alert wiring and a link to the data-incident runbook.

## Procedure

1. **Start with the highest-ROI pillars.** Stand up **freshness** and **volume** monitors first — they catch most real incidents cheaply. Add **schema-drift** and **distribution/anomaly** monitors after, where the dataset's value justifies them. Never lead with 200 column checks.
2. **Freshness monitor.** Define "how stale is too stale" against the dataset's event/landing time (e.g., "≤ 2h behind `ordered_at`"). Anchor to the expected cadence, and set the tolerance from the pipeline's real variance, not a guess.
3. **Volume monitor.** Watch row count / bytes per load against a **rolling baseline** (e.g., trailing-7-day mean) with a stated **tolerance** (±X% or ±Nσ). A sudden 40% drop or a doubling is the signal — a fixed `count > 1000` is not.
4. **Schema-drift monitor.** Watch for added/removed/renamed columns and type changes at the producer boundary. A silent schema change upstream is the single most common root cause of a bad-data incident — catch it at the seam.
5. **Distribution / anomaly monitor.** For the columns that carry meaning (a rate, an amount, a category share), watch the distribution against a baseline with a tolerance. Choose the detector deliberately: a **threshold/rule** where the acceptable band is known and stable; a **statistical/ML** detector (seasonality-aware) where the metric moves and a static band would false-alarm. Every anomaly monitor needs a **baseline + a tolerance**, never a magic number.
6. **Assign an owner + severity to every monitor, and route the alert.** An ownerless alert is noise; alert fatigue kills the program. Send each alert to the named owner's channel, set block-vs-warn (circuit-break only where downstream harm > pipeline-stall cost), and **link the data-incident runbook** so the on-call has a path, not just a red light.
7. **Capture it** in [`../../templates/data-quality-check-spec.md`](../../templates/data-quality-check-spec.md), and point the alert at [`../../templates/data-incident-runbook.md`](../../templates/data-incident-runbook.md).

## Worked example

> User: "We keep finding stale/wrong data after the fact. Set up monitors on `fct_orders` so we hear first."

- **Freshness:** alert if `max(ordered_at)` is > 2h behind wall clock during business hours; owner = analytics on-call; **blocks** the downstream revenue-dashboard refresh.
- **Volume:** daily order count vs trailing-7-day mean, tolerance ±20%; a >20% drop **warns** (could be a real slow day) but pages if it coincides with a freshness miss.
- **Schema-drift:** alert on any column add/drop/type-change on the upstream `raw.orders` source — this is where a silent producer change would first show.
- **Distribution:** `order_total` mean and the cancelled-share ratio vs a seasonality-aware baseline (weekends differ), tolerance ±3σ → a **statistical** detector, not a fixed threshold, because the metric moves.
- **Routing:** all four to `#data-oncall`, each with a link to the incident runbook; freshness+schema are block-severity, volume+distribution warn-then-escalate.

## Guardrails

- Freshness + volume first — highest ROI. Resist starting with a wall of column tests.
- Every monitor has a **baseline + tolerance**; a hard-coded magic number is a false-alarm factory.
- Threshold vs statistical/ML is a deliberate choice: static band for stable metrics, seasonality-aware detector for moving ones.
- Every monitor has an **owner + severity** and routes to a real channel with a **runbook link** — no ownerless alerts.
- Block-vs-warn per monitor; don't circuit-break a low-stakes signal into a pipeline stall.
- Monitors watch for the **unknown**; they don't replace the **tests** that assert known rules — ship both (see [`design-data-contracts-and-tests`](../design-data-contracts-and-tests/SKILL.md)).
- Anomaly-detection approaches, SLIs, and the tooling map live in [`../../knowledge/data-observability-patterns-2026.md`](../../knowledge/data-observability-patterns-2026.md); volatile platform facts carry a retrieval date.
