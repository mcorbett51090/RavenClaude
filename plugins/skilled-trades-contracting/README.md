# Skilled Trades Contracting — Claude Code plugin

An estimating-and-field-operations team for an HVAC, electrical, or plumbing contractor — it estimates to a loaded labor rate and true material cost, prices on a flat-rate book rather than guessing hours, runs the field on billable-hour efficiency and callback rate, and reads the trade P&L the way an owner who's also the best technician needs to.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
skilled trades contracting depth on top.

## What it does

Builds estimates on loaded labor and real material cost, prices service on a defensible flat-rate book, runs dispatch and field productivity on billable-efficiency and first-time-fix, and reads the contractor P&L. Produces estimates, flat-rate pricing, and field-ops scorecards a contractor acts on.

## Agents

- **`trades-engagement-lead`** — The engagement — scoping the contractor's problem, framing the read, routing, and synthesizing an action plan.
- **`estimating-specialist`** — Estimates and pricing — loaded labor rate, material cost, flat-rate book, and the bid.
- **`field-operations-specialist`** — The field — dispatch, billable-hour efficiency, first-time-fix, truck utilization, and scheduling.
- **`trade-business-analyst`** — The numbers — job costing, the contractor P&L, close rate/average ticket, truck utilization, and the scorecard.

## Skills

- **`build-the-loaded-rate`** — Build a billable labor rate that absorbs wage, burden, vehicle, tools, insurance, and overhead, so every hour sold makes money. Reach for this before any estimate or flat-rate book.
- **`build-flat-rate-book`** — Build a flat-rate price book from loaded labor and real material cost with good/better/best options, so service pricing protects margin. Reach for this on service pricing.
- **`raise-billable-efficiency`** — Read the billable-hour ratio and cut non-billable drive, restock, and rework time, since billable efficiency is the field's master number. Reach for this on a productivity question.
- **`cut-callbacks`** — Read first-time-fix and quantify the callback labor cost, then fix truck stocking and diagnosis, since a callback is a free truck roll. Reach for this when callbacks are high.
- **`read-the-sales-levers`** — Read close rate and average ticket and option-presentation, since they move revenue more than lead volume. Reach for this before spending on marketing.

## Slash commands

- **`/skilled-trades-contracting:build-the-loaded-labor-rate`** — Build the loaded labor rate
- **`/skilled-trades-contracting:build-the-flat-rate-book`** — Build the flat-rate book
- **`/skilled-trades-contracting:raise-billable-hour-efficiency`** — Raise billable-hour efficiency
- **`/skilled-trades-contracting:cut-the-callback-rate`** — Cut the callback rate
- **`/skilled-trades-contracting:read-the-sales-levers`** — Read the sales levers

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install skilled-trades-contracting@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not an FSM/dispatch platform, an accounting system, or a code/licensing authority — permit, code, and licensing questions route to the AHJ and a licensed tradesperson. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
