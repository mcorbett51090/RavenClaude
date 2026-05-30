# Extract repeated Flow logic into autolaunched subflows

**Status:** Pattern — strong default once the same logic appears in a second Flow.

**Domain:** Declarative automation / maintainability

**Applies to:** `salesforce`

---

## Why this exists

When the same sequence — a fault-logging routine, a "calculate discount" block, a "notify the owner" pattern — is rebuilt by hand in five Flows, a change to that logic means editing five canvases and hoping you found them all. An **autolaunched subflow** is the Flow equivalent of extracting a method: define the logic once, give it typed input/output variables, and call it from any number of parent Flows. One edit propagates everywhere; the parent Flows stay small and readable; and a shared subflow (a single fault handler, for instance) makes behavior *consistent* across automations instead of subtly divergent. The cost of not factoring is silent drift — five copies that were identical at birth and aren't anymore.

## How to apply

Build the reusable logic as an **autolaunched Flow** with variables marked *Available for input* / *Available for output*, then drop a **Subflow** element into each parent.

```
Subflow:  Log_Flow_Fault   (autolaunched)
  Input vars (Available for input):
    message  (Text)   <- caller passes {!$Flow.FaultMessage}
    source   (Text)   <- caller passes the parent Flow's API name
  Body: Create Records -> Error_Log__c (Message__c = {!message}, Source__c = {!source})

Parent (any record-triggered Flow):
  Update Records --[Fault]--> Subflow: Log_Flow_Fault
                                 message = {!$Flow.FaultMessage}
                                 source  = "Account_AfterSave"
```

**Do:**

- Factor logic into a subflow the moment it is needed in a *second* Flow (rule of two).
- Define explicit input/output variables — treat the subflow's variable contract like a method signature.
- Centralize the fault-logging handler as one subflow so every Flow logs identically (pairs with [`flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md)).

**Don't:**

- Put **DML or Get inside a Loop** in a subflow — bulk-safety rules apply inside subflows exactly as in the parent; the subflow runs in the *same* transaction and shares its governor limits.
- Over-factor a one-off — a single-use block doesn't need to be a subflow; extract on the second use, not speculatively.

## Edge cases / when the rule does NOT apply

A subflow runs **in the caller's transaction** and consumes the **same per-transaction limits** — factoring does not buy you a fresh limit budget, so a subflow called inside a loop still issues its DML once per iteration (don't). Subflows cannot be called from a *before-save* record-triggered Flow that does DML-bearing work in a way the before-save context disallows — match the subflow's operations to the calling context. When the reusable logic needs to be callable from **Apex, a button, or REST** too, the same autolaunched Flow serves both — that is a feature, not a separate build. If the logic is genuinely complex/iterative, it may belong in Apex instead (see the declarative ceiling).

## See also

- [`flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md) — the shared fault-handler subflow it recommends
- [`flow-bulk-safe-no-dml-in-loop-elements.md`](./flow-bulk-safe-no-dml-in-loop-elements.md) — bulk-safety holds inside subflows
- [`flow-pick-the-flow-type-by-trigger-and-timing.md`](./flow-pick-the-flow-type-by-trigger-and-timing.md) — autolaunched is the subflow type
- [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) — when reusable logic should be Apex instead

## Provenance

Extends the maintainability discipline of [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) (one ordered entry point, consolidate logic) to the reuse axis, grounded in Salesforce autolaunched-Flow / Subflow-element documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
