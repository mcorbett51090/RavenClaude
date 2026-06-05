# Small-Firm Legal Practice — Claude Code plugin

A practice-operations team for a solo or small-firm attorney — it manages matters on realization and the billable-vs-collected gap, drafts and reviews documents as attorney decision-support, runs intake on conflict and fit before the engagement, and reads the practice P&L the way a lawyer who is also the rainmaker and the COO must.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
small-firm legal practice depth on top.

## What it does

Manages matters on realization/utilization, supports drafting and document review as attorney work-product (never legal advice or representation), runs conflict-checked intake, and reads the practice's collected-revenue economics. Produces matter plans, drafting support, and practice scorecards an attorney acts on.

## Agents

- **`legal-engagement-lead`** — The engagement — scoping the practice problem, framing the read, routing, and synthesizing an action plan.
- **`litigation-specialist`** — Litigation matters — case planning, document/discovery support, deadlines, and matter budgeting, as attorney work product.
- **`contracts-drafting-specialist`** — Transactional drafting — document drafting and review, clause libraries, and redlines, as attorney work product.
- **`legal-operations-analyst`** — The numbers — realization, utilization, the practice P&L, intake/conflict process, and the scorecard.

## Skills

- **`read-realization`** — Read realization and the billed-vs-collected gap, locating write-downs, write-offs, and A/R, so the practice's real economics are visible. Reach for this on any 'busy but broke' question.
- **`run-conflict-checked-intake`** — Run intake as risk management — conflict check and fit/viability screen before the engagement — to prevent the matters that destroy realization. Reach for this at every new matter.
- **`support-drafting`** — Draft and review documents from clause libraries with issue flags, as attorney-reviewed work product, never legal advice. Reach for this on a drafting or review task.
- **`scope-the-matter`** — Scope a matter and choose the fee structure deliberately, since an open-ended hourly with no budget breeds write-offs. Reach for this before engaging.
- **`build-practice-scorecard`** — Build a realization-led practice scorecard with utilization, collected revenue, and A/R, each defined and baselined. Reach for this to instrument the practice.

## Slash commands

- **`/legal-small-firm:read-realization`** — Read realization
- **`/legal-small-firm:run-conflict-checked-intake`** — Run conflict-checked intake
- **`/legal-small-firm:support-drafting-as-work-product`** — Support drafting as work product
- **`/legal-small-firm:scope-the-matter-and-fee`** — Scope the matter and fee
- **`/legal-small-firm:build-a-practice-scorecard`** — Build a practice scorecard

## Knowledge bank

5 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]` / `[verify-at-use]`, and anything from training knowledge is marked `[unverified — training knowledge]`. Includes two **Mermaid** decision-tree files: the consolidated [`legal-practice-decision-trees.md`](knowledge/legal-practice-decision-trees.md) (fee structure / A/R collection / billing-rate review) and the net-new [`legal-intake-and-trust-decision-trees.md`](knowledge/legal-intake-and-trust-decision-trees.md) (conflict-checked intake / IOLTA three-way reconciliation).

## Scenarios bank & calculator

- **Scenarios** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified engagement narratives (realization-rate recovery, intake conflict/fit miss, IOLTA three-way reconciliation gap, utilization/capacity squeeze). Surfaced only as a *secondary* source behind the mandatory unverified-scenario preamble (see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)); they carry no client confidences and are never legal advice.
- **Calculator** — [`scripts/legal_calc.py`](scripts/legal_calc.py) (stdlib only, Python 3.8+): `realization` (the cascade + effective hourly rate), `matter-profit` (profitability vs the Rule of Thirds), `utilization` (billable ratio + non-billable split), `trust-recon` (three-way IOLTA reconciliation check). Decision-support, **not** legal/ethics/financial advice — a `trust-recon` FAIL is an arithmetic flag to route to the attorney, never a finding of misconduct.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install legal-small-firm@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a practice-management/case system, and it does not practice law, give legal advice, form an attorney-client relationship, or substitute for a licensed attorney's judgment — all work product is attorney-reviewed decision-support. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
