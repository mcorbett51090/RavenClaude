# Filter at the trigger, not at runtime — use trigger conditions, not a Condition action

**Status:** Pattern — strong default; deviate only with a written reason (e.g. you genuinely need a run record for every event for audit).

**Domain:** Power Automate

**Applies to:** `power-platform`

---

## Why this exists

A `Condition` (or `Filter array`, or an early `Terminate`) placed **inside** the flow still counts as a flow run and consumes an API request against the connector's and the user's limits — the flow already started before it bailed out. A **trigger condition** is evaluated *before* the run is created, so a non-matching event produces a *skipped trigger check*, not a run. On a noisy source (a SharePoint list edited hundreds of times a day, a Dataverse row touched by other flows), the difference is the gap between thousands of wasted runs and zero. Microsoft's own coding-guidelines page calls this out: "While you can filter other events by adding conditions to the flow, the flow still runs and the calls are counted as an API request." (Verified this session against Microsoft Learn *Customize your triggers with conditions* / *Optimize Power Automate triggers*, 2026-05-30.)

## How to apply

A trigger condition is an expression that **must start with `@`** and resolve to `true` for the run to be created. Set it under the trigger's **Settings → Trigger Conditions**.

```
@greater(triggerOutputs()?['body/amount'], 100)
```

Multiple conditions are ANDed by default; for OR, write one expression:

```
@or(equals(triggerBody()?['Status']?['Value'], 'Approved'), equals(triggerBody()?['Priority'], 'High'))
```

For **Dataverse** triggers (*When a row is added, modified or deleted*) prefer the trigger's own **Filter rows** (OData) + **Select columns** boxes over a generic trigger condition — they run server-side in Dataverse:

```
# Filter rows (note: NO $filter= prefix here, unlike the raw Web API)
statuscode eq 1 and contains(mc_partner_name,'Contoso')
```

**Authoring tip:** drop a temporary `Filter array` action, build the condition in its advanced-mode editor, copy the generated expression into the trigger condition, then delete the `Filter array` action. (Microsoft's documented shortcut for getting the expression syntax right.)

**Do:**
- Move every "should this run at all?" decision to the trigger condition.
- On Dataverse update triggers, set **Select columns** to only the columns whose change should fire the flow — but never include the primary key or always-present columns, or every update fires it.
- Keep the expression null-safe: `@equals(coalesce(triggerOutputs()?['body/status'], ''), 'Active')`.

**Don't:**
- Start a flow on every event and `Terminate` early "to keep it simple" — you still paid for the run.
- Put a lookup column in Dataverse **Select columns** — lookups are unsupported there and silently never fire.
- Forget the leading `@` — without it the condition is treated as a literal string and the flow runs every time.

## Edge cases / when the rule does NOT apply

- **You need an audit record for every event**, including non-matching ones — then a run + early `Terminate(Cancelled)` is intentional, not waste.
- **The decision needs data the trigger payload doesn't carry** (e.g. a related-record lookup). The trigger condition only sees `triggerOutputs()`/`triggerBody()`; if you must fetch more data to decide, that fetch has to happen inside the run.
- **`Select columns` semantics gotcha:** the flow triggers when a listed column is *included* in the update request, even if its value didn't change. For value-based gating, combine **Select columns** with a **Filter rows** OData expression.

## See also

- [`../skills/power-automate/resources/expressions-and-dynamic-content.md`](../skills/power-automate/resources/expressions-and-dynamic-content.md) — `triggerOutputs()` / `body()` / `coalesce()` patterns
- [`./flow-dataverse-trigger-recursion-control.md`](./flow-dataverse-trigger-recursion-control.md) — the recursion trap that trigger conditions also help prevent
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Triggers — which trigger type?`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — owner of the flow surface
- Microsoft Learn: [Customize your triggers with conditions](https://learn.microsoft.com/power-automate/customize-triggers) · [Optimize Power Automate triggers](https://learn.microsoft.com/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers)

## Provenance

Microsoft Learn coding-guidelines pages on trigger conditions and trigger optimization, plus the Dataverse *create-update-delete-trigger* reference (Filter rows / Select columns), all verified this session 2026-05-30. Reinforces `flow-engineer`'s surface-area note on "filter expressions, run-only-when-columns-change."

---

_Last reviewed: 2026-05-30 by `claude`_
