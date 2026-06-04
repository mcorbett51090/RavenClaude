# Architecture & AEC — Claude Code plugin

A practice-and-project team for an architect or small AEC firm — it manages the project through the design phases on a fee that matches the effort, controls scope and the change/RFI load that erodes margin, reads construction documents for coordination and constructability, and reads the firm P&L on utilization and net multiplier the way a principal who bills time must.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
architecture & aec depth on top.

## What it does

Manages projects through the AIA phases against a phase-loaded fee, controls scope creep and RFIs/change orders, supports drawing-set coordination and constructability review, and reads the firm on utilization and net multiplier. Produces fee proposals, phase plans, and practice scorecards a firm acts on.

## Agents

- **`aec-engagement-lead`** — The engagement — scoping the project/practice problem, framing the read, routing, and synthesizing a plan.
- **`design-architect`** — Design phases — the design-phase progression, scope/options control, and phase-gate discipline, as decision-support.
- **`construction-documents-specialist`** — Documents — drawing-set coordination, constructability, RFIs/change orders, and CA support, as decision-support.
- **`aec-project-analyst`** — The numbers — phase-loaded fees, project cost-vs-fee, utilization, net multiplier, and the scorecard.

## Skills

- **`phase-load-the-fee`** — Build a fee that matches the effort curve across the design phases, not a flat percentage, so the heavy phases aren't underwater. Reach for this on any fee proposal.
- **`control-scope-creep`** — Distinguish in-scope iteration from additional services and authorize the difference, so unbilled changes don't erode the fee. Reach for this when the design keeps changing.
- **`coordinate-the-set`** — Read the drawing set for cross-discipline coordination and constructability, since a coordinated set beats a beautiful one. Reach for this in CD.
- **`read-rfi-pattern`** — Read the RFI and change-order pattern as a coordination signal to improve the next set, not just process this one. Reach for this when RFIs are high.
- **`read-firm-economics`** — Read utilization and net multiplier to separate a busy firm from a profitable one. Reach for this on a practice-health question.

## Slash commands

- **`/architecture-aec:phase-load-the-fee`** — Phase-load the fee
- **`/architecture-aec:control-scope-creep`** — Control scope creep
- **`/architecture-aec:coordinate-the-drawing-set`** — Coordinate the drawing set
- **`/architecture-aec:read-the-rfi-change-pattern`** — Read the RFI/change pattern
- **`/architecture-aec:read-firm-economics`** — Read firm economics

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install architecture-aec@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not CAD/BIM software, a code-compliance authority, or a licensed engineering stamp — code, structural, and life-safety determinations route to the licensed architect/engineer of record. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
