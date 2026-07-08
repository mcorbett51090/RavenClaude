# craft-beverage-operations

A RavenClaude plugin: a **craft-beverage (winery / brewery / distillery) operations** specialist team for the three engines of a craft-beverage producer — production & cost, the tasting room & club (DTC), and distribution & compliance.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Operations and financial decision-support — not legal, tax, or regulatory advice.** The agents make no licensing, franchise-law, or excise determinations and store no PII. Benchmarks (yields, COGS, channel margins, tasting-room conversion, club churn) are volatile and producer-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a target, a price, or a plan. Three-tier, self-distribution eligibility, TTB / state licensing, direct-ship permits, and excise are **jurisdiction-specific** and flagged for a licensed professional.

## What it's for

Running a craft-beverage producer well: each unit made at a known, defensible cost; capacity read as tanks/barrels/time before vessels are added; the DTC-vs-wholesale channel mix optimized on net margin and absorbable demand; a tasting room that converts and a club that retains; and a distribution/compliance structure that's mapped and routed — not guessed.

## Agents

| Agent | Use for |
| --- | --- |
| **craft-beverage-operations-lead** | Batch/yield planning, COGS per unit, tank/barrel/time capacity, packaging, DTC-vs-wholesale channel margin mix |
| **tasting-room-and-club-manager** | Tasting-room throughput & conversion, club/membership revenue & churn, DTC e-commerce, events |
| **beverage-distribution-compliance-advisor** | Three-tier vs self-distribution economics, distributor relationships & depletion, TTB / state licensing & excise concepts — flags to a professional |

## What's inside

- **4 skills** — production-planning-and-cogs, tasting-room-throughput-and-conversion, club-membership-and-dtc-revenue, three-tier-and-self-distribution-economics.
- **Knowledge bank** — [`craft-beverage-decision-trees.md`](knowledge/craft-beverage-decision-trees.md) (4 Mermaid trees: channel mix, add production capacity, design the club, self-distribute vs distributor) + [`craft-beverage-reference-2026.md`](knowledge/craft-beverage-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — craft-beverage KPI dashboard, channel-margin & COGS worksheet.
- **2 commands** — `/model-channel-mix`, `/design-club-tier`.

## Seams

Three-tier / franchise law, TTB and state licensing, direct-ship permits, excise tax, worker classification, wage/tax, lease → a licensed attorney/accountant and the regulator (the agents model the economics and map the structure and flag the call). Security/privacy verdicts → [`ravenclaude-core`](../ravenclaude-core/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install craft-beverage-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
