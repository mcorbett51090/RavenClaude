---
name: status-and-steering-pack
description: Package delivery + risk data into audience-ready communication — a narrative-first status (RAG that explains itself and never contradicts the numbers), a steering-committee pack, and an escalation memo that is a decision request. Reach for this for recurring status, an exec/board update, or an escalation under pressure. Used by `stakeholder-comms-lead` (primary).
---

# Skill: status-and-steering-pack

**Purpose:** Turn the delivery-lead's earned-value status and the risk-analyst's register into communication that drives a decision — not a wall of tables. Used by `stakeholder-comms-lead`.

## When to use

- Recurring project status (weekly / fortnightly).
- A monthly/quarterly steering-committee or board pack.
- An escalation that needs a sponsor decision.
- Setting up a stakeholder register + comms cadence for a new project.

## The procedure

1. **Map stakeholders first** (power/interest): *manage-closely* (high/high) gets the steering cadence + detail; *keep-satisfied*, *keep-informed*, *monitor* each get their own depth. The comms plan names, per audience, the **message, channel, cadence, and single sender**.
2. **Narrative first.** Open with a plain-English executive summary: what changed, what it means, what the reader must decide/do. Tables are the appendix.
3. **The RAG explains itself** — "Amber: the gateway dependency slipped a week, pushing the integration milestone; recovery options below." Never a bare colour.
4. **Colour matches the numbers.** Green cannot sit on a SPI < 1 or an open high risk. If they disagree, fix the colour or fix the number — route back to `delivery-lead` / `risk-and-raid-analyst`; don't ship the contradiction.
5. **Single source of truth** — pull figures from the delivery-lead's EV and the risk register; never restate a number that drifts from its source.
6. **Escalations are decision requests:** issue → impact → options → recommendation → **decision needed by-when** → distribution.

## Anti-patterns this skill prevents

- A status/pack that opens with a table; a bare RAG colour; green over a red SPI.
- A comms plan with no cadence / channel / single sender per audience.
- An escalation with no explicit decision-needed + by-when.
- Restating figures that have drifted; same depth to every stakeholder.

## Output

A status report, steering-pack outline (see [`../../templates/steering-pack-outline.md`](../../templates/steering-pack-outline.md)), or escalation memo. End with the `stakeholder-comms-lead` Output Contract block; route partner/board-facing prose polish to `ravenclaude-core/documentarian` and any PII handling to `ravenclaude-core/security-reviewer`.
