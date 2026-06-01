# Status leads with the narrative — and the colour never contradicts the numbers

**Status:** Pattern — strong default for every status update, RAG, and steering pack; deviate only with a written reason.

**Domain:** Project management / reporting

**Applies to:** `project-management`

---

## Why this exists

Two failure modes kill status reporting. The first is **table-first**: a wall of numbers the executive has to decode, with no statement of what changed or what they must do. The second, more dangerous, is **the lying RAG**: a green status sitting on top of a schedule-performance index of 0.7 or an unmitigated high risk — the colour and the numbers disagree, and the reader trusts the colour. A status report exists to drive a decision, not to look reassuring.

## How to apply

- **Narrative first.** Open with a plain-English executive summary: what changed since last period, what it means, and what (if anything) the reader must decide or do. The tables are the appendix, not the headline.
- **The RAG states the why.** "Amber — the gateway dependency slipped a week, pushing the integration milestone; recovery options below." Never a bare colour.
- **Colour must match the numbers.** If earned value (SPI/CPI) or the risk register says the project is in trouble, the status cannot be green. If they disagree, fix the colour or fix the underlying number — don't ship the contradiction. Route back to `delivery-lead` / `risk-and-raid-analyst` if the numbers need to change.
- **One source of truth.** Pull figures from the delivery-lead's EV and the risk-analyst's register; never restate a number that drifts from its source.
- **Audience-tuned cadence + depth.** Manage-closely stakeholders get the steering cadence and detail; keep-informed get a lighter touch. The comms plan names the cadence, channel, and single sender per audience.
- **Escalations are decision requests:** issue → impact → options → recommendation → decision needed by-when → distribution.

**Do:** lead with the narrative + the ask; make the RAG explain itself; keep colour consistent with EV/risk; cite the source figures; tune depth to the audience.

**Don't:** open with a table; ship a bare colour; let green contradict a red SPI or an open high risk; restate drifting numbers; send the same depth to everyone.

## Edge cases / when the rule does NOT apply

A purely **informational** broadcast with no decision and no health signal can be lighter (still narrative-first, but no RAG/ask). A real-time **agile** board (burndown/burnup) is a live artifact, not a periodic status — its "narrative" is the sprint review. Confidential figures are scrubbed per the owning domain's rules before any external distribution.

## See also

- [`../agents/stakeholder-comms-lead.md`](../agents/stakeholder-comms-lead.md) — owns status/steering/escalation packaging.
- [`./commitments-have-one-owner-and-one-date.md`](./commitments-have-one-owner-and-one-date.md) — every escalation's "decision needed" carries an owner + by-when.
- [`../../ravenclaude-core/agents/documentarian.md`](../../ravenclaude-core/agents/documentarian.md) — polish for partner/board-facing prose.

## Provenance

Authored with the `project-management` plugin (2026-06-01). Mirrors the "numbers don't ship without commentary" + "narrative-first board pack" disciplines already in the `finance` plugin's house opinions, generalized to project status.

---

_Last reviewed: 2026-06-01 by `claude`_
