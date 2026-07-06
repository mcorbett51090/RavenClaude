# travel-agency-tour-operations

A RavenClaude plugin: a **travel agency / tour-operator operations** specialist team for the three engines of a leisure-travel business — the agency P&L and revenue model, itinerary design and multi-supplier booking, and supplier & commission management.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not legal, tax, or financial advice.** Supplier fare rules, commission rates, cancellation penalties, BSP/ARC settlement mechanics, and seller-of-travel / E&O requirements are volatile and supplier-/jurisdiction-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a quote, a booking, or a commission claim. The agents store no traveler PII.

## What it's for

Running a travel agency well: a revenue model that prices the advisor's expertise (not just commission), itineraries designed and documented so a change is a lookup and not a crisis, groups built on contracted blocks instead of optimism, disruptions recovered fast enough to earn the next booking, and every earned commission tracked and actually collected.

## Agents

| Agent | Use for |
|---|---|
| **travel-agency-operations-lead** | Agency P&L, revenue model (commission vs service fee vs markup), supplier mix, host-agency splits, booking systems, E&O / seller-of-travel risk |
| **itinerary-and-booking-specialist** | Itinerary design, multi-supplier booking, pricing/quoting, FIT vs group, changes/cancellations, disruption service-recovery, documentation |
| **supplier-and-commission-manager** | Supplier relationships, commission tracking & recovery, net vs commissionable, BSP/ARC settlement, preferred-supplier/consortia |

## What's inside

- **4 skills** — itinerary-design-and-quoting, supplier-and-commission-management, group-vs-fit-trip-operations, service-recovery-and-disruption.
- **Knowledge bank** — [`travel-agency-decision-trees.md`](knowledge/travel-agency-decision-trees.md) (4 Mermaid trees: revenue model, group vs FIT, disruption/service-recovery, commission-recovery chase) + [`travel-agency-reference-2026.md`](knowledge/travel-agency-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — itinerary & quote, supplier commission tracker.
- **2 commands** — `/build-itinerary-quote`, `/reconcile-commissions`.

## Seams

Domain-neutral protocols, structured output, and security/privacy verdicts → [`ravenclaude-core`](../ravenclaude-core/). Binding legal / seller-of-travel / E&O questions → counsel or the regulator; binding tax/accounting → the agency's financial authority. This team frames the operations exposure, not the binding legal or financial answer.

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install travel-agency-tour-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
