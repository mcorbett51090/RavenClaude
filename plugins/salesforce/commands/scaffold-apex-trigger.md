---
description: Scaffold a new Apex trigger using the one-trigger-per-object handler pattern — a thin trigger that delegates to a bulk-safe handler class with recursion control, plus a TestFactory-based test class. Bulkified and FLS-aware from the start.
argument-hint: "[SObject API name, e.g. Account]"
---

# Scaffold an Apex trigger (handler pattern)

You are running `/salesforce:scaffold-apex-trigger`. Create a production-grade Apex trigger for the SObject the user named (`$1`), following this plugin's one-trigger-per-object handler discipline. This is the `apex-engineer`'s default trigger shape.

## When to use this

A new object needs trigger automation that's genuinely code (not Flow). If the logic is same-record field updates with no callouts, **stop and recommend a before-save record-triggered Flow instead** (`flow-before-save-for-same-record-field-updates`) — don't scaffold Apex the platform can do declaratively.

## Inputs

- `$1` — the SObject API name (e.g. `Account`, `Custom_Object__c`). If absent, ask once which object.

## Steps

1. **Confirm there is no existing trigger** on this object — one trigger per object is non-negotiable (`apex-one-trigger-per-object-handler`). If one exists, extend its handler, don't add a second trigger.
2. Scaffold three files:
   - **`<Object>Trigger.trigger`** — thin: all six contexts routed to the handler, no logic in the trigger body.
   - **`<Object>TriggerHandler.cls`** — methods per context (`beforeInsert`, `afterUpdate`, …); **bulk-safe** (operate on `Trigger.new`/`Trigger.newMap` collections, never per-record SOQL/DML — `apex-soql-in-loops-is-a-defect`, `bulkify-every-soql-and-dml`); a static recursion guard (`apex-recursion-control-on-handlers`); CRUD/FLS enforced (`enforce-sharing-and-crud-fls`, `with sharing`).
   - **`<Object>TriggerHandlerTest.cls`** — uses a `TestFactory`, not `SeeAllData=true` (`apex-test-data-with-testfactory-not-seealldata`); asserts a **bulk** case (200 records), not just one.
3. Bind any dynamic SOQL with bind variables (`apex-bind-variables-in-dynamic-soql`); use Maps for O(1) lookups (`apex-collections-and-maps-for-o1-lookups`).
4. Show the diff. Run the local test if a scratch org / `sf` CLI is available.

## Guardrails

- Never put SOQL or DML inside a loop. Never use `SeeAllData`. Never add a second trigger to an object.
- Async work (callouts, heavy compute) → pick the channel deliberately (`apex-async-channel-selection`), don't block the trigger.
- Surface the human-only residue (deploy to the org, assign permissions) as a teed-up step with the exact `sf` command.
