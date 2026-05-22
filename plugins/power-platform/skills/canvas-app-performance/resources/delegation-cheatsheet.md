# Delegation Cheatsheet — Canvas + Power Fx (2026)

Quick reference for which operators delegate against which sources. Always defer to the blue squiggle in Studio — if Power Fx warns, it doesn't delegate, regardless of what this doc says. Microsoft's tables drift; this doc is a starting point.

## Dataverse (canonical reference for delegation depth)

| Function / operator | Delegates? | Notes |
|---|---|---|
| `Filter` with `=`, `<>`, `<`, `<=`, `>`, `>=` | Yes | On indexed columns; non-indexed still works but slower |
| `Filter` with `StartsWith`, `EndsWith` | Yes (StartsWith always; EndsWith newer) | EndsWith introduced via Dataverse Web API enhancements; verify with blue squiggle |
| `Filter` with `In` | Yes for option sets and lookups; partial for text | Mind the IN-list size; ~100 items typical ceiling |
| `Search` | Yes | Across the columns you specify |
| `LookUp` | Yes | Same operator rules as Filter |
| `Sort`, `SortByColumns` | Yes | One column delegates cleanly; multi-column is partial |
| `Distinct` | Yes on single column | Multi-column distinct typically not delegable |
| `Sum`, `Count`, `CountRows`, `Average`, `Min`, `Max` over Filter | Yes via `CountRows(Filter(...))`, `Sum(Filter(...), col)` | Newer canvas runtimes; older apps need updating |
| `IsBlank()` in predicate | Partial — yes on specific column types; no on others | Test |
| Complex `If` inside predicate | No | Refactor — split into multiple Filters and Concat |
| Joins / multi-table queries | Use a Dataverse view, bind to the view | Power Fx does not delegate cross-table |

## SharePoint

| Function / operator | Delegates? | Notes |
|---|---|---|
| `Filter` with `=`, `<>` on indexed Text/Choice/Number | Yes | **Index the column** — non-indexed = client-side filter = 500-row cap |
| `Filter` with `StartsWith` on Text | Yes | Indexed columns only for best perf |
| `Filter` on Lookup columns | Partial | Use the `.Id` not the display |
| `Search` | No | Pull into ClearCollect, search locally |
| `Sort` on indexed column | Yes | Non-indexed = client-side |
| `LookUp` | Same rules as Filter | |
| Boolean (Yes/No) columns | Yes | But check current platform notes — historically flaky |
| Person/Group columns | Partial | Filter by Claims/Email yes; by Title no |
| Multi-value choice / lookup | No | Cannot delegate predicates on multi-value columns |

## SQL Server (on-prem via gateway or Azure SQL)

| Function / operator | Delegates? | Notes |
|---|---|---|
| `Filter` with most operators | Yes | Including `In`, `StartsWith` |
| `Sort` | Yes | |
| `Search` | No | |
| Computed columns | Partial | Filter delegates against the computed value but cannot push the expression in |
| Views | Yes | Bind to a SQL view rather than Filter-on-Filter chains |
| Stored procedures | Use as actions, not as gallery sources | |

## Excel (OneDrive Excel / OneDrive for Business Excel table)

| Function / operator | Delegates? | Notes |
|---|---|---|
| Anything | No | Excel doesn't delegate. 500-row hard cap. Use as read-only reference data only. If your data is in Excel and your app is non-trivial, the answer is "move to Dataverse first." |

## Patterns to work past the 500-row ceiling (when delegation isn't possible)

### Paged ClearCollect

```powerfx
// On a screen OnVisible, load up to 4000 rows in 2 pages
ClearCollect(
    colData,
    Filter('My Table', ID <= 2000)
);
Collect(
    colData,
    Filter('My Table', ID > 2000 && ID <= 4000)
);
```

Works only if the source delegates the `Filter` (otherwise each call still truncates at 500). The pagination key (`ID` above) must be the source's actual primary key or an indexed monotonically increasing column.

### Push to a flow

If you need >4000 rows for an in-app operation, the right answer is usually:
1. Power Automate flow with the Dataverse "List Rows" action (supports paging up to the platform limit).
2. Flow returns the rows to the canvas app (or writes them to a collection-friendly intermediate).
3. Canvas app reads the returned rows.

Cost: premium flow, latency on the round-trip. But it's the supported pattern past the canvas runtime's ceiling.

### Reconsider the UX

The unspoken option: most "I need all 50,000 rows in a Gallery" requirements are users asking for a search experience, not a browse experience. A Search-first UX with delegable Filter on 1-3 fields is faster, more usable, and avoids the ceiling entirely.

## How to verify delegation in 30 seconds

1. Open the canvas app in Studio.
2. Look at the expression in the property bar.
3. If there's a blue squiggle, hover — Power Fx tells you exactly which part of the expression isn't delegable.
4. Fix or accept the cap (only if you can prove the source will never exceed the cap).
5. **Don't** raise the in-app row limit from 500 to 2000 as a "fix" — it's a band-aid that buys you time, not a solution. The next user who imports more rows will hit it again.
