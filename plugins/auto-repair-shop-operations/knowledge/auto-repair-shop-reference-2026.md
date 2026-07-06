# Auto-Repair Shop — 2026 Reference

> Dated reference for the `auto-repair-shop-operations` team: the fixed-ops concepts that drive a repair shop and the benchmarks agents reach for. The durable reasoning lives in [`auto-repair-shop-decision-trees.md`](auto-repair-shop-decision-trees.md); this file is the freshness-anchored "what the numbers and norms are."
>
> **Operations/financial decision-support — not legal, tax, or OEM-warranty-policy advice.** Every labor-rate norm, productivity/efficiency/proficiency target, and parts-margin figure below is **volatile and market-, shop-, and vehicle-mix-specific**. Each row carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the shop's own books, the current labor guide, or the local statute before it drives a price, a target, or a pay plan. No customer PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Labor economics — the core distinction

| Concept | What it is | Why it matters | Source / retrieved | Flag |
|---|---|---|---|---|
| Door / posted labor rate | The advertised hourly rate | A ceiling, not what you collect | _<source placeholder — shop's posted rate>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Effective labor rate (ELR) | Labor $ collected / billed hours | The **real** price after erosion | _<source placeholder — shop P&L>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Billed / flagged hours | Labor-guide time sold on the RO | The labor-GP input | _<source placeholder — labor guide>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Warranty labor rate | Reimbursement rate on warranty work | Often below door rate; erodes ELR | _<source placeholder — warranty policy>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> **Durable rule:** read profitability on the ELR, never the door rate. The gap between them is recoverable margin — see the pricing decision tree.

---

## 2. Productivity / efficiency / proficiency benchmarks `[ESTIMATE]`

| Dial | Formula (concept) | Reference direction `[ESTIMATE]` | Source / retrieved | Flag |
|---|---|---|---|---|
| Productivity | clocked / available hours | Higher is better; low = idle/dispatch/car-count gap | _<source placeholder — industry benchmark>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Efficiency | billed / clocked hours | Above 100% means beating flag time; the labor-GP multiplier | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Proficiency | billed / actual hours | True speed vs the guide; training/tooling signal | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Comeback rate | comeback ROs / total ROs | Lower is better; a direct tax on labor GP | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> These are planning anchors and directional, **not quotable facts**. Confirm the current benchmark and the shop's own baseline before setting a target with an owner. Actual healthy ranges vary widely by shop type (general repair vs specialty vs quick-lube), vehicle mix, and pay plan.

---

## 3. Parts gross-profit matrix (concept)

A **parts matrix** prices parts by cost tier so low-cost parts carry a higher markup percentage than high-cost parts (a flat percentage over-prices expensive parts and under-earns on cheap ones). The tiers and percentages are a **shop decision**, set once and then managed — not a default from the parts vendor.

| Cost tier (concept) | Markup direction `[ESTIMATE]` | Source / retrieved | Flag |
|---|---|---|---|
| Low-cost parts | Higher markup % (protects margin on small tickets) | _<source placeholder — shop matrix>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Mid-cost parts | Moderate markup % | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| High-cost parts | Lower markup % (keeps the ticket competitive) | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Sublet / tires / batteries | Category-specific handling | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> **Durable rule:** set the matrix deliberately to a target blended parts GP%, then review it periodically against cost changes — don't let the vendor's list price set your margin. Actual tier breakpoints and percentages are `[verify-at-use]`.

---

## 4. State / regulatory specifics (never assume)

| Topic | Note | Source / retrieved | Flag |
|---|---|---|---|
| Written-estimate / authorization rules | Many states require a written estimate and authorization before work, plus disclosure to exceed it | _<source placeholder — state statute>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Diagnostic-fee disclosure | Rules on disclosing diagnostic/teardown fees vary | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Return of old parts | Some jurisdictions require offering the customer their old parts | _<source placeholder>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> These are **jurisdiction-specific and change** — always confirm against the current local statute; flag to the owner for legal review when a gate depends on it.

---

## 5. How to use this file

1. Find the concept/benchmark/rule you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs a target or a customer-facing number.
4. For anything that drives a price, a pay plan, or a customer estimate: confirm against the shop's own numbers, the current labor guide, or the local statute first.

---

## See also

- [`auto-repair-shop-decision-trees.md`](auto-repair-shop-decision-trees.md) — the durable pricing / comeback / declined-work / pay-plan trees.
- Adjacent (distinct) models: [`../../automotive-dealership/CLAUDE.md`](../../automotive-dealership/CLAUDE.md), [`../../fleet-logistics/CLAUDE.md`](../../fleet-logistics/CLAUDE.md), [`../../skilled-trades-contracting/CLAUDE.md`](../../skilled-trades-contracting/CLAUDE.md).
