# Use a before-save record-triggered Flow for same-record field updates

**Status:** Pattern — strong default; use after-save (or Apex) only when the work is not a same-record write.

**Domain:** Declarative automation / performance

**Applies to:** `salesforce`

---

## Why this exists

When automation only needs to set fields **on the record that triggered it**, a before-save record-triggered Flow writes those fields *in the same DML the platform is already performing* — no extra DML statement, no extra SOQL, no save re-entry. Doing the same work in an after-save Flow (or an old Workflow Field Update, or an after trigger) forces a second `update` on the same record: a wasted DML row against the governor budget and an extra pass through the save order that can re-trigger automation. Salesforce's own performance guidance reports before-save record-triggered Flows running materially faster than the equivalent after-save update. `[verify-at-build — exact multiplier varies by release]`

## How to apply

Pick the save phase by **what the Flow writes**, not by habit:

```
Writes only fields on the triggering record  -> BEFORE-save Flow
Creates/updates OTHER records, sends email,
  posts to Chatter, makes a callout, runs async -> AFTER-save Flow
```

In a before-save Flow you set the field directly on the `$Record` global variable with an **Assignment** element and let the platform commit it — there is **no Update Records element** and there should not be one:

```
Start: Object = Opportunity, Trigger = "A record is updated",
       Optimize for = "Fast Field Updates"   (this is the before-save mode)
  Decision: {!$Record.StageName} == "Closed Won"
    -> Assignment: {!$Record.Commission_Locked__c} = true
                   {!$Record.Close_Audit_Date__c} = {!$Flow.CurrentDate}
  (no Update Records element — the assignment to $Record is the write)
```

**Do:**
- Set entry conditions so the Flow only runs when the relevant field actually changed (see [`flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md)).
- Assign straight to `$Record` and let the implicit save persist it.

**Don't:**
- Add an Update Records element that re-saves the triggering record in a before-save Flow — it is unnecessary and can recurse.
- Use after-save just because that is the only mode you know; that is the wasted-DML anti-pattern.

## Edge cases / when the rule does NOT apply

Before-save Flows **cannot**: create or update other records, send email/Chatter, call subflows that do DML, run asynchronously, or make callouts — those require after-save. They also do not see the record's Id on **insert** until after the save in some cross-record contexts; same-record fields are fine. If you need both a same-record update *and* related-record work, do the same-record part before-save and the rest after-save (still one owner per phase — see [`flow-one-record-triggered-per-object-per-context.md`](./flow-one-record-triggered-per-object-per-context.md)).

## See also

- [`flow-one-record-triggered-per-object-per-context.md`](./flow-one-record-triggered-per-object-per-context.md) — one Flow per phase
- [`flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md) — don't run on every save
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — "before vs after save" tree
- [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the shared DML budget this saves

## Provenance

Codifies house opinion #11 ("before-save Flow is free DML") from [`../CLAUDE.md`](../CLAUDE.md) and [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md), grounded in Salesforce's record-triggered-automation decision guide.

---

_Last reviewed: 2026-05-30 by `claude`_
