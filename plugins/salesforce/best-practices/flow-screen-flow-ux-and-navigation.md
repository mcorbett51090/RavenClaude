# Design Screen Flow UX for progressive disclosure and graceful navigation — not a single long form

**Status:** Pattern
**Domain:** Flow automation / UX
**Applies to:** `salesforce`

---

## Why this exists

Screen Flows are the primary declarative UX mechanism for guided multi-step processes in Salesforce. A Screen Flow with 15 fields on a single screen is a form, not a flow — it defeats the "one thing at a time" interaction principle, overwhelms users, and produces validation errors that force them to scroll back through the form to find the problem. Progressive disclosure (showing each logical step on its own screen, with navigation back to correct earlier choices) produces higher completion rates, fewer user errors, and a cleaner undo model. It also makes the flow easier to extend — adding a step means adding a screen, not expanding an already-crowded form.

## How to apply

Screen layout principles:

| Principle | Implementation |
|---|---|
| One logical question per screen | Group related fields (contact info, address, payment) but not all fields at once |
| Back navigation available | Always enable "Previous" button on multi-step flows |
| Progressive validation | Validate each screen's fields before proceeding, not all at once at the end |
| Error messages at field level | Use formula resources to compute error messages and surface them via `{!errorMessage}` components |
| Conditional screens | Use branch/decision elements to show only screens relevant to the user's prior choices |

```xml
<!-- Example: conditional screen using a Decision element -->
<decision name="Is_B2B_Customer">
    <rules>
        <name>Is_B2B</name>
        <conditions>
            <leftValueReference>CustomerType</leftValueReference>
            <operator>EqualTo</operator>
            <rightValue><stringValue>Business</stringValue></rightValue>
        </conditions>
        <connector><targetReference>B2B_Details_Screen</targetReference></connector>
    </rules>
    <defaultConnector><targetReference>B2C_Details_Screen</targetReference></defaultConnector>
</decision>
```

**Do:**
- Keep each screen to 5 fields or fewer — if more are needed, consider whether some can be computed from prior answers.
- Use the `Display Text` component with dynamic merge fields to show the user a summary of what they have entered before the final submit screen.
- Place the `Fault` connector on every data element (Record Create, Record Update, Apex Action) and route it to a screen that shows a user-friendly error message.

**Don't:**
- Put a `Record Create` or `Record Update` inside a loop on a screen flow's submit — DML in a loop is banned for Flow just as for Apex (see `flow-bulk-safe-no-dml-in-loop-elements`).
- Remove the "Previous" button from intermediate screens — users need to correct earlier choices without starting over.
- Validate at the final screen only — by then the user has no context for which screen the invalid data came from.

## Edge cases / when the rule does NOT apply

A single-screen data-entry form (a quick-capture component used by power users who know the fields well) may put all fields on one screen if the field count is < 8 and all fields are always relevant. Document the design decision.

## See also

- [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) — owns Screen Flow design and navigation patterns
- [`./flow-entry-conditions-and-fault-paths.md`](./flow-entry-conditions-and-fault-paths.md) — the fault-path rule that applies to every DML element in a Screen Flow

## Provenance

Codifies standard Salesforce Flow UX best practice; Lightning Flow design guide (Salesforce UX guidance); standard progressive-disclosure interaction principle.

---

_Last reviewed: 2026-06-05 by `claude`_
