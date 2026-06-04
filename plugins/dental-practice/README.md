# Dental Practice — Claude Code plugin

A treatment-planning-and-revenue-cycle team for a dental practice owner — it controls overhead against the ~62% median, holds collections above 98%, builds case acceptance on the treatment plan rather than the discount, and reads doctor/hygiene production per hour the way a practice that runs on the schedule does.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
dental practice depth on top.

## What it does

Holds overhead to benchmark, protects the collection ratio, raises case acceptance through treatment-plan presentation, and instruments doctor and hygiene production per hour. Produces overhead reads, case-acceptance plans, and RCM scorecards an owner acts on.

## Agents

- **`dental-practice-lead`** — The engagement — scoping the owner's problem, framing the read, routing, and synthesizing an action plan.
- **`clinical-treatment-planner`** — Case acceptance — treatment-plan sequencing, presentation, and acceptance as decision-support for the dentist.
- **`dental-rcm-specialist`** — The revenue cycle — collection ratio, PPO write-offs and payer mix, A/R, and claims.
- **`dental-operations-analyst`** — The economics — overhead, production per hour, hygiene analytics, and the scorecard.

## Skills

- **`benchmark-overhead`** — Read overhead as a % of collections against the ~62% median before cutting any single cost, so the diagnosis targets the real driver. Reach for this on a margin problem.
- **`protect-the-collection-ratio`** — Read banked-vs-produced dollars and recover the collection ratio toward 98%+, so production becomes income. Reach for this when collections slip.
- **`lift-case-acceptance`** — Raise treatment-plan acceptance through presentation and sequencing rather than discounting. Reach for this when big plans don't close.
- **`read-production-per-hour`** — Read doctor and hygiene production per hour, not per day, to expose the real capacity story. Reach for this on a production question.
- **`manage-the-payer-mix`** — Read the effective fee by plan and manage PPO write-offs as a deliberate strategy, not an accident. Reach for this when adjustments erode margin.

## Slash commands

- **`/dental-practice:benchmark-overhead`** — Benchmark overhead
- **`/dental-practice:protect-the-collection-ratio`** — Protect the collection ratio
- **`/dental-practice:lift-case-acceptance`** — Lift case acceptance
- **`/dental-practice:read-production-per-hour`** — Read production per hour
- **`/dental-practice:manage-the-ppo-payer-mix`** — Manage the PPO payer mix

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install dental-practice@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a substitute for clinical dental judgment, a practice-management system, or a coding authority — treatment planning is decision-support for a licensed dentist. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
