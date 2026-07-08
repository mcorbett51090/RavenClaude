# chiropractic-practice

**Chiropractic practice operations & compliance team** — two agents covering the two engines of a
doctor-of-chiropractic office: **running the practice** (capacity, care plans, the cash/wellness model,
retention) and **coding it defensibly** (CMT/E&M, medical necessity, the active-vs-maintenance line, ABN).

> Operations & coding **decision-support**, NOT medical, legal, or billing advice, and NOT a coding
> certification. No PHI/PII. Scope, coverage, and coding rules are state- and payer-specific and volatile
> — every specific carries a retrieval date + `[verify-at-use]` and is flagged for a licensed professional.
> Inherits the `ravenclaude-core` constitution.

## Agents

| Agent | Owns | Spawn when |
|---|---|---|
| [`chiropractic-practice-lead`](agents/chiropractic-practice-lead.md) | Capacity & scheduling to the care plan, the cash/insurance/wellness-plan model, membership pricing, PVA & plan-completion retention | "Structure this care plan"; "price a wellness membership"; "patients drop off"; "chasing balances after the visit" |
| [`chiro-billing-compliance-specialist`](agents/chiro-billing-compliance-specialist.md) | CMT vs E&M by region, documented medical necessity via the PART exam, the active-vs-maintenance plateau call, ABN workflow, audit-defensible notes | "Which code?"; "document medical necessity"; "active care or maintenance?"; "do I need an ABN?" |

## Skills

- [`design-care-plan-and-cadence`](skills/design-care-plan-and-cadence/SKILL.md) — a phased, defensible care plan with re-exam checkpoints.
- [`code-and-document-the-visit`](skills/code-and-document-the-visit/SKILL.md) — CMT/E&M code + PART-based necessity note.
- [`build-cash-and-wellness-plan-model`](skills/build-cash-and-wellness-plan-model/SKILL.md) — a compliant, cost-covering membership model.

## Knowledge bank

- [`knowledge/billing-and-medical-necessity-decision-tree.md`](knowledge/billing-and-medical-necessity-decision-tree.md) — active vs maintenance, region-based CMT, PART, ABN.
- [`knowledge/chiro-payer-and-coding-reference-2026.md`](knowledge/chiro-payer-and-coding-reference-2026.md) — dated coding/payer reference + operating benchmarks.

## Boundaries (what routes elsewhere)

- **Deep denials / AR / full revenue-cycle** → `medical-revenue-cycle`.
- **Different clinical/billing model (timed CPT, 8-minute rule)** → `physical-therapy-rehab-clinic`.
- **A live audit response or a licensure/legal question** → a certified coder / counsel (this plugin is decision-support only).

## Install

```
/plugin marketplace add ./
/plugin install chiropractic-practice@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
