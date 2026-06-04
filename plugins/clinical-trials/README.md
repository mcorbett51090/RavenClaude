# Clinical Trials — Claude Code plugin

A clinical-operations team for a sponsor, CRO, or site network — it designs feasible protocols (because eligibility criteria drive the enrollment failure that hits two-thirds of sites), plans patient recruitment against a ~$6,533 per-patient cost (and ~$19,533 to replace), manages site activation and the ~30% dropout, and frames the regulatory submission the way a study where 80% run late demands.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
clinical trials depth on top.

## What it does

Stress-tests protocol feasibility against enrollment risk, plans recruitment and retention against per-patient economics, sequences site activation and monitoring, and structures the regulatory submission. Produces feasibility assessments, recruitment plans, and submission-readiness reads a clinical-operations leader acts on.

## Agents

- **`trials-engagement-lead`** — The engagement — scoping the trial-ops question, framing the read, routing, and synthesizing an operational plan.
- **`protocol-design-specialist`** — Feasibility — eligibility criteria, enrollment risk, retention-by-design, and protocol operability, as decision-support.
- **`clinical-operations-manager`** — Execution — site activation, recruitment funnel, monitoring, and retention operations.
- **`regulatory-submissions-specialist`** — Submissions — regulatory documentation, eCTD structure, data quality, and submission readiness, as decision-support.

## Skills

- **`stress-test-feasibility`** — Stress-test eligibility criteria against the addressable population and site capacity before the protocol locks, since restrictive criteria are the biggest enrollment killer. Reach for this at design.
- **`plan-recruitment-funnel`** — Plan recruitment as a costed funnel with a cost per stage, against the per-patient economics, instead of a hope. Reach for this on any enrollment plan.
- **`accelerate-site-activation`** — Sequence site selection, contracting, and start-up as the schedule's critical path to cut the activation delay. Reach for this when sites are slow.
- **`design-for-retention`** — Build retention into visit burden, schedule, and engagement to lower the ~30% dropout, instead of re-recruiting. Reach for this when dropout threatens the timeline.
- **`read-submission-readiness`** — Read documentation completeness, data quality, and eCTD structure throughout the trial so the filing isn't a final-month scramble. Reach for this before a milestone.

## Slash commands

- **`/clinical-trials:stress-test-protocol-feasibility`** — Stress-test protocol feasibility
- **`/clinical-trials:plan-the-recruitment-funnel`** — Plan the recruitment funnel
- **`/clinical-trials:accelerate-site-activation`** — Accelerate site activation
- **`/clinical-trials:design-for-retention`** — Design for retention
- **`/clinical-trials:read-submission-readiness`** — Read submission readiness

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install clinical-trials@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not an EDC/CTMS, an IRB, or a medical/regulatory authority — protocol, safety, and submission decisions belong to qualified medical, regulatory, and ethics professionals. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
