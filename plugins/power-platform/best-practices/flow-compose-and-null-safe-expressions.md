# Name intermediate values with Compose and make every cross-action reference null-safe

**Status:** Pattern — strong default. A flow built from deeply nested one-line expressions with no `Compose` steps is unreviewable and fails intermittently on null paths.

**Domain:** Power Automate

**Applies to:** `power-platform`

---

## Why this exists

Two readability/robustness failures recur in flows. First, **dynamic content can be null on some run paths** — an optional field, a branch that didn't execute, an empty `List rows` result — and an unguarded `body('X')?['field']` reference throws or silently produces a broken downstream value. Second, **deeply nested single-line expressions** (`@if(greater(length(body('Get_items')?['value']),0), first(...)..., ...)`) are impossible to debug in run history: you see the final value, not the intermediates, so you can't tell which sub-expression went wrong. `Compose` is free, names intermediate values so they appear individually in run history, and turns a 200-character nested expression into three readable steps. Guarding with `coalesce()` / `if()` turns an intermittent null-path failure into a defined default.

## How to apply

**Null-safe references** — guard every cross-action read that *could* be absent:

```
# Default an optional field to empty string instead of throwing:
@coalesce(triggerOutputs()?['body/middleName'], '')

# Guard a list that might be empty before taking first():
@if(greater(length(body('List_rows')?['value']), 0), first(body('List_rows')?['value']), null)
```

Use the `?[...]` safe-navigation operator everywhere — `body('X')?['a']?['b']` returns null instead of erroring if `a` is absent.

**Compose to name intermediates** — break a nested expression into named steps; the name shows up in run history:

```
Compose - Order Items     =  body('List_rows')?['value']
Compose - Order Count     =  length(outputs('Compose_-_Order_Items'))
Compose - Has Orders      =  greater(outputs('Compose_-_Order_Count'), 0)
```

**Parse JSON early** for HTTP/custom-connector responses so downstream steps get typed dynamic content instead of raw-string indexing.

**Do:**
- Reference the correct surface: `triggerOutputs()`/`triggerBody()` for the trigger, `outputs('Action')` for an action's raw output, `body('Action')` for its body payload.
- Name `Compose` actions descriptively ("Compose - Order Total"), so the expression self-documents and the value is inspectable per-run.
- `coalesce()` every optional field read; assume any cross-branch reference can be null.

**Don't:**
- Nest four function calls in one expression when three `Compose` steps would show the failure point — debuggability beats brevity in a flow.
- Index into an HTTP response with raw string functions when `Parse JSON` would give you typed content.
- Reference an action's output from a branch that may have been skipped without a null guard — skipped actions yield null, and the unguarded read fails only sometimes.

## Edge cases / when the rule does NOT apply

- **A genuinely trivial expression** (`utcNow()`, a single safe field read off the trigger that's always present) doesn't need a wrapping `Compose` — don't pad the flow for ceremony.
- **`coalesce` hides real bugs** if overused — defaulting a *required* field to `''` can mask a missing-data problem; guard, but don't paper over data you actually need (fail loudly there instead).
- **`Compose` adds action count** — in a very tight latency-critical flow with thousands of iterations, inline the trivial ones; the readability win is per-authoring, the action-count cost is per-run.

## See also

- [`../skills/power-automate/resources/expressions-and-dynamic-content.md`](../skills/power-automate/resources/expressions-and-dynamic-content.md) — `outputs()`/`body()`/`triggerOutputs()`, `coalesce`, date/string/array function reference
- [`./flow-trigger-conditions-not-runtime-filters.md`](./flow-trigger-conditions-not-runtime-filters.md) — null-safe trigger conditions use the same `coalesce` pattern
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — flow design trees
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — "Compose early, Compose often. Naming intermediate values makes flows readable; Compose is free."

## Provenance

Codifies the `flow-engineer` agent's "Compose early, Compose often" opinion and the `power-automate` skill's expressions resource (null-guard with coalesce/if, Parse JSON early, descriptive Compose names, avoid deeply nested expressions). Expression-function behavior is stable Power Automate / Logic Apps workflow-definition-language; safe-navigation `?[...]` and `coalesce` semantics are long-standing.

---

_Last reviewed: 2026-05-30 by `claude`_
