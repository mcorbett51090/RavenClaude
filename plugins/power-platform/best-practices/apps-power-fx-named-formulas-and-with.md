# Prefer named formulas and `With()` over `Set()` in `OnStart` for derived state

**Status:** Pattern — strong default; reserve `App.OnStart` `Set` for non-derivable side effects.

**Domain:** Canvas apps / Power Fx

**Applies to:** `power-platform`

---

## Why this exists

A monolithic `App.OnStart` that `Set()`s a dozen globals serially delays first paint by seconds — the user stares at the splash screen while every value is computed eagerly, whether or not the first screen needs it. Worse, `Set()` scattered across control events creates an implicit dependency graph nobody can trace: change one value and three screens silently break. Named formulas (`App.Formulas`) recompute **lazily** and only when their inputs change, so they never bloat startup; `With()` scopes a temporary value to a single expression instead of leaking a global. Both move derived state out of imperative `Set` chains, which is `power-fx-engineer`'s stated top opinion.

## How to apply

Use `App.Formulas` for any value derived from other values. Use `With()` to name an intermediate inside one expression. Reserve `Set` in `OnStart` for genuine side effects.

```powerfx
// App.Formulas — declarative, lazy, recomputes only when User()/Config changes.
varUserEmail = Lower(User().Email);
varIsAdmin   = varUserEmail in colAdminEmails;
varTheme     = LookUp(Config, Key = "theme").Value;

// With() — scope an intermediate instead of leaking a global var.
With(
    { lines: Filter(OrderLines, OrderId = varCurrentOrder.Id) },
    { count: CountRows(lines), total: Sum(lines, Amount) }
)

// App.OnStart — keep it to side effects only (state that must exist before first nav).
Set(varCurrentOrder, Defaults(Orders))
```

**Do:**

- Move every derivable global from `OnStart` into `App.Formulas`.
- Use `With()` to compute a scalar once and reuse it (also keeps delegation-breaking aggregates out of row predicates).
- Keep variable prefixes consistent — `var*` context, `g*`/named globals, `col*` collections — so scope is readable without IntelliSense (constitution §3 #6).

**Don't:**

- Recreate config you can express as a named formula via `Set(...)` in `OnStart`.
- Put data loads in `App.Formulas` that should be per-screen `OnVisible` (named formulas are for *derivation*, not bulk fetch).
- Reference a named formula from `OnStart` expecting an order guarantee — named formulas are not sequential statements.

## Edge cases / when the rule does NOT apply

- **Named formulas cannot hold mutable state** — anything a button must *write* (a running selection, a cart) stays a `Set`/`Collect` variable. Named formulas are read-only and derived.
- **Behavioral/side-effecting work** (`Notify`, `Patch`, `Navigate`) cannot live in `App.Formulas` — those belong in event handlers.
- **Values needed before any screen renders** that must be imperatively set (e.g. a one-time `Set(varStartTime, Now())`) legitimately stay in `OnStart`.

## See also

- [`../skills/canvas-app-performance/SKILL.md`](../skills/canvas-app-performance/SKILL.md) §3 — OnStart vs OnVisible vs StartScreen
- [`./apps-canvas-performance-budget.md`](./apps-canvas-performance-budget.md)
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md) — `Decision Tree: Power Fx — named formula vs Set/OnStart vs With vs Concurrent`
- [`../agents/power-fx-engineer.md`](../agents/power-fx-engineer.md) — "Named formulas > `Set` in `OnStart`" is this agent's stated default

## Provenance

From `power-fx-engineer.md` "Opinions specific to this agent" (named-formulas-first, `Patch` with `Defaults`, variable prefixes) and the `canvas-app-performance` skill §3. `With()` scoping guidance complements the delegation rule in this plugin.

---

_Last reviewed: 2026-05-30 by `claude`_
