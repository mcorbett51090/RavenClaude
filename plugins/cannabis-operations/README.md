# Cannabis Operations — Claude Code plugin

A compliance-and-retail-operations team for a licensed cannabis operator — it runs seed-to-sale traceability against the state track-and-trace system (Metrc/BioTrack/LeafData), manages the 280E tax burden that makes COGS allocation existential, runs dispensary retail on margin and basket, and reads a ~$45B U.S. market where the rules change at the state line.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
cannabis operations depth on top.

## What it does

Builds seed-to-sale compliance against the state's mandated system, allocates COGS aggressively-but-defensibly under 280E, runs dispensary retail on margin/basket/inventory turns, and tracks the state-by-state regulatory patchwork. Produces compliance SOPs, 280E COGS frameworks, and retail scorecards an operator acts on.

## Agents

- **`cannabis-engagement-lead`** — The engagement — scoping the operator's problem, framing the read, routing, and synthesizing an action plan.
- **`seed-to-sale-compliance-specialist`** — Traceability — track-and-trace reconciliation, SOPs, testing/remediation, and the state regulatory patchwork.
- **`dispensary-retail-operations-specialist`** — The store — category margin, basket/UPT, inventory turns, menu/assortment, and budtender productivity.
- **`cannabis-finance-analyst`** — The numbers — 280E COGS allocation, unit economics, inventory/turns analytics, and the scorecard, as decision-support.

## Skills

- **`reconcile-seed-to-sale`** — Reconcile physical inventory to the state track-and-trace system and resolve discrepancies as compliance events, not bookkeeping. Reach for this on any traceability question.
- **`frame-280e-cogs`** — Build a defensible COGS-allocation framework under 280E, as decision-support for the CPA, so only properly-capitalized cost reduces taxable income. Reach for this on any tax-burden question.
- **`run-dispensary-retail`** — Read category margin, basket, and turns and lift store profit without discount-driven traffic. Reach for this on a store-margin question.
- **`manage-the-state-patchwork`** — Anchor every compliance answer to the specific state and date, since track-and-trace, testing, potency, and tax all vary. Reach for this on any compliance claim.
- **`read-inventory-turns`** — Read inventory turns as both a cash and a compliance metric, flagging aged and perishable product. Reach for this on a cash or expiry question.

## Slash commands

- **`/cannabis-operations:reconcile-seed-to-sale`** — Reconcile seed-to-sale
- **`/cannabis-operations:frame-280e-cogs-allocation`** — Frame 280E COGS allocation
- **`/cannabis-operations:run-dispensary-retail-on-margin`** — Run dispensary retail on margin

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install cannabis-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a track-and-trace system, a seed-to-sale platform, or a tax/legal authority — 280E positions and licensing route to qualified cannabis counsel and CPAs. Cannabis remains federally illegal; this is operational, not legal, guidance. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
