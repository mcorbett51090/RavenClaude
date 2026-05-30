# Choose Flow vs Apex deliberately — one automation entry point per object

**Status:** Pattern — strong default; deviate only with a written reason in the design.

**Domain:** Declarative automation / automation density

**Applies to:** `salesforce`

---

## Why this exists

Two failure modes drive this rule. First, picking the wrong tool: simple same-record updates written in Apex carry test, maintenance, and recursion-control overhead a before-save Flow gives you for free; genuinely complex logic forced into Flow becomes an unmaintainable canvas. Second — the silent one — **automation stacking**: a record-triggered Flow *and* an Apex trigger *and* a legacy Process Builder all firing on the same save, with no shared order, recursing unpredictably. These are house opinions #11 and #12.

## How to apply

Before adding automation, inventory every entry point already firing on that object's event, then place new logic by where it falls against the declarative ceiling.

```
Same-record field update only        -> before-save record-triggered Flow (free DML)
Simple related-record CRUD / approval -> after-save record-triggered Flow
Complex logic / reusable units / unit tests needed
  / explicit recursion control / mid-transaction callout
  / bulk tuning past Flow's element limits           -> Apex trigger + handler
```

**Reach for Apex past the declarative ceiling when:**
- Logic is genuinely complex or needs reusable, unit-tested units.
- You need explicit recursion control or precise execution order.
- You need a synchronous callout inside the transaction.
- Bulk behavior must be tuned beyond Flow's element limits.

**Do:**
- Keep **one ordered entry point per object** — consolidate into the existing automation before adding another.
- **Document the call** in the design: "Flow because X" / "Apex because Y".

**Don't:**
- Stack a new Flow on an object that already has an Apex trigger (or vice versa) without consolidating.
- Default to Apex out of habit when a before-save Flow does the job with free DML.

## Edge cases / when the rule does NOT apply

"One entry point per *object*" is per trigger-event semantics — a before-save Flow and an after-save trigger are different phases and can legitimately coexist if each phase has a single owner and the ordering is documented. The rule targets *uncoordinated* stacking, not deliberate phase separation. Platform-event or async-driven automation that doesn't fire on the record save is outside this entry-point count.

## Edge note on limits

Whichever tool you choose, per-transaction governor limits are shared — a Flow loop over a large collection hits the same SOQL/DML ceilings as Apex.

## See also

- [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) — the full decision tree + the declarative ceiling
- [`../knowledge/trigger-handler-framework.md`](../knowledge/trigger-handler-framework.md) — the one-trigger-per-object handler pattern
- [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the shared limit budget
- [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) — the agent that owns this triage

## Provenance

Codifies house opinions #11–#12 from [`../CLAUDE.md`](../CLAUDE.md), grounded in [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) (sourced from Salesforce's record-triggered-automation decision guide).

---

_Last reviewed: 2026-05-30 by `claude`_
