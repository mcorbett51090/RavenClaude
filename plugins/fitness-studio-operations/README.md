# fitness-studio-operations

A RavenClaude plugin: a **fitness-studio operations** specialist team for running boutique fitness studios, gyms, and personal-training studios as businesses — the membership model, the retention engine, the class schedule, and the way you pay your staff — so the studio acquires members efficiently, keeps them, fills its schedule, and pays its team in a model that survives.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

## What it's for

Running the *business* of a studio: pricing and the membership model (drop-in, class packs, unlimited recurring billing, founding-member rates), the unit economics (revenue per member, LTV, CAC, payback), the retention/churn engine that actually determines whether the studio survives, the class schedule and capacity (utilization, waitlists, instructor mix), instructor/trainer pay (rev-share vs hourly vs per-head, and the practical 1099-vs-W2 line), the front desk and member experience, and retail/ancillary revenue. This is the **studio-ops craft** — distinct from the coaching/programming on the floor, the books, and the acquisition campaigns.

## Agents

| Agent | Use for |
|---|---|
| **fitness-studio-operations-lead** | Membership models + pricing, unit economics (LTV/CAC, revenue per member), front-desk & member experience, retail/ancillary revenue, the studio P&L view |
| **member-retention-analyst** | Churn math, at-risk detection, win-back, the retention economic engine, cohort/visit-frequency analysis |
| **class-and-instructor-ops-lead** | Class schedule & capacity (utilization, waitlists), instructor mix, pay models (rev-share/hourly/per-head), the 1099-vs-W2 flag, no-show/late-cancel policy |

## What's inside

- **5 skills** — design-membership-model, compute-studio-unit-economics, analyze-retention-and-churn, optimize-class-schedule, design-instructor-pay-model.
- **Knowledge bank** — [`fitness-studio-operations-decision-trees.md`](knowledge/fitness-studio-operations-decision-trees.md) (5 Mermaid trees: pricing-model, retention-intervention, capacity, pay-model, no-show) + [`fitness-studio-operations-reference-2026.md`](knowledge/fitness-studio-operations-reference-2026.md) (dated tooling/benchmark map).
- **7 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **3 templates** — membership model & pricing, retention dashboard, class schedule & pay plan.
- **3 commands** — `/design-membership`, `/retention-review`, `/schedule-audit`.
- **1 advisory hook** — `check-studio-anti-patterns.sh` (pricing doc with no churn/retention mention, schedule doc with no utilization mention, pay doc with no classification mention). `STUDIO_STRICT=1` to block.

## When to use vs adjacent plugins

| Use this plugin for | Use the other plugin for |
|---|---|
| The membership model, retention, schedule, pay model | The books, tax filing, sales-tax, the payroll run → [`accounting-bookkeeping`](../accounting-bookkeeping/) |
| CAC as a number to spend against | Acquisition campaigns, ad spend, the funnel → [`marketing-operations`](../marketing-operations/) |
| Flagging the 1099-vs-W2 question; designing the pay model | The binding worker-classification call, hiring, HR policy → [`people-operations-hr`](../people-operations-hr/) |

This plugin is **not** for coaching, workout programming, or exercise prescription — that's the floor craft, not studio operations.

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install fitness-studio-operations@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for routing rules, house opinions, and the output contract.
