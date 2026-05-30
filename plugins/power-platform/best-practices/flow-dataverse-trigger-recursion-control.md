# A Dataverse-triggered flow that updates its own trigger row must break the recursion loop

**Status:** Absolute rule — a *When a row is modified* flow that writes back to the same row with no recursion guard is an infinite loop waiting for the first edit. It will burn your daily request budget and can throttle the whole environment.

**Domain:** Power Automate / Dataverse

**Applies to:** `power-platform`

---

## Why this exists

The *When a row is added, modified or deleted* Dataverse trigger fires on **every** matching write — including writes the flow itself makes. A flow that triggers on "row modified" and then updates that same row re-triggers itself, which updates the row again, which re-triggers… The loop only stops when Dataverse's own infinite-loop-detection (depth) trips or you hit a request limit — by which point you've consumed thousands of API requests and possibly throttled other flows in the environment. This is the single most common self-inflicted Dataverse-flow outage. The fix is cheap and must be designed in, not bolted on after the incident.

## How to apply

You have three independent levers; use the cheapest that fits.

**1. Run only when the right columns change (cheapest).** In the trigger, set **Select columns** to *only* the column(s) whose change should fire the flow. If the flow writes back to a *different* column than the one it watches, the write-back never re-triggers it.

```
# Trigger: When a row is modified
# Select columns:  mc_status
# Flow writes to:  mc_last_processed_on   <-- different column, no re-trigger
```

**2. Filter rows + a sentinel column (when you must write the same column).** Have the flow set a flag the trigger's **Filter rows** excludes, so its own write fails the filter:

```
# Filter rows (OData, server-side):
mc_processed eq false
# Flow's last step sets mc_processed = true  -> its own write doesn't match the filter
```

**3. Trigger-depth guard (last resort, for genuine cascades).** Read the trigger's recursion depth and bail above a threshold. The depth lives in the trigger metadata header:

```
@greater(triggerOutputs()?['headers']?['x-ms-workflow-trigger-depth'], 1)
```

Use this as a **trigger condition** so a deep re-entry never even creates a run. (Header name verified this session against Microsoft Learn *trigger from Dataverse* guidance; treat the exact casing as `[verify before quoting]`.)

**Do:**
- Default to lever 1 (watch one column, write another) — it's free and needs no flag column.
- Combine **Select columns** with **Filter rows** when you genuinely must update the watched column.
- Set the trigger's **scope** (User / Business Unit / Organization) as narrow as the requirement allows — a narrower scope is fewer triggering events to begin with.

**Don't:**
- Leave **Select columns** empty on an update trigger that writes back — empty means "any column change fires it," which guarantees the loop.
- Rely on Dataverse's built-in depth cutoff as your design — it stops the runaway, but only after many wasted runs and a possible throttle.
- Put a **lookup** column in **Select columns** — lookups are unsupported there and the trigger silently never fires (a different bug, same box).

## Edge cases / when the rule does NOT apply

- **The flow never writes back to the trigger row** (it only reads it, or writes to a *related* row that doesn't itself trigger the flow) — no recursion risk, no guard needed.
- **Genuine intended cascades** (a parent update that *should* propagate to children which *should* re-run logic) — here the trigger-depth guard is the right tool, tuned to the legitimate cascade depth, not zero.
- **Create vs modify** — *When a row is added* doesn't self-recurse on update-backs, but a flow that *creates* rows that themselves match an *added* trigger can still loop; the same sentinel/filter logic applies.

## See also

- [`./flow-trigger-conditions-not-runtime-filters.md`](./flow-trigger-conditions-not-runtime-filters.md) — Filter rows / Select columns / trigger-condition mechanics this rule builds on
- [`../skills/power-automate/resources/error-handling-scopes-child-flows.md`](../skills/power-automate/resources/error-handling-scopes-child-flows.md) — "Control recursion with proper update logic or depth checks"
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Triggers — which trigger type?`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — flags "a Dataverse-triggered flow that updates the row that triggered it without filter conditions or depth control — infinite loop."

## Provenance

Codifies the `flow-engineer` agent's named anti-pattern (Dataverse self-update infinite loop) and the `power-automate` skill's "control recursion with proper update logic or depth checks." The three-lever framing (column-watch / sentinel-filter / depth-guard) is the standard mitigation order. The `x-ms-workflow-trigger-depth` header name is [unverified — training knowledge; verify against current Microsoft Learn before quoting exact casing].

---

_Last reviewed: 2026-05-30 by `claude`_
