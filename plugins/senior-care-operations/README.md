# Senior Care Operations — Claude Code plugin

An operations team for an assisted-living, memory-care, or home-care operator — it manages census and occupancy as the revenue engine, prices to acuity rather than a flat rate, staffs to acuity-based hours-per-resident-day, and reads quality and compliance as the license-and-reputation risk that a community runs on.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
senior care operations depth on top.

## What it does

Manages census/occupancy and move-in/move-out flow, prices to acuity, staffs to acuity-based PPD/hours-per-resident-day, and reads quality/compliance as operational risk. Produces census plans, acuity-based staffing models, and operations scorecards an operator acts on.

## Agents

- **`senior-care-lead`** — The engagement — scoping the operator's problem, framing the read, routing, and synthesizing an action plan.
- **`clinical-care-compliance-specialist`** — Quality and compliance — survey readiness, incident/fall patterns, quality measures, and acuity assessment, as decision-support.
- **`census-occupancy-strategist`** — Census — the sales funnel, move-in/move-out flow, length of stay, and occupancy.
- **`senior-care-finance-analyst`** — The numbers — acuity-based pricing, hours-per-resident-day staffing, labor/turnover cost, and the scorecard.

## Skills

- **`manage-census-flow`** — Read census as a flow of move-ins, move-outs, and length of stay, not a point number, so the right lever is pulled. Reach for this on any occupancy question.
- **`price-to-acuity`** — Build acuity-based pricing that captures the care cost by level, instead of a flat rate, to protect margin. Reach for this on a pricing question.
- **`staff-to-acuity-ppd`** — Build a staffing model on acuity-weighted hours-per-resident-day, not a fixed ratio, so labor matches need. Reach for this on a labor question.
- **`read-quality-and-compliance`** — Read survey readiness, incidents/falls, and quality measures as existential operational risk, as decision-support. Reach for this on a quality question.
- **`quantify-labor-and-turnover`** — Read labor cost, agency reliance, and turnover as quantified unit economics, since they drive both margin and quality. Reach for this on a cost question.

## Slash commands

- **`/senior-care-operations:manage-census-flow`** — Manage census flow
- **`/senior-care-operations:price-to-acuity`** — Price to acuity
- **`/senior-care-operations:staff-to-acuity-based-ppd`** — Staff to acuity-based PPD
- **`/senior-care-operations:read-quality-and-compliance`** — Read quality and compliance
- **`/senior-care-operations:quantify-labor-and-turnover`** — Quantify labor and turnover

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install senior-care-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not an EHR/care-management system, a clinical authority, or a licensing/survey authority — care plans, clinical decisions, and regulatory determinations route to licensed clinicians and the state survey agency. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
