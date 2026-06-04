# E-commerce & DTC — Claude Code plugin

A growth-and-unit-economics team for a DTC brand operator — it protects the LTV:CAC ratio (the 3:1 line below which a brand bleeds), reads conversion against the 1.4–1.8% average, attacks the retention gap (the average brand keeps just ~28% for a second purchase), and reads contribution margin after the real cost of acquisition and returns.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
e-commerce & dtc depth on top.

## What it does

Holds LTV:CAC as the master ratio, reads the conversion funnel and AOV, builds retention as the profit engine, and computes contribution margin after CAC, shipping, and returns. Produces unit-economics models, acquisition-channel reads, and retention plans a DTC operator acts on.

## Agents

- **`ecommerce-lead`** — The engagement — scoping the growth problem, framing the read, routing, and synthesizing a growth plan.
- **`merchandising-specialist`** — Product and conversion — assortment, pricing, AOV levers, product pages, and the conversion funnel.
- **`performance-marketing-strategist`** — Acquisition — CAC by channel, channel mix, creative/offer testing, and acquisition efficiency.
- **`retention-analytics-analyst`** — The numbers — LTV, repeat rate, cohort retention, contribution margin, and the scorecard.

## Skills

- **`read-ltv-cac`** — Read LTV:CAC against the 3:1 line and contribution margin after the real costs, so a profitability problem is diagnosed correctly. Reach for this on any growth/profit question.
- **`diagnose-the-funnel`** — Locate a conversion problem by funnel stage — traffic, product page, cart, checkout — instead of reading the headline rate. Reach for this when conversion is low.
- **`build-the-retention-engine`** — Read cohort retention and the repeat rate and build the second-purchase engine, since retention compounds LTV. Reach for this when growth depends on acquisition alone.
- **`manage-cac-by-channel`** — Read CAC by channel and cohort and allocate budget to efficiency, instead of a blended number. Reach for this when CAC climbs.
- **`cost-the-returns`** — Read return rate and its full cost as a contribution-margin line, so a high-return category isn't mistaken for a winner. Reach for this on a margin question.

## Slash commands

- **`/ecommerce-dtc:read-ltvcac-and-contribution-margin`** — Read LTV:CAC and contribution margin
- **`/ecommerce-dtc:diagnose-the-conversion-funnel`** — Diagnose the conversion funnel
- **`/ecommerce-dtc:build-the-retention-engine`** — Build the retention engine

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install ecommerce-dtc@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a storefront platform, an ad account, or a payments/tax authority — platform configuration and sales-tax nexus route to the relevant specialists. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
