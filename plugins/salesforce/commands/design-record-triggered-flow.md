---
description: Design a record-triggered Flow the right way — pick the flow type by trigger+timing, use before-save for same-record updates, keep it bulk-safe with no DML in loops, and add entry conditions + fault paths. Routes to Apex when the logic outgrows Flow.
argument-hint: "[object and what should happen, e.g. 'Opportunity: set Stage on close']"
---

# Design a record-triggered Flow

You are running `/salesforce:design-record-triggered-flow`. Help the user design a correct record-triggered Flow for the automation they described (`$ARGUMENTS`), following this plugin's `flow-automation-architect` discipline — and tell them honestly when the job belongs in Apex instead.

## When to use this

A new piece of record automation is needed and you're deciding *how* to build it declaratively. Use the Flow-vs-Apex single-entry-point rule (`flow-vs-apex-one-entry-point`): one automation entry point per object per context — never a Flow and a trigger both firing on the same event.

## Steps

1. **Pick the flow type by trigger + timing** (`flow-pick-the-flow-type-by-trigger-and-timing`):
   - Same-record field updates, no related records → **before-save** record-triggered (fastest, no extra DML — `flow-before-save-for-same-record-field-updates`).
   - Needs related records / async / emails → **after-save**.
   - Scheduled / batch → schedule-triggered, not record-triggered.
2. **One record-triggered flow per object per context** (`flow-one-record-triggered-per-object-per-context`) — consolidate, don't proliferate.
3. **Bulk-safe by construction** (`flow-bulk-safe-no-dml-in-loop-elements`): no Create/Update/Delete *inside* a loop element; collect then act once.
4. Add **entry conditions** (so it only runs when it must) and **fault paths** on every element that can fail (`flow-entry-conditions-and-fault-paths`).
5. **Extract reusable logic into subflows** (`flow-extract-reusable-logic-into-subflows`) rather than copy-paste.
6. **Escalate to Apex** when: complex bulk logic, >1 callout, heavy loops, or rollback semantics Flow can't express. Recommend `/salesforce:scaffold-apex-trigger` and say why.

## Guardrails

- Never build a Flow that duplicates an existing trigger's event (double automation = order-of-execution bugs).
- Never put DML in a loop element — it's the Flow equivalent of SOQL-in-a-loop.
- Declarative-first (`platform-declarative-before-code`), but don't force Flow to do an Apex job.
