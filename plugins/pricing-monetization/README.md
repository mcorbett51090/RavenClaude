# pricing-monetization

> A RavenClaude plugin: the pricing & monetization team — the agents that own the one
> question no other plugin answers, **what to charge and how to package it.**

## What it is

A domain-neutral, 2-agent team for pricing strategy and monetization. It selects the
pricing model and value metric, designs packaging and tiers, runs (or specs)
willingness-to-pay research, sets discount and price-change governance, and
instruments the monetization metrics — then hands the *modeling* to `finance`, the
*go-to-market* to `sales-revops`, and the *roadmap* to `product-management`.

It is **advisory and educational** — not a guarantee of a financial outcome and not
legal advice. Price-fixing, MAP, and price-regulation questions route to counsel.

## Why it exists (the gap it fills)

Three plugins sit *around* a price but none owns it:

| Question | Owner |
|---|---|
| Is the model arithmetic right (LTV, margin, cash)? | `finance` |
| What should we build, for whom? | `product-management` |
| How do we sell it and pay comp? | `sales-revops` |
| **What do we charge, on what metric, in what package?** | **this plugin** |

## Roster

| Agent | Owns |
|---|---|
| **`pricing-strategist`** | Pricing-model selection, value-metric choice, packaging & tiering, price-change/migration plans, discount governance. |
| **`monetization-analyst`** | Willingness-to-pay research design, price-elasticity reading, monetization-metric definitions (ARPA/NRR/leakage), and judging whether a change worked. |

## What's inside

- **5 skills** — `pricing-model-selection`, `value-metric-design`, `packaging-and-tiering`, `willingness-to-pay-research`, `price-change-rollout`.
- **Knowledge bank (3 docs)** — three Mermaid decision trees (model / value-metric / WTP-method), a monetization-metric glossary with formulas, and a dated 2026 reference (model trends, AI-product pricing, packaging patterns, the price-change playbook).
- **10 best-practices** — value-not-cost, value-metric-first, WTP-is-researched, fence-don't-list, realized-price, change-is-a-migration, NRR-scoreboard, freemium-is-a-CAC-line, decompose-lift-from-mix-shift, not-legal-advice.
- **3 templates** — packaging-design worksheet, price-change rollout plan, WTP-study brief.
- **Scenarios bank** — per-seat-caps-an-AI-product, everyone-buys-the-cheapest-tier, did-the-price-increase-work.

## Install

```shell
/plugin marketplace update ravenclaude
/plugin install pricing-monetization@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0` (inherits the Team Lead, the Capability Grounding
and Structured Output protocols, and the security/review seams).

## Seams

`finance` (the dollar model) · `product-management` (what to build) · `sales-revops`
(quota/comp/deal-desk) · `applied-statistics` (is the price-test lift real?) ·
`fintech-payments-engineering` / `backend-engineering` (billing/metering) ·
`legal-ops-clm` + counsel (MAP / anti-trust / price regulation).

This plugin owns **the price, the metric, the package, and the governance.**
Everything downstream of the price belongs to someone else.
