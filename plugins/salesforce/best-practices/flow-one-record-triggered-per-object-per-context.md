# One record-triggered Flow per object per save phase — and order it

**Status:** Pattern — strong default; deviate only with a written, ordered reason in the design.

**Domain:** Declarative automation / automation density

**Applies to:** `salesforce`

---

## Why this exists

Record-triggered Flows on the same object and same save phase have **no guaranteed order unless you set one**, and they recurse against each other the same way stacked triggers do. House opinion #12 ("one automation entry point per object") is usually read as "Flow *or* Apex," but it bites just as hard *within* Flow: three "Set Status" before-save Flows on `Opportunity` will run in an undefined order until you assign each a Trigger Order, and each new one widens the recursion surface. The sibling doc [`flow-vs-apex-one-entry-point.md`](./flow-vs-apex-one-entry-point.md) covers the Flow-vs-Apex axis; this doc covers the *Flow-vs-Flow* axis on a single object.

## How to apply

Treat each (object, save phase) pair as a slot that holds **one Flow**. The phases are distinct and may each hold one owner:

```
Account · before-save   -> exactly one record-triggered Flow (free same-record field writes)
Account · after-save     -> exactly one record-triggered Flow (related records, async, callouts)
Account · async path     -> runs after the transaction commits (scheduled paths)
```

When a second requirement lands on a slot that is already taken, **add a decision branch inside the existing Flow** instead of creating a second Flow. If two Flows on the same phase are genuinely unavoidable (e.g. one ships in a managed package), give each an explicit **Trigger Order** value (1–2000) on the Flow's start element so the run order is deterministic. `[verify-at-build — Trigger Order is available on record-triggered Flow start elements; confirm the 1–2000 range against the current release notes]`

**Do:**
- Consolidate new logic into the existing Flow for that phase via a Decision element.
- Set an explicit **Trigger Order** when two Flows on one phase cannot be merged.
- Name Flows `<Object>_<Phase>_<Purpose>` so the slot is obvious in the Flow list.

**Don't:**
- Build a second before-save Flow on an object that already has one, without a Trigger Order.
- Mix a before-save Flow and an Apex `before` trigger on the same object without documenting which owns the same-record writes.

## Edge cases / when the rule does NOT apply

A before-save Flow and an after-save Flow are **different phases** and are expected to coexist — that is not stacking. Managed-package Flows you cannot edit are a legitimate reason to run two Flows on one phase; Trigger Order is the tool that makes it safe. Scheduled-path and async-after-commit logic inside a record-triggered Flow does not count against the synchronous-phase slot because it runs in a separate transaction.

## See also

- [`flow-vs-apex-one-entry-point.md`](./flow-vs-apex-one-entry-point.md) — the Flow-vs-Apex axis of the same house opinion
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — "Which Flow type" + "before vs after save" trees
- [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) — the declarative ceiling
- [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) — the agent that owns density triage

## Provenance

Codifies house opinion #12 from [`../CLAUDE.md`](../CLAUDE.md), extended to the Flow-vs-Flow case, grounded in [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) and Salesforce's record-triggered-automation decision guide.

---

_Last reviewed: 2026-05-30 by `claude`_
