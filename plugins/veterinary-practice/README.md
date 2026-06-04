# Veterinary Practice — Claude Code plugin

A clinical-and-practice-management team for a veterinary hospital owner or medical director — it builds standardized care protocols, runs the practice on production and ACT (average client transaction), manages the appointment-and-doctor capacity that gates revenue, and frames the independent-vs-corporate position in a fast-consolidating market.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
veterinary practice depth on top.

## What it does

Standardizes clinical protocols to reduce variation, instruments production per DVM and ACT, manages schedule capacity and the doctor-to-support-staff ratio, and reads the practice's economics against a market where corporate chains held ~41% of 2025 revenue. Produces protocol packs, practice scorecards, and capacity plans an owner acts on.

## Agents

- **`vet-practice-lead`** — The engagement — scoping the owner's problem, framing the read, routing to a specialist, and synthesizing an action plan.
- **`clinical-protocol-specialist`** — Standardized care — protocol design, recommended-care compliance, and reducing unwarranted clinical variation as decision-support.
- **`practice-operations-manager`** — Capacity and the floor — appointment templates, doctor-to-support ratio, schedule utilization, and staff retention.
- **`vet-finance-analyst`** — The economics — production/ACT analytics, the P&L, fee-schedule repricing, and the practice scorecard.

## Skills

- **`instrument-production-and-act`** — Read practice revenue as production per DVM and average client transaction × visits, never one alone, so a revenue problem is diagnosed correctly. Reach for this on any revenue question.
- **`design-care-protocol`** — Build an evidence-aligned, standardized care protocol as decision-support for the licensed DVM, to reduce unwarranted variation. Reach for this on a common presentation worked up inconsistently.
- **`unlock-schedule-capacity`** — Find the doctor bottleneck and fix the appointment template so a fully-booked practice can grow throughput. Reach for this when revenue is flat despite full demand.
- **`lift-care-compliance`** — Read recommended-care acceptance as a communication metric and raise it, instead of treating it as fixed demand. Reach for this when acceptance of dentals/diagnostics/preventives is low.
- **`reprice-the-fee-schedule`** — Reprice fees from the cost-of-service stack and medical value, not the neighbor's prices, to recover margin without losing position. Reach for this when margin erodes despite volume.

## Slash commands

- **`/veterinary-practice:instrument-production-and-act`** — Instrument production and ACT
- **`/veterinary-practice:design-a-care-protocol`** — Design a care protocol
- **`/veterinary-practice:unlock-schedule-capacity`** — Unlock schedule capacity

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install veterinary-practice@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a substitute for licensed veterinary judgment, a PIMS, or a pharmacy authority — clinical protocols are decision-support for a licensed DVM, never a treatment order. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
