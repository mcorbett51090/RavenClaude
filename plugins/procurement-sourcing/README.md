# Procurement & Sourcing — Claude Code plugin

A strategic-sourcing team for a procurement or category lead — it segments spend before it sources (the Kraljic should-cost lens), runs the sourcing event on total cost of ownership rather than unit price, manages supplier risk as a portfolio, and reads the spend cube the way a category manager who owns savings does.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
procurement & sourcing depth on top.

## What it does

Builds spend visibility and category segmentation, runs sourcing on TCO and should-cost, manages supplier risk and concentration as a portfolio, and tracks realized vs negotiated savings. Produces category strategies, RFx frameworks, and spend-analytics reads a procurement leader acts on.

## Agents

- **`sourcing-lead`** — The engagement — scoping the sourcing problem, framing the category strategy, routing, and synthesizing a savings plan.
- **`category-strategist`** — Sourcing — category strategy, the Kraljic play, RFx design, TCO modeling, and should-cost.
- **`supplier-risk-specialist`** — Risk — supplier financial/operational risk, concentration, mitigation, and supply continuity.
- **`spend-analytics-analyst`** — The numbers — the spend cube, classification, realized-vs-negotiated savings, tail spend, and the scorecard.

## Skills

- **`segment-the-spend`** — Place a category on the supply-risk × spend matrix and match the sourcing play before sourcing, so you don't auction a strategic single-source. Reach for this before any sourcing event.
- **`source-on-tco`** — Run a sourcing decision on TCO — freight, quality, switching, inventory, lifecycle — not unit price, so a price 'savings' doesn't raise total cost. Reach for this on any sourcing event.
- **`manage-supplier-risk`** — Assess supplier and concentration risk across the base and mitigate single-source exposure, instead of a one-time checkbox. Reach for this on a continuity question.
- **`build-the-spend-cube`** — Build and classify the spend cube by category, supplier, and business unit, surfacing tail spend, so strategy rests on visibility. Reach for this when spend is opaque.
- **`validate-realized-savings`** — Measure realized savings against a finance-recognized baseline and locate leakage, so negotiated savings aren't mistaken for P&L impact. Reach for this on any savings claim.

## Slash commands

- **`/procurement-sourcing:segment-the-spend-kraljic`** — Segment the spend (Kraljic)
- **`/procurement-sourcing:source-on-total-cost-of-ownership`** — Source on total cost of ownership
- **`/procurement-sourcing:manage-supplier-risk-as-a-portfolio`** — Manage supplier risk as a portfolio

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install procurement-sourcing@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not an ERP/P2P system, a contract-management platform, or a legal authority — contract terms and supplier disputes route to legal and the contracting team. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
