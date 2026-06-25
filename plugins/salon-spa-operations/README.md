# salon-spa-operations

A RavenClaude plugin: a **salon & spa operations** specialist team for hair salons, day spas, and barbershops — so the chairs stay full, clients keep rebooking, and the margin stays healthy.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

## What it's for

Running the floor of a salon, spa, or barbershop: a calendar that's actually full (online booking, the empty mid-week chair, the color processing-time overlap that *is* capacity), a no-show policy with a deposit behind it, the compensation decision that defines the business — **commission vs booth/chair rental vs hybrid** and its control/tax trade — a service menu priced to margin with good-better-best tiers, the retail attachment that is the margin lifeline, and the rebooking rate that is the whole game. This is the **salon/spa-ops craft** — distinct from the books, the marketing, and HR law around it.

## Agents

| Agent | Use for |
|---|---|
| **salon-spa-operations-lead** | Front desk + client experience, the commission-vs-booth-rental decision, stylist staffing/retention, day-to-day ops, routing |
| **booking-and-retention-analyst** | Calendar utilization, online booking, double-booking + color overlap, gap-filling, the no-show/deposit policy, rebooking rate, retention |
| **service-menu-and-pricing-strategist** | Service-menu design (good-better-best, add-ons), pricing + price increases, retail/product attachment, service-mix margin |

## What's inside

- **5 skills** — design-service-menu-and-pricing, set-no-show-and-deposit-policy, choose-commission-vs-booth-rental, improve-rebooking-rate, plan-retail-attachment.
- **Knowledge bank** — [`salon-spa-operations-decision-trees.md`](knowledge/salon-spa-operations-decision-trees.md) (4 Mermaid trees: compensation model, empty-chair diagnosis, price increase, deposit policy) + [`salon-spa-operations-reference-2026.md`](knowledge/salon-spa-operations-reference-2026.md) (dated benchmark map).
- **7 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **3 templates** — service menu & pricing, no-show/deposit policy, compensation-model comparison.
- **3 commands** — `/design-service-menu`, `/set-no-show-policy`, `/compare-comp-models`.
- **1 advisory hook** — `check-salon-anti-patterns.sh` (cancellation policy with no deposit, comp plan with no classification, menu/pricing doc with no retail/rebooking). `SALON_STRICT=1` to block.

## Seams

The books, payroll mechanics, sales-tax filing → [`accounting-bookkeeping`](../accounting-bookkeeping/) · ad/social/email campaigns and promotions → [`marketing-operations`](../marketing-operations/) · the legal worker-classification verdict and employment law → [`people-operations-hr`](../people-operations-hr/) · client-PII / card-on-file / photo-consent verdicts → [`ravenclaude-core/security-reviewer`](../ravenclaude-core/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install salon-spa-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for routing rules, house opinions, and the output contract.
