# Precision Agriculture — Claude Code plugin

An agronomy-and-farm-operations team for a grower, farm manager, or ag retailer — it manages inputs to agronomic and economic return (not maximum yield), reads yield by management zone rather than field average, times operations to the agronomic and weather window, and reads the farm P&L per acre the way an operator who lives the margin does.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
precision agriculture depth on top.

## What it does

Manages fertility and crop protection to economic optimum, reads yield by management zone, times operations to agronomic windows, and reads cost and margin per acre. Produces input plans, zone-management reads, and per-acre economics a grower acts on.

## Agents

- **`agronomy-engagement-lead`** — The engagement — scoping the grower's problem, framing the read, routing, and synthesizing a season plan.
- **`crop-agronomist`** — Agronomy — fertility, crop protection, hybrid/variety selection, and operation timing, as decision-support.
- **`farm-operations-analyst`** — The numbers — per-acre cost and margin by field, zone yield analytics, input ROI, and the scorecard.
- **`ag-market-analyst`** — The outside view — commodity price, input cost trends, marketing/hedging frames, and basis.

## Skills

- **`optimize-input-economics`** — Set input rates at the economic optimum where marginal return equals marginal cost, not at agronomic maximum, so the last unit pays. Reach for this on any input decision.
- **`manage-by-zone`** — Read yield and soil by management zone and apply variable-rate inputs where they pay, instead of a field average. Reach for this on a yield or input question.
- **`time-the-operations`** — Time planting, application, and harvest to the agronomic and weather window, since timing drives yield and quality more than rate. Reach for this on an operations-timing question.
- **`build-fertility-from-data`** — Build the fertility program from current soil/tissue data and removal rates, not last year's program, so neither over- nor under-application costs margin. Reach for this on a fertility question.
- **`build-per-acre-economics`** — Build cost and margin per acre by field so the money-losing acres are visible. Reach for this on any margin question.

## Slash commands

- **`/precision-agriculture:optimize-input-economics`** — Optimize input economics
- **`/precision-agriculture:manage-by-zone`** — Manage by zone
- **`/precision-agriculture:time-the-operations`** — Time the operations

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install precision-agriculture@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a farm-management software platform, an equipment telematics system, or an agronomic/pesticide-label authority — application rates and label compliance route to a licensed agronomist/applicator. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
