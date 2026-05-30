# Pick the lowest-tier mechanism for a derived value: formula/calculated → rollup → plug-in → flow

**Status:** Pattern — strong default; climb the tiers only when the lower one can't express the requirement.

**Domain:** Dataverse / Data modeling

**Applies to:** `power-platform`

---

## Why this exists

"Store a derived value" has four very different implementations with very different costs, and choosing by habit produces either fragile chains or needless code. A **formula/calculated column** computes **same-record** values **synchronously, on read** — instant, no storage, but it can only see fields on its own row (and a formula column can't even reference a related table). A **rollup column** aggregates **child rows** (SUM/COUNT/MIN/MAX) but is **not real-time**: it refreshes on a system async job (hourly by default, or on-demand), so it's wrong whenever the parent must reflect children *immediately*. A **plug-in** can do anything — cross-table aggregation that must be instant, side effects, external calls — at the cost of C#, registration, and (if synchronous) added write latency. A **flow** handles async, connector-driven, or long-running derivations but adds licensing and run-history surface. The §3 #7 house rule — *lowest-tier mechanism that does the job* — exists because each tier up is materially more expensive to build, test, and maintain. The specific trap to avoid: chaining a formula → calculated → rollup, which is recursion-fragile and miserable to debug.

## How to apply

Walk up only as far as the requirement forces you:

```text
Same record, simple math/text/conditional, needed instantly?     → FORMULA / CALCULATED column
Aggregate of CHILD rows (SUM/COUNT/MIN/MAX), eventual is OK?      → ROLLUP column (async refresh)
Aggregate of children that must be EXACT the instant it changes,  → PLUG-IN (PostOperation on the
   or cross-table logic with side effects / transactional?           child; sync if it must roll back)
Async, connector-driven, external API, scheduled, or long-running? → FLOW (Power Automate)
```

```text
// FORMULA column — same-record, synchronous, no storage. Power Fx, same row only.
cnt_quantity * cnt_unitprice
If(cnt_duedate < Now(), "Overdue", "On Track")

// ROLLUP column — child aggregation, ASYNC (hourly job / on-demand recalc). NOT real-time.
SUM of cnt_orderline.cnt_lineamount WHERE statecode = Active

// PLUG-IN — real-time child aggregation that must be exact on every child change.
// Register: PostOperation, sync, on Create/Update/Delete of the CHILD; recompute parent total.
```

| Mechanism | Scope | Timing | Cost | Use when |
|---|---|---|---|---|
| **Formula / calculated column** | Same record only | Synchronous (on read) | Lowest — metadata only | Concatenation, arithmetic, conditional on the row's own fields |
| **Rollup column** | Parent ← child aggregate | **Async** (hourly/on-demand) | Low | SUM/COUNT/MIN/MAX of children where "eventually correct" is acceptable |
| **Plug-in** | Anything (cross-table, side effects) | Synchronous or async | High (C# + registration) | Real-time parent total, transactional logic, multi-table writes |
| **Flow** | Anything connector-reachable | Async (trigger/schedule) | Medium (+ licensing) | External calls, scheduled recompute, approvals, long-running |

**Do:**
- Use a **formula/calculated column** for any same-record derivation — it's free, synchronous, and storage-less.
- Use a **rollup** for child aggregates where eventual consistency is fine (dashboards, reporting totals). Trigger an on-demand recalc if a user needs it fresh now.
- Reach for a **plug-in** only when the aggregate must be exact at the instant a child changes, or the logic is transactional/cross-table — register it **PostOperation on the child**.
- Prefer a **flow** over a plug-in when the work is async and connector-shaped (house rule §3 #7: flow before plug-in).

**Don't:**
- Chain **formula → calculated → rollup** — recursion-fragile and hard to debug; collapse it into one mechanism or a plug-in.
- Use a **rollup** where the parent must reflect the child *immediately* — it won't; the async job lag will read as a "wrong total" bug.
- Put a **multi-select choice, related-table reference, or another rollup** inside a formula column — unsupported; formula columns are same-record-only.
- Write a **plug-in** for something a rollup or formula already does — that's climbing two tiers for no requirement.

## Edge cases / when the rule does NOT apply

- **Rollups can't aggregate across an N:N** or over multi-select choices, and have hierarchy limits — those genuinely require a plug-in or scheduled flow.
- A **calculated column referencing another calculated column** is allowed but compounds staleness/recursion risk — keep the chain flat.
- A rollup's **on-demand recalc** (the manual refresh button / `CalculateRollupField` action) bridges *some* "needs it now" cases without a plug-in — try that before writing code.
- **Formula vs calculated** differ in null handling (formula treats null as 0/empty; calculated does not) and in function set — pick deliberately if null semantics matter.
- If the derivation feeds **Power BI**, compute it as a **measure** in the semantic model instead of materializing it in Dataverse (see `bi-measures-not-calculated-columns.md`).

## See also

- [`../skills/dataverse-web-api/resources/formula-columns.md`](../skills/dataverse-web-api/resources/formula-columns.md) — formula limits (same-record only, 1000-char, no cyclic refs) and the "When to Use What" table
- [`../skills/dataverse-plugins/resources/common-patterns.md`](../skills/dataverse-plugins/resources/common-patterns.md) — the cascade-aggregate plug-in reference implementation
- [`./dataverse-plugin-pipeline-stage-selection.md`](./dataverse-plugin-pipeline-stage-selection.md) — if it must be a plug-in, which stage/mode
- [`./dataverse-avoid-cascade-on-high-volume-child.md`](./dataverse-avoid-cascade-on-high-volume-child.md) — don't abuse cascade to maintain a parent aggregate
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Derived values — rollup vs calculated vs plug-in vs flow`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; flags the formula→calculated→rollup chain anti-pattern

## Provenance

Grounded in `skills/dataverse-web-api/resources/formula-columns.md` (same-record-only constraint, the "When to Use What" routing table, null-handling difference), the `dataverse-plugins` skill (PostOperation child-aggregate pattern), the platform-wide house rule §3 #7 ("lowest-tier mechanism … Business rule before JavaScript. Power Fx before flow. Flow before plug-in"), and the `dataverse-architect` anti-pattern "A formula column referencing a calculated column referencing a rollup — recursion fragility." Rollup async-refresh cadence (hourly default / on-demand) is the documented Dataverse behavior — verify current cadence against Microsoft Learn before quoting an SLA.

---

_Last reviewed: 2026-05-30 by `claude`_
