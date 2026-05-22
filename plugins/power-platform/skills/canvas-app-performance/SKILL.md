---
name: canvas-app-performance
description: Diagnose and fix Power Fx canvas app performance — delegation as a P1 design constraint, lazy-load patterns, Concurrent() vs sequential, ClearCollect vs collection growth, OnStart vs OnVisible, screen-transition cost, control-count budgets per screen, and the connector-call audit via Monitor. Used by `power-fx-engineer` (primary).
---

# Canvas App Performance Skill

**Purpose:** Senior-maker playbook for diagnosing and fixing canvas app performance — and, more importantly, for designing apps that don't get slow in the first place. Performance work in canvas is not "optimisation after the fact"; the design choices that lock in performance are made on day one. Most slow apps got slow at design time, not because of "extra features."

## When to Use

- **An app is reported slow** — by users, by Monitor, by your own gut on load or screen transition.
- **Before shipping a new canvas app** — pre-release performance pass, *especially* for any app touching >500 rows or wired to 3+ connectors.
- **Reviewing someone else's canvas app** — performance is a code-review dimension, not a follow-up.
- **Adding a new screen, gallery, or connector to an existing app** — verify the addition didn't push the app over a control-count or delegation cliff.

## Core Principles

1. **Delegation is a P1 design constraint, not a polish item.** (Plugin house rule §3 #9.) Non-delegable filters silently truncate at 500 rows by default. If your data source might exceed 500 rows now or ever, delegation is mandatory.
2. **The runtime evaluates expressions on every relevant change.** A control's `Text`, `Visible`, `Items` property is not "set once" — it's a function the runtime calls when dependencies change. A `LookUp()` in a Gallery's `ThisItem` context runs once per visible row, on every refresh.
3. **Network calls are the dominant cost.** Local Power Fx is fast. Connector calls are slow. Audit the count and frequency of connector calls per user interaction — that's your real performance budget.
4. **OnStart is the wrong place for almost everything.** Use `OnVisible` per screen, or `App.StartScreen` for the initial routing decision. OnStart blocks the splash screen.
5. **Pre-load, then operate.** ClearCollect once OnVisible, then Filter/LookUp/Search against the collection. Re-hitting the connector for every interaction is the most common slow-app pattern.

## Playbook

### 1. The canvas runtime model in plain English

A canvas app is a tree of controls. Every control has properties that are *expressions*. The runtime evaluates an expression whenever a dependency it references changes. So:

- `Label1.Text = LookUp(Accounts, ID = ThisItem.AccountID).Name` inside a Gallery — the LookUp runs once per row, on every refresh of the gallery. With 200 rows and a Dataverse source, that's 200 connector calls per gallery refresh.
- `Button1.Visible = User().Email = "admin@x.com"` — evaluated once on screen show, then cached until User() invalidates.
- `Gallery1.Items = Filter(Accounts, Status = "Active")` — if Filter is delegable, the connector receives the filter and returns at most the delegation limit; if not, the runtime pulls up to 500 rows and filters client-side.

The mental model: **every property is a function; every function runs whenever its inputs change**. Build with that in mind.

### 2. Delegation rules per data source (2026 limits)

| Data source | Common delegable | Common NON-delegable | Default row cap |
|---|---|---|---|
| **Dataverse** | `Filter`, `Search`, `LookUp`, `Sort`, `SortByColumns`, most operators (`=`, `>`, `<`, `In`, `StartsWith`) on most columns | `Distinct` on some types, complex `If` in predicates, `Sum`/`Count` on filtered subsets in older runtimes | 500 (raise to 2000 in Advanced Settings) |
| **SharePoint** | `Filter`, `LookUp`, `Sort` on indexed columns; `StartsWith`, `=` on text | `Search`, complex predicates, lookups across lists, `In` on choice columns (partial) | 500 (raise to 2000) |
| **SQL Server** | `Filter`, `Sort`, `LookUp`, most operators | `Search`, `IsBlank()` in predicate, some `If` patterns | 500 (raise to 2000) |
| **Excel / OneDrive Excel** | Almost nothing delegates | Almost everything | 500 hard cap |

**Rule**: if Power Fx underlines your expression with a blue warning, it doesn't delegate. The warning is not a suggestion. The 500-row cap will silently truncate your results in production where the table has grown.

Patterns to work past the ceiling:
- **Paged Search/Filter + ClearCollect**: collect first 2000 rows, then collect next 2000 by offset (using a primary key range), aggregate into one collection. Works for one-time loads; not for live filtering.
- **Push the filter to the data source**: where possible, build a Dataverse view or SharePoint indexed column so the predicate becomes delegable.
- **Redesign the UX**: do users actually need to browse all rows? A search-first UX with delegable Filter is usually faster *and* more usable than a full-list-then-narrow UX.

See [`resources/delegation-cheatsheet.md`](resources/delegation-cheatsheet.md) for the per-source table with current Dataverse Web API operator coverage.

### 3. OnStart vs OnVisible vs App.StartScreen

- **App.OnStart** — fires once at app launch, before the first screen renders. The user sees the splash screen until OnStart finishes. Use only for: setting up global state that *every* screen needs and that *must* be set before navigation. The default impulse to "ClearCollect everything OnStart" is wrong — it makes the splash screen sit for 8 seconds.
- **App.StartScreen** — formula that decides which screen the app opens to. Fast: just evaluates and routes.
- **Screen.OnVisible** — fires every time the screen becomes active. Use for: per-screen ClearCollect, refreshing screen-local state. This is where most data loading should live.

**Pattern**: App.OnStart sets only user-context (`Set(varUser, User())`) and config (`Set(varAppConfig, LookUp(Config, Key="App"))`). Screens load their own data OnVisible. The splash is short; data appears as the user navigates.

### 4. Concurrent() vs sequential `;`

Sequential operations (`Op1; Op2; Op3`) run one after the other. With three independent Dataverse calls, that's three round-trip latencies stacked.

`Concurrent(Op1, Op2, Op3)` runs them in parallel and waits for all to complete. Same total work, ~1/3 the wall time on a network-bound workload.

**Rule**: any time you have 2+ independent operations in `OnVisible` or `OnStart`, wrap them in `Concurrent()`. The only reason not to is if Op2 depends on Op1's result — and even then, the dependent parts can often be re-grouped.

### 5. ClearCollect vs collection growth

- `ClearCollect(colA, source)` — clears colA, then re-collects. Use for refresh.
- `Collect(colA, item)` — appends. Useful for streaming pages.
- **Anti-pattern**: `Collect(colA, source)` in a loop with no `Clear()` — collection grows unbounded across user navigations.
- **Anti-pattern**: ClearCollect on every `OnSelect` of a button the user mashes — fires a network round-trip each time. Throttle or cache.

### 6. Control-count budget per screen

Hard guidance: **>500 controls on one screen is a smell**. The runtime re-evaluates all visible expressions on relevant changes; control count drives that workload directly.

Common offenders:
- Galleries with 8+ controls per item, scrolled through 200 items → effectively 1600 controls in scope.
- Mega-forms with 30 fields × 3 controls (label + input + error) = 90 controls before validation logic.
- Hidden "tabs" implemented as 4 stacked containers with `Visible` toggling — all four are still in the tree.

Fixes:
- Use a Custom Page or model-driven form for heavy data-entry surfaces (form rendering is server-side, not Power Fx-evaluated).
- Reduce gallery template complexity — pull supplementary labels into a single concatenated string instead of 5 separate Label controls.
- Split a mega-screen into a navigation flow across 2-3 simpler screens.

### 7. Lookup denormalization

**Anti-pattern**: `Label.Text = LookUp(Accounts, ID = ThisItem.AccountID).Name` inside a 200-row Dataverse-backed gallery. That's 200 LookUps per refresh.

**Fix**: in the source query, project the label column onto the row. Either:
- Use a Dataverse view that includes the related Account.Name as a column on the row; bind the gallery to the view.
- Store a denormalized AccountName text column on the row (writable by a flow on update).
- ClearCollect the parent table into a local collection once OnVisible; LookUp against the collection (no network round-trip per row).

### 8. The Monitor workflow

When an app is slow:
1. Open the app in Studio. Tools → **Monitor**. Play the app.
2. Reproduce the slow interaction.
3. In Monitor, sort by Duration descending.
4. The top entries are your top fixes. Common findings:
   - A connector call repeated dozens of times per screen show → LookUp in a gallery, fix per §7.
   - A single slow Dataverse call (>2s) → check whether the query is non-delegable, or whether the user has Read access to the table without a security-role optimization.
   - An expensive `Patch()` on a complex form → split into smaller patches or push to a flow.

Always Monitor *first*, then fix. Don't optimize what isn't slow.

## Anti-Patterns to Flag

- LookUp in a gallery's ThisItem expressions
- OnStart doing 10 ClearCollects sequentially
- Sequential connector calls where Concurrent() would parallelise
- Filter / Search with the blue underline (non-delegable) on a real data source
- Single screen with 500+ controls
- Stacked hidden containers used as a tab pattern
- Re-collecting on every click of a button
- Hard-coded environment URLs in formulas (also violates §3 #2 — env vars)
- GUIDs in formulas — look up by name or alternate key (§3 #11)
- `Set(...)` and `Collect(...)` calls without `var*`/`col*` prefix (§3 #6)

## Escalation

- **Performance still bad after delegation + Monitor + pre-load pattern** → consider whether canvas is the right tool. A heavy data-entry workflow often belongs in a model-driven app or Custom Page; escalate to Team Lead.
- **Suspected platform throttling** → `power-platform-admin` for capacity / API limit review.
- **Underlying connector slow on its own** → `flow-engineer` for connector-call alternatives, or `dataverse-architect` if the source is Dataverse and the slowness is query-shape related.
- **App needs >2000 rows interactively** → architecture conversation, not a canvas-tuning conversation. Bring `dataverse-architect` and `architect` in.
- **PCF component is the bottleneck** → `pcf-developer`.

Always pair this skill's findings with the `power-platform-tester` agent for repeatable load/responsiveness assertions before declaring "fixed."
