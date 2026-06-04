# Fleet & Logistics — Claude Code plugin

A fleet-operations team for a carrier, private fleet, or last-mile operator — it reads cost-per-mile against the ~$2.26 industry all-in (and the ~$1.78 non-fuel marginal), manages the operating ratio in a market that turned negative-margin in 2024, routes and dispatches to deadhead and utilization, and treats driver turnover (often 90%+ at large truckload carriers) as a unit-economics problem.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
fleet & logistics depth on top.

## What it does

Builds cost-per-mile bottom-up, manages the operating ratio, optimizes routing/dispatch against deadhead and utilization, runs preventive maintenance against CPM, and treats driver retention as economics. Produces cost-per-mile models, dispatch strategies, and fleet scorecards an operator acts on.

## Agents

- **`fleet-engagement-lead`** — The engagement — scoping the fleet problem, framing the read, routing, and synthesizing an action plan.
- **`dispatch-routing-specialist`** — Movement — routing, dispatch, deadhead reduction, utilization, and lane profitability.
- **`fleet-maintenance-specialist`** — The iron — preventive maintenance, maintenance CPM, downtime, and lifecycle/replacement.
- **`logistics-cost-analyst`** — The numbers — cost-per-mile, the operating ratio, fuel/MPG, retention economics, and the scorecard.

## Skills

- **`build-cost-per-mile`** — Build CPM from fixed and variable components, isolating fuel and the non-fuel marginal, so the cost is visible where it lives. Reach for this on any margin question.
- **`manage-the-operating-ratio`** — Read the operating ratio (expenses ÷ revenue) as the survival headline and decompose it before acting. Reach for this on any profitability question.
- **`reduce-deadhead`** — Read empty miles and truck utilization and build a routing/backhaul plan to lift the loaded-mile ratio. Reach for this when rate-per-mile looks fine but margin doesn't.
- **`run-preventive-maintenance`** — Run a PM program against maintenance CPM and downtime so a deferred PM doesn't become a roadside failure. Reach for this when repair costs rise.
- **`quantify-driver-retention`** — Read driver turnover as a quantified unit-economics cost across recruiting, training, and unseated trucks. Reach for this when turnover is high.

## Slash commands

- **`/fleet-logistics:build-cost-per-mile-bottom-up`** — Build cost-per-mile bottom-up
- **`/fleet-logistics:manage-the-operating-ratio`** — Manage the operating ratio
- **`/fleet-logistics:reduce-deadhead-and-raise-utilization`** — Reduce deadhead and raise utilization
- **`/fleet-logistics:run-preventive-maintenance-to-cpm`** — Run preventive maintenance to CPM
- **`/fleet-logistics:quantify-driver-retention-cost`** — Quantify driver retention cost

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install fleet-logistics@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a TMS, an ELD, or a DOT/FMCSA compliance authority — safety and hours-of-service questions route to a qualified compliance officer. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
