# franchise-operations

**Franchise operations team** for the two halves of a franchise business: the **system economics &
relationship** (should I buy/expand, what does the FDD really say, do the unit economics work after
fees) and **running the units** (multi-unit P&L, prime cost, brand standards, manager accountability).

> Business **decision-support**, NOT legal, financial, or investment advice. Binding FDD / franchise-
> agreement review routes to `legal-ops-clm`; deep model mechanics route to `finance`. Fees, Item-19
> figures, and disclosure specifics are per-FDD-edition, jurisdictional, and volatile — every one carries
> a retrieval date + `[verify-at-use]`. Inherits the `ravenclaude-core` constitution.

## Agents

| Agent | Owns | Spawn when |
|---|---|---|
| [`franchise-operations-strategist`](agents/franchise-operations-strategist.md) | FDD/Item-19 read, royalty/ad-fund/fee flows, royalty-loaded unit economics, the new-unit/expand go/no-go, the franchisor↔franchisee relationship | "Should I buy this franchise?"; "what does this Item 19 tell me?"; "make money after fees?"; "should I expand?" |
| [`multi-unit-performance-manager`](agents/multi-unit-performance-manager.md) | Multi-unit P&L, prime-cost control, brand-standard audits, manager scorecards, unit-variance ranking | "A location is losing money"; "labor and food costs too high"; "keep quality consistent"; "manage the managers" |

## Skills

- [`model-unit-economics`](skills/model-unit-economics/SKILL.md) — the royalty-loaded unit P&L + break-even + ramp.
- [`read-the-fdd`](skills/read-the-fdd/SKILL.md) — a decision-focused FDD read (literacy, not legal advice).
- [`run-brand-standard-audit`](skills/run-brand-standard-audit/SKILL.md) — a repeatable cross-unit audit + coaching loop.

## Knowledge bank

- [`knowledge/new-unit-decision-tree.md`](knowledge/new-unit-decision-tree.md) — the go/no-go tree + the fee stack.
- [`knowledge/franchise-economics-reference-2026.md`](knowledge/franchise-economics-reference-2026.md) — the FDD Items map + dated benchmarks.

## Boundaries (what routes elsewhere)

- **Binding FDD / franchise-agreement review, negotiation, enforceability** → `legal-ops-clm`.
- **Deep financial-model mechanics, projections, valuation** → `finance`.
- **Single-concept unit operations depth** → `restaurant-operations` / `retail-store-operations`.
- **Dispatch/field-service multi-site work** → `field-service-management`.

## Install

```
/plugin marketplace add ./
/plugin install franchise-operations@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
