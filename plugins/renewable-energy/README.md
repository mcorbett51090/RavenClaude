# Renewable Energy — Claude Code plugin

A project-development team for a solar/storage developer, EPC, or asset owner — it models LCOE and project IRR against a cost-per-watt that ran ~$2.56 in 2025, navigates the interconnection queue that gates most projects, structures around the post-2025 ITC shift (residential 25D ended; 48E/PPA pathways remain), and reads O&M and degradation the way a 25-year asset demands.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
renewable energy depth on top.

## What it does

Models LCOE, project IRR, and the financing structure, sequences interconnection and permitting (the real schedule risk), structures around the 2025-2026 tax-credit shift, and reads O&M, availability, and degradation over the asset life. Produces project pro-formas, interconnection plans, and asset-performance reads a developer acts on.

## Agents

- **`renewables-engagement-lead`** — The engagement — scoping the project question, framing the pro-forma, routing, and synthesizing a development plan.
- **`solar-project-developer`** — Development — site/resource, permitting, the development timeline, and incentive structuring.
- **`grid-interconnection-specialist`** — The grid — the interconnection queue, study process, upgrade costs, and the tariff/PPA interface.
- **`energy-finance-analyst`** — The numbers — LCOE, project IRR, net cost after incentives, O&M/degradation, and the pro-forma.

## Skills

- **`model-lcoe-and-irr`** — Model levelized cost of energy and project IRR together, on net cost after the live incentives, since they answer different questions. Reach for this on any project-economics question.
- **`model-the-interconnection-queue`** — Read the interconnection queue, study sequence, and likely upgrade allocation as the project's schedule and cost risk. Reach for this before committing a schedule.
- **`structure-the-incentive`** — Structure the project around the incentive pathway that's actually available post-2025, with a date, instead of an expired one. Reach for this on any financing-structure question.
- **`read-asset-performance`** — Read availability, degradation, and O&M cost over the 25-year asset life so the IRR rests on real operations. Reach for this on an operating-asset question.
- **`value-storage-dispatch`** — Value a battery on its dispatch use-case — arbitrage, demand-charge reduction, capacity — not a flat $/kWh. Reach for this on a storage add.

## Slash commands

- **`/renewable-energy:model-lcoe-and-project-irr`** — Model LCOE and project IRR
- **`/renewable-energy:model-the-interconnection-queue`** — Model the interconnection queue
- **`/renewable-energy:structure-to-the-live-incentive`** — Structure to the live incentive
- **`/renewable-energy:read-asset-performance-over-life`** — Read asset performance over life
- **`/renewable-energy:value-storage-by-dispatch`** — Value storage by dispatch

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install renewable-energy@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not an engineering/PE stamp, a utility tariff authority, or a tax/legal advisor — interconnection studies, structural/electrical design, and tax-credit qualification route to licensed professionals. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
