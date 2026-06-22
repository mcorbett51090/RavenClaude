# Nonprofit Fundraising — Claude Code plugin

A development team for a nonprofit fundraiser or executive director — it protects donor retention (the cheapest dollar a nonprofit has, at ~$0.20 to keep vs ~$1.50 to acquire), builds the grant pipeline on fit before effort, segments the donor base by value and recency, and reads cost-to-raise-a-dollar honestly across channels.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
nonprofit fundraising depth on top.

## What it does

Holds donor retention as the master efficiency number, qualifies grants on funder fit before writing, segments donors by value/recency/engagement, and reads cost-per-dollar-raised by channel. Produces grant proposals, major-gift cultivation plans, and development scorecards a fundraiser acts on.

## Agents

- **`development-lead`** — The engagement — scoping the development problem, framing the plan, routing, and synthesizing a fundraising strategy.
- **`grant-writer`** — Grants — funder-fit qualification, proposal design, logic models, and the grant pipeline.
- **`major-gifts-strategist`** — Major gifts and donors — segmentation, the cultivation cycle, moves management, and stewardship.
- **`nonprofit-finance-analyst`** — The numbers — retention, cost-per-dollar by channel, the restricted/unrestricted mix, and the development scorecard.

## Skills

- **`protect-donor-retention`** — Read donor retention by cohort and fix the leaky bucket before pouring in acquisition, since retention is ~7x cheaper than acquisition. Reach for this on any growth question.
- **`qualify-the-funder`** — Score a grant opportunity on funder fit before writing, so effort goes where alignment is. Reach for this before any proposal.
- **`run-the-cultivation-cycle`** — Move a donor through identification, qualification, cultivation, solicitation, and stewardship rather than jumping to the ask. Reach for this on a major-gift prospect.
- **`segment-the-donor-base`** — Segment donors by value, recency, and engagement (RFM-style) to direct cultivation hours where they pay. Reach for this when cultivation is spread thin.
- **`read-cost-per-dollar`** — Compute cost-to-raise-a-dollar per channel, never blended, so the subsidizing channel is visible. Reach for this on a portfolio/efficiency question.
- **`grant-postaward-compliance`** — Manage a grant *after* the award: set up, spend only on allowable/allocable/reasonable costs, track budget-vs-actual monthly, report on cadence, stay audit-ready through close-out. Reach for this once a grant is won (the post-award/compliance side).

## Slash commands

- **`/nonprofit-fundraising:protect-donor-retention`** — Protect donor retention
- **`/nonprofit-fundraising:qualify-the-funder`** — Qualify the funder
- **`/nonprofit-fundraising:run-the-cultivation-cycle`** — Run the cultivation cycle
- **`/nonprofit-fundraising:segment-the-donor-base`** — Segment the donor base
- **`/nonprofit-fundraising:read-cost-per-dollar-by-channel`** — Read cost-per-dollar by channel

## Knowledge bank

5 research-grounded reference docs under [`knowledge/`](knowledge/) — covering both the pre-award development side and the post-award / grant-compliance side ([`grant-management-post-award.md`](knowledge/grant-management-post-award.md)). Figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, regulatory specifics carry `[verify-at-use]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install nonprofit-fundraising@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a CRM/donor database, an accounting system, or a legal/tax authority on charitable giving — gift-acceptance and tax questions route to counsel. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
