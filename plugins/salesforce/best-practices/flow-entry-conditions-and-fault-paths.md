# Set tight entry conditions and a fault path on every record-triggered Flow

**Status:** Absolute rule for fault handling; strong-default pattern for entry conditions.

**Domain:** Declarative automation / reliability

**Applies to:** `salesforce`

---

## Why this exists

Two silent defects ship in most hand-built Flows. First, **no entry condition**: the Flow runs on *every* save of the object, burning interview and element limits and re-evaluating logic that only matters for a fraction of records. Second, **no fault path**: when a DML or Get element fails (validation rule, FLS, lock contention, a required field), an unhandled fault in a record-triggered Flow **rolls back the entire triggering transaction** and surfaces a raw `FLOW_ELEMENT_ERROR` to the user — the save the user attempted dies with an opaque message. Entry conditions are a performance + correctness control; fault paths are a reliability control. Both are cheap; both are usually missing.

## How to apply

**Entry conditions** — gate the Flow at the Start element with the tightest filter that still catches every real case, and use the "only when a record is updated to meet the condition" option so re-saves that don't change the relevant field skip the Flow:

```
Start: Object = Case
       Condition Requirements = "All Conditions Are Met (AND)"
         Status        EqualTo   "Escalated"
         Priority      EqualTo   "High"
       Trigger only when the record is updated to meet the condition requirements
```

**Fault paths** — every element that can fault (Get/Create/Update/Delete Records, Action, callout) gets a **Fault connector** to an explicit handler. The handler logs, notifies, and fails *gracefully* rather than rolling back the user's save:

```
Update Records (Set_Parent) --[Fault]--> Create Records (Error_Log__c:
      Message__c = {!$Flow.FaultMessage}, Flow_Api_Name__c = "Case_AfterSave")
   --> (optional) Screen/Custom Notification to the running user
```

**Do:**
- Use AND-grouped, field-level entry conditions; prefer "updated to meet condition" over "every time."
- Wire a Fault connector on every DML/Action/callout element to a logging + notify handler.
- Centralize the fault handler into a subflow so every Flow logs the same way.

**Don't:**
- Leave the Start element's condition requirements as "None" (runs on every save).
- Leave a DML element with a dangling default-only path and no Fault connector.

## Edge cases / when the rule does NOT apply

A before-save Flow whose only action is an Assignment to `$Record` cannot fault on DML (there is no DML element) — the fault-path rule applies to elements that *can* fault, not to pure assignments. For genuinely "run on every record" needs (e.g. stamping a last-modified-by-automation marker), document the absence of an entry condition so a reviewer knows it is deliberate, not forgotten. In **screen** Flows, an unhandled fault shows the user the fault screen rather than rolling back a trigger context, but you still want a Fault path for a clean message.

## See also

- [`flow-before-save-for-same-record-field-updates.md`](./flow-before-save-for-same-record-field-updates.md) — the before-save pure-assignment exception
- [`flow-bulk-safe-no-dml-in-loop-elements.md`](./flow-bulk-safe-no-dml-in-loop-elements.md) — limits that tight entry conditions protect
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — Flow-type selection
- [`enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) — FLS faults Flows can hit

## Provenance

Codifies the `flow-automation-architect` house line "entry criteria are not optional" from [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md), grounded in Salesforce record-triggered Flow + fault-connector documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
