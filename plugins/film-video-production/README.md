# Film & Video Production — Claude Code plugin

A production-management team for a producer, production company, or post house — it budgets to a defensible top-sheet, schedules to the shoot day rather than the calendar, runs the post pipeline as a dependency chain, and reads production economics the way a line producer who answers for every dollar on the day must.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
film & video production depth on top.

## What it does

Builds budgets to a top-sheet with contingency, schedules to shoot days and locations, sequences the post pipeline as a dependency chain, and reads production cost against the bid. Produces budgets, schedules, and post-pipeline plans a producer acts on.

## Agents

- **`production-lead`** — The engagement — scoping the project, framing the budget/schedule, routing, and synthesizing a production plan.
- **`line-producer`** — The day — the top-sheet budget, the shoot schedule, crew/gear/locations, and contingency.
- **`post-production-supervisor`** — Post — the post pipeline, picture lock, deliverables/specs, and the finishing dependency chain.
- **`production-finance-analyst`** — The numbers — cost-vs-bid, the cost report, contingency tracking, and the production scorecard.

## Skills

- **`build-the-top-sheet`** — Build the budget bottom-up to a top-sheet with a risk-sized contingency, so the number is defensible. Reach for this on any budget question.
- **`schedule-the-shoot`** — Schedule to shoot days, locations, and cast availability with company moves and turnaround, not the calendar. Reach for this on a scheduling question.
- **`sequence-the-post-pipeline`** — Sequence post as a dependency chain keyed off picture lock, so the delivery date rests on the critical path. Reach for this on a post plan.
- **`define-the-deliverables`** — Define the delivery spec (formats, masters, captions, QC) first, since it's the actual product. Reach for this before pricing or finishing.
- **`track-cost-vs-bid`** — Track cost against the bid line by line and watch contingency burn, so overage is managed not discovered. Reach for this during production.

## Slash commands

- **`/film-video-production:build-the-top-sheet-budget`** — Build the top-sheet budget
- **`/film-video-production:schedule-the-shoot`** — Schedule the shoot
- **`/film-video-production:sequence-the-post-pipeline`** — Sequence the post pipeline
- **`/film-video-production:define-the-deliverables`** — Define the deliverables
- **`/film-video-production:track-cost-vs-bid`** — Track cost vs bid

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install film-video-production@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not an NLE, a scheduling platform, or a union/legal authority — union rules, clearances, and contracts route to the relevant specialists and counsel. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
