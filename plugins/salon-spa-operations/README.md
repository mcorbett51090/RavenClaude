# salon-spa-operations

A RavenClaude plugin: a **salon / spa / barbershop operations** specialist team for the three engines of a service-chair business — the owner-level P&L, the front-desk booking engine, and provider economics.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Operations and financial decision-support — not legal, tax, or employment-classification advice.** Benchmarks (utilization, retail-attach, no-show rates, commission splits, booth rent) are volatile and market-/model-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a target, a price, or a policy. Worker classification, wage/tax, lease, and deposit/payment rules are flagged for a licensed professional. The agents store no client PII.

## What it's for

Running a salon, spa, or barbershop well: a full calendar defended against no-shows and fed by rebooking, chair-hours and room-hours sold at high utilization, a service mix and retail attach that carry margin, and a provider compensation model chosen deliberately on the real book.

## Agents

| Agent | Use for |
|---|---|
| **salon-spa-operations-lead** | Chair/room utilization, service mix, retail attach, membership/package revenue, the staffing model |
| **front-desk-booking-manager** | Online booking, no-show / late-cancel policy & deposits, rebooking at checkout, waitlist, reminders |
| **stylist-chair-economics-advisor** | Commission tiers, booth rent, product cost, prebooking, clientele building, retention |

## What's inside

- **4 skills** — booking-and-no-show-control, chair-and-room-utilization, retail-attach-and-service-mix, compensation-models-commission-vs-booth-rent.
- **Knowledge bank** — [`salon-spa-decision-trees.md`](knowledge/salon-spa-decision-trees.md) (4 Mermaid trees: compensation model, no-show policy & deposit, rebook at checkout, price the service menu) + [`salon-spa-reference-2026.md`](knowledge/salon-spa-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — salon KPI dashboard, service menu & pricing worksheet.
- **2 commands** — `/set-noshow-policy`, `/model-compensation`.

## Seams

Worker classification, wage/tax, lease law, and deposit/payment-processor rules → a licensed professional (the agents model the economics and flag the call). Security/privacy verdicts → [`ravenclaude-core`](../ravenclaude-core/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install salon-spa-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
