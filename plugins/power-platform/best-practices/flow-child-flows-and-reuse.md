# Extract logic used 2+ times into a child flow with explicit input/output schemas

**Status:** Pattern — strong default; a parent flow that inlines the same 5-action sequence three times is a refactor target, not a finished build. (House rule §3 "lowest-tier mechanism" + `flow-engineer` opinion "child flows for any logic used 2+ times.")

**Domain:** Power Automate

**Applies to:** `power-platform`

---

## Why this exists

Inlined-and-copied logic drifts: you fix the bug in two of the three copies and the third silently keeps misbehaving. A **child flow** (a separate solution-aware cloud flow triggered by *When an HTTP request is received* / **Manually trigger a flow** with a typed input schema, returning via **Respond to a PowerApp or flow**) gives you one place to fix, one place to test, and a clean input/output contract the parent can't violate. It also shrinks the parent below the practical review ceiling — a 30-action parent that calls three named child flows is reviewable; a 90-action monolith is not. The cost is real (a child-flow call is a synchronous round-trip with its own latency and its own run record), so this is a *pattern*, not an absolute: reuse and readability earn the round-trip; a one-off three-action sequence does not.

## How to apply

A child flow is a solution-aware flow whose trigger carries a **typed input schema** and which ends in **Respond to a PowerApp or flow** carrying a **typed output schema**. The parent calls it with the **Run a Child Flow** action.

Child trigger input (Manually trigger a flow, V2 — typed inputs):

```
Inputs: partnerId (Text), invoiceAmount (Number), notifyEmail (Email)
```

Child response (Respond to a PowerApp or flow) — declare the output schema so the parent gets typed dynamic content:

```json
{
  "type": "object",
  "properties": {
    "status":  { "type": "string" },
    "recordId":{ "type": "string" }
  }
}
```

Parent calls it and reads typed outputs:

```
@body('Run_a_Child_Flow')?['recordId']
```

**Do:**
- Put the child flow **in the same solution** as the parent — child flows must be solution-aware to be callable via *Run a Child Flow*, and they inherit the parent's connection references at call time.
- Give the child a **typed** input and a **typed** output schema. Untyped `string`-everything children push the parsing burden back onto every caller.
- Always end the child with **Respond to a PowerApp or flow** (or **Terminate** with a status) — a child that falls off the end returns nothing and the parent's downstream `body(...)` references resolve null.
- Keep the child's own **Try-Catch-Finally**; on failure, terminate the child with `Failed` so the parent's `Catch` can detect it via `outputs('Run_a_Child_Flow')?['statusCode']`.

**Don't:**
- Call a child flow inside a high-iteration `Apply to each` without measuring — each call is a synchronous run; 5,000 iterations is 5,000 child runs against your daily request budget. Batch instead (see `flow-concurrency-and-pagination.md`).
- Build a child flow for a genuinely one-off three-action sequence — the round-trip and the extra run record aren't worth it.
- Let parent and child double-handle the same error — decide where the `Terminate(Failed)` lives (the child) and have the parent only *react* to it.

## Edge cases / when the rule does NOT apply

- **Instant/child flows can't call themselves recursively** to unbounded depth — Power Automate has no tail-call; deep recursion belongs in a `Do until` loop or a Dataverse plug-in.
- **Connection-reference inheritance** only works for *solution-aware* parent→child. A child flow shared outside the solution loses the inherited context and asks for its own connections.
- **Latency-critical paths** (a synchronous response back to a canvas app) may not tolerate the extra child round-trip — inline there, and accept the duplication, or move the logic to a Power Fx named formula.

## See also

- [`../skills/power-automate/resources/error-handling-scopes-child-flows.md`](../skills/power-automate/resources/error-handling-scopes-child-flows.md) — child-flow schema + Respond-to-a-PowerApp-or-flow reference
- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — how a child's `Terminate(Failed)` surfaces in the parent's `Catch`
- [`./flow-concurrency-and-pagination.md`](./flow-concurrency-and-pagination.md) — why not to call a child flow per-row in a large loop
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Reuse — child flow vs inline vs other surface`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — "Child flows for any logic used 2+ times, with clear input/output schemas."

## Provenance

Codifies `flow-engineer`'s "child flows for any logic used 2+ times" opinion and the `power-automate` skill's child-flow resource (typed schemas, *Respond to a PowerApp or flow*, solution-context inheritance). The connection-reference inheritance and "must be solution-aware to be callable" points are the load-bearing ALM gotchas. Child-flow call mechanics (Run a Child Flow, synchronous round-trip) [unverified — training knowledge; verify against current Microsoft Learn *Create child flows* before quoting limits].

---

_Last reviewed: 2026-05-30 by `claude`_
