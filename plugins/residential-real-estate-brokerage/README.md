# residential-real-estate-brokerage

A RavenClaude plugin: a **residential real-estate brokerage operations** specialist team for the engines of a residential brokerage — the brokerage/team P&L and pipeline, the listing lifecycle plus transaction coordination, and buyer representation, all on a fair-housing-clean, agency-disclosed compliance floor.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not legal, financial, real-estate-license, or lending advice.** This domain is fair-housing sensitive: commission rates, contingency periods, agency rules, and protected-class lists are volatile and jurisdiction-/agreement-specific — each carries a retrieval date + `[verify-at-use]` and must be confirmed against current law, the contract, and the brokerage's own agreements before it drives a price, an offer, a comp plan, or a disclosure. The agents store no client PII and never steer.

## What it's for

Running a residential brokerage well: a pipeline you can read stage by stage, a commission model that pencils for the agent and the house, listings priced to the comps and launched to win the first weekend, transactions that never miss a deadline, and buyers represented to a clean close — without a fair-housing or agency-disclosure misstep.

## Agents

| Agent | Use for |
|---|---|
| **residential-brokerage-lead** | Brokerage/team P&L, lead-to-close pipeline, commission splits/caps, recruiting & retention, agency/fair-housing compliance, brand/lead-gen |
| **listing-and-transaction-coordinator** | CMA/pricing, listing prep + MLS + marketing launch, contract-to-close timeline, contingencies, deadlines, docs |
| **buyer-agent-advisor** | Buyer needs analysis, showings, offer & negotiation strategy, financing coordination, closing |

## What's inside

- **4 skills** — cma-and-pricing-strategy, listing-launch-and-marketing, transaction-timeline-management, commission-split-and-cap-economics.
- **Knowledge bank** — [`residential-brokerage-decision-trees.md`](knowledge/residential-brokerage-decision-trees.md) (4 Mermaid trees: price a listing/CMA, represent buyer vs seller / dual-agency conflict, offer & counter strategy, commission split-vs-cap model) + [`residential-brokerage-reference-2026.md`](knowledge/residential-brokerage-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — listing launch plan, transaction timeline checklist.
- **2 commands** — `/build-cma`, `/manage-transaction-timeline`.

## Seams

Buyer financing mechanics → [`mortgage-lending`](../mortgage-lending/) · title/escrow & closing settlement → the `title-escrow-settlement` team · ongoing landlord/rental ops → [`property-management`](../property-management/) · commercial/investment deal economics (distinct model) → [`commercial-real-estate`](../commercial-real-estate/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install residential-real-estate-brokerage@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
