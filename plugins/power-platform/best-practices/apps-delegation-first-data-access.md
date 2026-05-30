# Treat the delegation warning as a P1 design constraint, not a polish item

**Status:** Absolute rule — a non-delegable query against a source that can exceed the row cap is a bug, not a preference.

**Domain:** Canvas apps / Power Fx

**Applies to:** `power-platform`

---

## Why this exists

Canvas apps silently truncate non-delegable queries at the delegation row limit (500 by default, raisable to 2,000). The app works perfectly in dev against a 40-row table and then loses records in production once the table grows past the cap — with no error, no warning at runtime, just wrong results. The blue underline in Studio is the only signal, and it appears at author time, which is exactly when it is cheapest to fix. Delegation is the single most common cause of "the app shows the wrong data and nobody knows why," which is why the plugin constitution lists it as house rule §3 #9.

## How to apply

Design the query so the **predicate runs on the server**. A function/operator pair delegates only if both the function (`Filter`, `LookUp`, `Search`, `Sort`) and the operator (`=`, `>`, `StartsWith`, `In` — source-dependent) are on the source's delegable list.

```powerfx
// DON'T — Lower() is not delegable; the runtime pulls 500 rows then filters client-side.
Filter(Accounts, Lower(name) = Lower(txtSearch.Text))

// DO — StartsWith on a text column delegates to Dataverse/SharePoint/SQL.
Filter(Accounts, StartsWith(name, txtSearch.Text))

// DON'T — a delegation-breaking comparison buried in a row predicate.
Filter(Orders, total > Sum(colLines, amount))

// DO — pre-compute the scalar outside the predicate so only a delegable compare ships.
With({ threshold: Sum(colLines, amount) }, Filter(Orders, total > threshold))
```

**Do:**

- Fix every blue-underline warning, or explicitly cap and document the source as small (`< 500` rows, will-never-grow, with a written note).
- Push the predicate to the source: build a Dataverse view, add a SharePoint indexed column, or denormalize a filter column.
- Redesign to a search-first UX when full-list browsing forces a non-delegable shape — usually faster *and* more usable.

**Don't:**

- Raise the limit to 2,000 and call it solved. That moves the cliff, it does not remove it.
- Use `Search()` on SharePoint or SQL expecting delegation — it generally does not delegate there.
- Assume a function delegates on every source; coverage is per-source (see the cheat sheet).

## Edge cases / when the rule does NOT apply

- **Genuinely small, bounded sources** — a config table of 12 rows, a static option list. A non-delegable filter is fine; leave a comment stating the bound so a future maintainer does not "fix" a non-bug.
- **One-time bulk loads** — paged `ClearCollect` past the ceiling (collect by primary-key range) is an accepted pattern for loading-then-operating-locally; it is not live filtering.
- **Aggregates the source can't delegate at all** (`Sum`/`Count` over a filtered Dataverse subset in older runtimes) — accept the cap, cap the input set first, or move the aggregate server-side.

## See also

- [`../skills/canvas-app-performance/SKILL.md`](../skills/canvas-app-performance/SKILL.md) §2 — delegation rules per source with 2026 limits
- [`../skills/canvas-app-performance/resources/delegation-cheatsheet.md`](../skills/canvas-app-performance/resources/delegation-cheatsheet.md) — per-source operator coverage
- [`../agents/power-fx-engineer.md`](../agents/power-fx-engineer.md) — the agent that owns delegation puzzles
- [`../knowledge/apps-decision-trees.md`](../knowledge/apps-decision-trees.md) — `Decision Tree: Canvas data access — delegation-safe vs accept-the-cap`

## Provenance

Distilled from the `canvas-app-performance` skill (Core Principle #1 and §2) and plugin constitution §3 #9 / §4 anti-patterns, both shipped in `power-platform`. The "blue underline is not a suggestion" framing is the skill's own.

---

_Last reviewed: 2026-05-30 by `claude`_
