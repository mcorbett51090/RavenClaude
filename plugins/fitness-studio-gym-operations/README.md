# fitness-studio-gym-operations

A RavenClaude plugin: a **gym / boutique-fitness-studio operations** specialist team for the three engines of a fitness business — the membership P&L, the retention machine, and the class grid.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not legal, financial, or medical/exercise-prescription advice.** Churn/LTV benchmarks, class-fill targets, instructor-pay norms, and pricing figures are volatile and model-/market-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed against your own books before it drives a price, a pay model, or a growth decision. The agents store no member PII.

## What it's for

Running a fitness business well: a membership base that compounds because it retains, an onboarding that gets new members to a visit habit, a class grid scheduled on real demand and paid for correctly, and ancillary lines (personal training, retail, café) that add the margin dues can't reach.

## Agents

| Agent | Use for |
|---|---|
| **fitness-studio-operations-lead** | Membership P&L, growth vs churn, member LTV, class/floor utilization, ancillary revenue, pricing strategy |
| **membership-retention-manager** | Onboarding, attendance/engagement triggers, churn prediction & saves, win-back, referral, tier design |
| **class-schedule-coach-ops** | Class scheduling, instructor utilization & pay, capacity/fill, waitlist, no-show policy, sub coverage |

## What's inside

- **4 skills** — membership-growth-and-churn, member-onboarding-and-retention, class-schedule-and-instructor-utilization, ancillary-revenue-mix.
- **Knowledge bank** — [`fitness-studio-decision-trees.md`](knowledge/fitness-studio-decision-trees.md) (4 Mermaid trees: churn-save triage, membership pricing/tier model, schedule the class grid on fill, instructor pay model) + [`fitness-studio-reference-2026.md`](knowledge/fitness-studio-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — studio KPI dashboard, retention playbook.
- **2 commands** — `/build-retention-plan`, `/optimize-class-grid`.

## Seams

Retail-attach mechanics → [`retail-store-operations`](../retail-store-operations/) · café / food-service P&L → [`restaurant-operations`](../restaurant-operations/) · instructor staffing & pay → [`people-operations-hr`](../people-operations-hr/) · comparable membership-service ops → [`hotel-hospitality-operations`](../hotel-hospitality-operations/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install fitness-studio-gym-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
