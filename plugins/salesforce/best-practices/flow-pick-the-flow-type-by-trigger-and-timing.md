# Pick the Flow type by what triggers it and when it must run

**Status:** Pattern — strong default; the type follows the trigger, not personal familiarity.

**Domain:** Declarative automation / Flow selection

**Applies to:** `salesforce`

---

## Why this exists

Salesforce ships several Flow types and they are **not interchangeable**: each has a different trigger, a different transaction context, and a different set of allowed operations. Building a screen Flow for a background data fix means a user has to click through it; building a record-triggered Flow for a nightly batch means it never runs on records that don't get saved; doing a callout in a before-save context fails because before-save can't make callouts. Picking the wrong type isn't a style choice — it produces a Flow that *can't do the job* or does it at the wrong time. The type is determined by two observable facts: **what fires it** and **when the work must happen relative to the triggering transaction**.

## How to apply

Map the requirement to the type by trigger source and timing:

```
A user needs to walk through a guided UI       -> Screen Flow
A record is created/updated, react same-record -> Record-triggered, BEFORE-save
A record is created/updated, related/async work-> Record-triggered, AFTER-save
Work must run later / on a delay after save     -> Record-triggered + Scheduled Path
A nightly/periodic sweep over a record set      -> Schedule-triggered Flow
React to a published platform event             -> Platform-event-triggered Flow
Reusable logic called by other Flows            -> Autolaunched (subflow) — no trigger
Called from Apex / a button / REST              -> Autolaunched Flow
```

```
Example — "email the owner 3 days before a Contract expires":
  NOT a screen Flow (no user), NOT a plain after-save (timing is days later)
  -> Record-triggered (after-save) on Contract
       + Scheduled Path offset = 3 days before {!$Record.EndDate}
         -> Send Email action
```

**Do:**

- Choose the type from the trigger source first, then confirm the timing (immediate vs scheduled path vs separate schedule).
- Use a **scheduled path** on a record-triggered Flow for "later, relative to this record" work; use a **schedule-triggered** Flow for "periodic sweep across many records."
- Use platform-event-triggered Flows to decouple producers from consumers.

**Don't:**

- Reach for a screen Flow when no human is in the loop — that work is autolaunched or record-triggered.
- Attempt callouts or async-only actions in a before-save context — they aren't allowed there.

## Edge cases / when the rule does NOT apply

Some needs combine types: a record-triggered Flow can *launch* a screen Flow only indirectly (record-triggered Flows have no UI); to put a user in the loop after a record change, notify them and let them open a screen Flow/action. Schedule-triggered Flows run as the automated process / a chosen user — sharing and FLS context differ from a record-triggered Flow running as the saving user; verify the running context for the data you touch. Platform-event-triggered Flows run in their own transaction after publish, so they don't roll back the producer. For the deeper "Flow vs Apex vs LWC" placement question, see the decision-tree file rather than just the Flow-type list. `[verify-at-build — confirm current Flow types and scheduled-path limits against the release notes]`

## See also

- [`flow-before-save-for-same-record-field-updates.md`](./flow-before-save-for-same-record-field-updates.md) — the before-vs-after-save axis in detail
- [`flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md) — gate whichever type you pick
- [`../knowledge/flow-lwc-decision-trees.md`](../knowledge/flow-lwc-decision-trees.md) — the "which Flow type" + "Flow vs Apex vs LWC" trees
- [`integration-platform-events-vs-cdc-vs-callout.md`](./integration-platform-events-vs-cdc-vs-callout.md) — when a platform-event trigger is the right seam

## Provenance

Codifies the record-triggered-Flow design discipline in [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) ("before-save for same-record … after-save for related records and async paths") extended across the full Flow-type set, grounded in Salesforce Flow-builder / record-triggered-automation documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
