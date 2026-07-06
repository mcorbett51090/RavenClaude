# auto-repair-shop-operations

A RavenClaude plugin: an **independent auto-repair / general-automotive-service shop operations** specialist team for the three engines of a repair shop — the shop P&L / fixed-ops economics, the service-advisor front counter, and the technician bay workflow.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Operations and financial decision-support — not legal, tax, or OEM-warranty advice.** Labor-rate norms, labor-guide times, parts-margin figures, productivity benchmarks, and state estimate-authorization rules are volatile and market-/shop-/jurisdiction-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed against the shop's own numbers, the current labor guide, or the local statute before it drives a price, a target, or a pay plan. The agents store no customer PII.

## What it's for

Running a repair shop well: an effective labor rate that survives discounts and comebacks, technicians who bill more hours than they clock, a parts matrix that carries its margin, a front counter that converts an honest inspection into a well-margined sale, and a bay workflow that fixes the car right the first time and recovers the work that got declined.

## Agents

| Agent | Use for |
|---|---|
| **auto-repair-shop-lead** | Shop P&L, effective labor rate, bay/tech productivity, labor + parts gross profit, comeback rate, car count/scheduling |
| **service-advisor-estimator** | Write-up, digital vehicle inspection (DVI), inspection-to-estimate, approval workflow, declined-work follow-up, ethical upsell |
| **technician-workflow-manager** | Dispatch, flat-rate vs actual hours, WIP/RO aging, parts staging, quality/comeback control |

## What's inside

- **4 skills** — effective-labor-rate-and-gross-profit, estimate-and-dvi-workflow, technician-productivity-and-efficiency, ro-lifecycle-and-comeback-control.
- **Knowledge bank** — [`auto-repair-shop-decision-trees.md`](knowledge/auto-repair-shop-decision-trees.md) (4 Mermaid trees: price a job / labor + parts matrix, comeback root-cause triage, declined-work follow-up, tech pay flat-rate vs hourly) + [`auto-repair-shop-reference-2026.md`](knowledge/auto-repair-shop-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — repair-order workflow, shop KPI dashboard.
- **2 commands** — `/build-estimate`, `/diagnose-comebacks`.

## Seams

Dealer-service-department fixed ops → [`automotive-dealership`](../automotive-dealership/) · fleet-maintenance customers → [`fleet-logistics`](../fleet-logistics/) · owner-operator single-trade service-business economics → [`skilled-trades-contracting`](../skilled-trades-contracting/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install auto-repair-shop-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
