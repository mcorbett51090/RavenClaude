# DAX measure correctness — the evaluation-context body for authoring measures that are right

> **Last reviewed:** 2026-06-09. This is the deep DAX-measure-correctness reference for the `power-bi-engineer` agent — the body of knowledge that prevents measures that *run* but return the *wrong number*. DAX authoring is this plugin's job; the `microsoft-fabric` plugin routes DAX authoring here (see [`../../microsoft-fabric/knowledge/dax-measures-for-direct-lake.md`](../../microsoft-fabric/knowledge/dax-measures-for-direct-lake.md) for the Direct Lake storage-mode overlay). Refresh when (a) a Power BI / Fabric release changes DAX semantics (context transition, time-intelligence, `SUMMARIZECOLUMNS` callable-in-iteration, calculation-group precedence have all moved across releases), (b) SQLBI / DAX.guide / Microsoft Learn revise any cited article, or (c) a new measure-correctness failure shape surfaces in production.
>
> **Claim-grounding note.** The ten pre-verified findings in §The one mental model / §CALCULATE & filter modifiers / §Iterators are taken from a 3-vote adversarial deep-research run and cite SQLBI / DAX.guide / Microsoft Learn inline — they are not re-derived from training memory. The gap-topic sections (VAR, time intelligence, relationships, performance, validation, AI failure modes) were grounded against the cited URLs fetched 2026-06-09. Any claim about **version-volatile behavior** carries a `[verify-at-use]` tag — DAX is one of the surfaces Microsoft tightens across releases, and "it worked last year" is not a contract. When a behavioral claim gates a consequential action (a deployed measure, a stakeholder number), cite the this-session check or mark it `[unverified]` and verify before shipping.
>
> **When to read this file.** Before authoring or reviewing any non-trivial measure — especially one that aggregates over a relationship, does a percent-of-total, compares time periods, or filters a multi-column context. Read its companions for the *failure* shapes: [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) (measures that silently **blank** a visual) and [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) (measures that silently return **zero**). This file is the *positive* model — how to write the measure correctly in the first place.

---

## The one mental model

Almost every wrong measure traces to a misunderstanding of **evaluation context**. There are two kinds, and they are not interchangeable.

**Row context** iterates but does **not** filter. It exists only inside a calculated column or an iterator (`FILTER`, `SUMX`, `AVERAGEX`, `ADDCOLUMNS`, …). It gives the expression "the current row" but does **not** restrict which rows other tables see. ([SQLBI — Row context and filter context](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/), [SQLBI — Filter context](https://www.sqlbi.com/articles/filter-context-in-dax/))

**Filter context** restricts which rows are visible. It comes from slicers, the visual's axis/rows, page/report filters, and `CALCULATE` filter arguments. **Only filter context filters data.** A matrix cell is a *filter context*, not a row context.

**Filter context propagates across relationships; row context does not.** Inside a row context (e.g. an iterator), the engine does **not** auto-resolve relationships — you must reach across with `RELATED` (to the one-side) or `RELATEDTABLE` (to the many-side). The #1 LLM trap here is assuming `SUMX(Orders, ...)` can "see" a related dimension column without `RELATED`. ([SQLBI — Row context and filter context](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/), [Endjin — RELATED and RELATEDTABLE](https://endjin.com/blog/2021/03/dax-relationships-related-and-relatedtable), [dax.guide/related](https://dax.guide/related/))

### Context transition — the silent filter

**Context transition** turns the current row context into an equivalent filter context. It needs **both** conditions: an active row context **and** a `CALCULATE` — *explicit, or implicit*. A `CALCULATE` at the top level (no surrounding row context) is a no-op for transition. The dangerous half: because **every measure reference is an implicit `CALCULATE`** (next paragraph), transition can fire where you never *typed* `CALCULATE` — so "I didn't write `CALCULATE`, therefore there's no context transition" is a **false and costly assumption** (our research refuted exactly that over-absolute claim). The correct test is: *is there an active row context, and is there a `CALCULATE` — written or implicit-via-a-measure-call?* ([SQLBI — Understanding context transition](https://www.sqlbi.com/articles/understanding-context-transition-in-dax/), [SQLBI — Context transition explained visually](https://www.sqlbi.com/articles/context-transition-in-dax-explained-visually/))

**Every measure reference is auto-wrapped in an implicit `CALCULATE`.** So invoking a measure *inside* a row context silently triggers context transition — each iterated row gets its own filter context. This is the single largest source of subtle DAX bugs.

```dax
-- This is per-customer-Sales-then-summed, NOT a single Sales over all customers:
Total = SUMX ( Customers, [Sales] )   -- [Sales] transitions per customer row
```

That is sometimes exactly what you want (per-customer-then-sum) and sometimes a performance/correctness trap — know which. ([SQLBI — Understanding context transition](https://www.sqlbi.com/articles/understanding-context-transition-in-dax/))

**Context transition applies only to `CALCULATE`'s first (expression) argument.** The filter arguments of `CALCULATE` evaluate in the *surrounding / original* context, never the transitioned one. ([SQLBI — Context transition and filters in CALCULATE](https://www.sqlbi.com/articles/context-transition-and-filters-in-calculate/))

---

## CALCULATE & filter modifiers

`CALCULATE` is the only function that modifies filter context. Its filter arguments **overwrite (replace)** any existing filter on the *same column* by default — this is the source of a whole class of wrong-total bugs. The modifiers below change that behavior; each has a classic mistake.

| Modifier | What it does | The classic mistake |
|---|---|---|
| *(bare filter arg)* | **Replaces** the existing filter on that column. | A multi-column filter exists (e.g. Year *and* Month from the matrix) and your iterator touches one column — the replace wipes the other, giving SQLBI's "Monthly Average Incorrect" wrong result. Fix with `KEEPFILTERS`. ([SQLBI — Filter context](https://www.sqlbi.com/articles/filter-context-in-dax/)) |
| `KEEPFILTERS(...)` | **Intersects (AND)** the new filter with the existing one instead of replacing it. | Forgetting it on a sub-column filter inside an iteration → the over-write bug above. ([dax.guide/keepfilters](https://dax.guide/keepfilters/), [Learn — KEEPFILTERS](https://learn.microsoft.com/en-us/dax/keepfilters-function-dax), [SQLBI — ALL vs ALLSELECTED vs ALLEXCEPT vs REMOVEFILTERS](https://www.sqlbi.com/articles/all-vs-allselected-vs-allexcept-vs-removefilters/)) |
| `ALL(Table)` / `ALL(Column)` | Removes filters **and returns a table** — usable wherever a table expression is required (e.g. the table arg of `SUMX`). | Reaching for `REMOVEFILTERS` where you need a *table* (see next row). |
| `ALLEXCEPT(T, c1, …)` | Removes all filters on `T` *except* the listed columns. | Listing the wrong "keep" columns — silently keeps a filter you meant to drop. |
| `REMOVEFILTERS(...)` | **Modifier only** — clears filters but **cannot return a table**. | Using it where a table expression is required (e.g. as a `SUMX` first arg) — invalid; use `ALL`. Also: `REMOVEFILTERS(T1, T2)` in one call silently blanks visuals (see [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) §1). ([Learn — REMOVEFILTERS](https://learn.microsoft.com/en-us/dax/removefilters-function-dax), [SQLBI — ALL vs ALLSELECTED…](https://www.sqlbi.com/articles/all-vs-allselected-vs-allexcept-vs-removefilters/)) |
| `ALLSELECTED(...)` | "Visual totals" — ignores filters from *inside* the query (the visual's own grouping) but keeps filters from *outside* (slicers). The **only** function that uses shadow filter contexts. | SQLBI calls it "very dangerous." **Never use it inside an iterator.** It is the top LLM failure for percent-of-total. ([SQLBI — ALL vs ALLSELECTED…](https://www.sqlbi.com/articles/all-vs-allselected-vs-allexcept-vs-removefilters/), [Learn — ALLSELECTED](https://learn.microsoft.com/en-us/dax/allselected-function-dax)) |

**Predicate vs `FILTER(table)` as a filter argument.** A simple boolean predicate `Product[Color] = "Red"` is auto-expanded by the engine to `FILTER(ALL(Product[Color]), Product[Color] = "Red")` — it **replaces** the filter on that one column and touches only that column. A `FILTER(Product, …)` over the *whole table* **intersects** with the existing context (it iterates the rows visible now) and materializes the entire table — generally slower and with different semantics. **Prefer the column predicate** unless you specifically need multi-column / row-by-row logic; wrap in `KEEPFILTERS` when you need intersect-not-replace. ([SQLBI — Filter arguments in CALCULATE](https://www.sqlbi.com/articles/filter-arguments-in-calculate/))

---

## Iterators vs aggregators

A plain aggregator (`SUM`, `AVERAGE`, `MIN`) works on a single column in the current filter context. An **iterator** (`SUMX`, `AVERAGEX`, …) walks a table row by row, creating a **row context** per row, and evaluates an expression that can span columns.

**Reach for `SUMX` when correctness requires per-row arithmetic** that a column-level aggregate cannot express:

```dax
-- WRONG: SUM(Qty) * SUM(Price) is not the revenue — it multiplies two grand totals.
Revenue = SUM ( Sales[Quantity] ) * SUM ( Sales[Net Price] )

-- RIGHT: multiply per row, then sum.
Revenue = SUMX ( Sales, Sales[Quantity] * Sales[Net Price] )
```

**Inside the iterator's row context, relationships do not auto-resolve** — pull related columns with `RELATED` (one-side) or `RELATEDTABLE` (many-side):

```dax
-- Sales fact -> Product dimension (many-to-one): RELATED reaches the one-side.
Revenue with Std Cost =
    SUMX ( Sales, Sales[Quantity] * RELATED ( Product[StandardCost] ) )
```

Two reminders that bite here: (1) referencing a **measure** inside the iterator triggers context transition (§The one mental model) — usually what you want for per-entity-then-aggregate, but know it's happening; (2) **`REMOVEFILTERS` cannot be the table argument** of `SUMX` — use `ALL`. ([SQLBI — Row context and filter context](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/), [dax.guide/related](https://dax.guide/related/))

---

## VAR semantics

> Grounded against [SQLBI — Variables in DAX](https://www.sqlbi.com/articles/variables-in-dax/) (fetched 2026-06-09).

**A DAX variable is a constant: it is evaluated once, at the point and context where it is *defined*, not where it is *used*.** SQLBI's phrasing: "A DAX variable is indeed a constant … computed once and never recomputed, regardless of subsequent filter context changes." Moving a sub-expression into a `VAR` is only safe **if that sub-expression was computed in the same filter context** as where you reference it.

The accuracy bug — a variable does **not** recompute inside a later `CALCULATE`:

```dax
-- WRONG: returns 1. The variable captured Sales in the ORIGINAL context;
-- the CALCULATE(..., ALL(Product)) cannot recompute a constant.
% of Product Total =
VAR SalesAmount = SUMX ( Sales, Sales[Quantity] * Sales[Net Price] )
RETURN DIVIDE ( SalesAmount, CALCULATE ( SalesAmount, ALL ( Product ) ) )

-- RIGHT: the denominator must re-run the expression under its own context.
% of Product Total =
VAR _Sales    = SUMX ( Sales, Sales[Quantity] * Sales[Net Price] )
VAR _AllSales = CALCULATE ( SUMX ( Sales, Sales[Quantity] * Sales[Net Price] ), ALL ( Product ) )
RETURN DIVIDE ( _Sales, _AllSales )
```

**Correct, valuable uses:** readability (semantic names for sub-steps), debugging (temporarily `RETURN` a variable to inspect it), and performance (a sub-expression computed once is reused, not re-evaluated). The discipline: only `VAR`-extract a sub-expression you've confirmed is context-stable at every reference site. Variables also evaluate **lazily** — an unreferenced `VAR` is never computed.

---

## DIVIDE, BLANK, IF vs SWITCH(TRUE())

**Always use `DIVIDE(num, denom [, alt])` for division**, not the `/` operator. `DIVIDE` is the safe, query-optimized form: it returns `BLANK()` (or your `alt`) on a zero or blank denominator by default, and is faster than a hand-rolled `IF` guard. ([Learn — Use DIVIDE, not the divide operator](https://learn.microsoft.com/en-us/dax/best-practices/dax-divide-function-operator), [SQLBI — DIVIDE performance](https://www.sqlbi.com/articles/divide-performance/))

```dax
-- WRONG: divide-by-zero error / clutters with a manual guard.
Margin % = IF ( SUM ( Sales[Revenue] ) = 0, BLANK(), [Profit] / [Revenue] )

-- RIGHT: DIVIDE handles zero/blank denominators and optimizes.
Margin % = DIVIDE ( [Profit], [Revenue] )
```

**BLANK propagation.** `BLANK` behaves as `0` in *addition/subtraction* and as empty in *multiplication* (`BLANK * x = BLANK`), and comparisons coerce it (`BLANK = 0` is **TRUE**) — so a measure that returns `BLANK` can silently read as `0` downstream (this is exactly the silent-zero shape in [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md)). Be deliberate about whether "no data" should surface as blank (preferred — keeps the visual honest) or as an explicit value.

**`SWITCH(TRUE(), …)` over nested `IF`.** For more than two branches, `SWITCH(TRUE(), cond1, res1, cond2, res2, …, else)` reads linearly and lowers cognitive load versus deeply nested `IF`. The **first matching condition wins**, so order matters — put the most-likely / most-specific conditions first; the default (final) value is `BLANK` if omitted, and all result branches **must share one data type**. ([dax.guide/switch](https://dax.guide/switch/))

---

## Time intelligence correctness

> Grounded against [SQLBI — Mark as Date Table](https://www.sqlbi.com/articles/mark-as-date-table/), [Learn — DATEADD](https://learn.microsoft.com/en-us/dax/dateadd-function-dax), and [DAX Patterns — Standard time-related calculations](https://www.daxpatterns.com/standard-time-related-calculations/) (fetched 2026-06-09).

Time intelligence is the area where "the measure runs, the number is wrong" happens most. Two preconditions are non-negotiable:

1. **A proper, complete (contiguous) date table** — one row per day, **all** consecutive dates from Jan 1 of the first year to Dec 31 of the last, no gaps, a unique `Date`/`DateTime` column with no time component. ([DAX Patterns](https://www.daxpatterns.com/standard-time-related-calculations/))
2. **Mark as Date Table.** Marking adds an implicit `REMOVEFILTERS` over the Date table whenever the date column is filtered, so a time-intelligence filter doesn't leave a stale filter on another date column (e.g. `Date[Calendar Year]`) — SQLBI: without it "the filter produced by `DATESYTD` only filters `Date[Date]`; it does not overwrite the outer filter on `Date[Calendar Year]`," producing wrong results. (If the relationship uses a true Date-typed column, DAX applies the `REMOVEFILTERS` automatically; integer date keys do **not** get this — mark the table.) ([SQLBI — Mark as Date Table](https://www.sqlbi.com/articles/mark-as-date-table/)) `[verify-at-use]`

Function pitfalls:

- **`TOTALYTD` vs `DATESYTD`** produce identical results — `TOTALYTD` is syntactic sugar over `DATESYTD`. Pick either for clarity. ([DAX Patterns](https://www.daxpatterns.com/standard-time-related-calculations/))
- **`SAMEPERIODLASTYEAR` internally translates to `DATEADD`** — no performance advantage; `DATEADD` is just more flexible for custom offsets. ([DAX Patterns](https://www.daxpatterns.com/standard-time-related-calculations/))
- **`DATEADD` requires a contiguous set of dates in the current filter context.** Microsoft Learn: "If the date column syntax is used and the dates in the current context do not form a contiguous interval, the function returns an error." A partial/filtered date range (e.g. a slicer that selects scattered days) breaks it. ([Learn — DATEADD](https://learn.microsoft.com/en-us/dax/dateadd-function-dax)) `[verify-at-use]`
- **Use table-valued time functions as filters, not scalar ones** — `ENDOFMONTH` (table) not `EOMONTH` (scalar) inside `CALCULATE`. ([DAX Patterns](https://www.daxpatterns.com/standard-time-related-calculations/))
- **Fiscal calendars:** standard functions accept a year-end-date argument but it must be a **constant literal**; the fiscal year must start on the same date each year; quarters are fixed to Jan/Apr/Jul/Oct boundaries; a March-1 start has a documented leap-year bug. For anything beyond a simple fiscal offset, use a custom calendar table + week/period columns. ([DAX Patterns](https://www.daxpatterns.com/standard-time-related-calculations/)) `[verify-at-use]`

---

## Relationships that change measure results

> Grounded against [SQLBI — Bidirectional relationships and ambiguity](https://www.sqlbi.com/articles/bidirectional-relationships-and-ambiguity-in-dax/), [dax.guide/crossfilter](https://dax.guide/crossfilter/), and [SQLBI — DAX limitations with inactive relationships and RLS](https://www.sqlbi.com/articles/dax-limitations-with-inactive-relationships-and-row-level-security-rls/) (fetched 2026-06-09).

The same measure can return different numbers depending on which relationship is active and how it cross-filters — and the author can't see it in the DAX.

- **Active vs inactive relationships.** A model allows one *active* path between two tables; extra paths are *inactive*. To use an inactive relationship for one measure, wrap the calc in `CALCULATE ( …, USERELATIONSHIP ( fact[colA], dim[colB] ) )`. Forgetting it means the measure quietly uses the *active* relationship and the number is for the wrong join (the role-playing-dimension trap: an Orders fact with OrderDate **and** ShipDate both joined to Date — only one is active). ([SQLBI — Inactive relationships and RLS](https://www.sqlbi.com/articles/dax-limitations-with-inactive-relationships-and-row-level-security-rls/))
- **`CROSSFILTER` changes the *direction* of an already-active relationship** within a `CALCULATE` (`None`/`OneWay`/`Both`/`OneWay_RightFiltersLeft`/`OneWay_LeftFiltersRight`). It does **not** activate an inactive relationship — that's `USERELATIONSHIP`'s job. The two are distinct tools. ([dax.guide/crossfilter](https://dax.guide/crossfilter/))
- **Bidirectional cross-filter is a hazard, not a default.** It creates *ambiguity* when more than one path connects two tables (e.g. Date→Sales→Product→Purchases vs a direct Date→Purchases); the engine runs a disambiguation algorithm that SQLBI calls "extremely complex … for a human" — and different filter combinations then yield different, unpredictable numbers. SQLBI's rule: don't reach for bidirectional just to sync slicers ("if you need to kill ants … you do not turn on the Death Star"); prefer a targeted `CROSSFILTER` in the specific measure, or a slicer-sync pattern that doesn't change the model. ([SQLBI — Bidirectional relationships and ambiguity](https://www.sqlbi.com/articles/bidirectional-relationships-and-ambiguity-in-dax/))
- **RLS + inactive-relationship interaction:** `CROSSFILTER` cannot change default propagation from a table that has RLS applied; inactive relationships have documented limits under RLS — route any RLS-touching measure through `ravenclaude-core/security-reviewer`. ([SQLBI — Inactive relationships and RLS](https://www.sqlbi.com/articles/dax-limitations-with-inactive-relationships-and-row-level-security-rls/)) `[verify-at-use]`

---

## Performance ↔ correctness

> Grounded against [SQLBI — Filter arguments in CALCULATE](https://www.sqlbi.com/articles/filter-arguments-in-calculate/), [SQLBI — Optimizing DAX expressions involving multiple measures](https://www.sqlbi.com/articles/optimizing-dax-expressions-involving-multiple-measures/), and [SQLBI — Introducing calculation groups](https://www.sqlbi.com/articles/introducing-calculation-groups/) (fetched 2026-06-09).

In DAX, the fast form and the correct form are usually the same form — but not always, so make the choice deliberately.

- **Boolean column predicate over `FILTER(table)` in `CALCULATE`.** `CALCULATE ( [Sales], Product[Color] = "Red" )` lets the engine push a column filter; `CALCULATE ( [Sales], FILTER ( Product, Product[Color] = "Red" ) )` materializes the whole table and changes the semantics (intersect vs replace). Use the predicate; use `FILTER` only for genuine multi-column / measure-based row logic, and wrap in `KEEPFILTERS` if you need intersect-not-replace. ([SQLBI — Filter arguments in CALCULATE](https://www.sqlbi.com/articles/filter-arguments-in-calculate/))
- **Avoid unnecessary context transition.** Calling a measure inside a high-cardinality iterator transitions per row (§The one mental model) — sometimes required, often a hidden cost. If you don't need per-row entity scope, aggregate directly.
- **`CALCULATE ( SUM ( … ) )` vs `SUMX`.** `CALCULATE(SUM(col))` is a single column aggregation in a modified filter context; `SUMX` is a row-by-row iteration. They are **not interchangeable** — `SUMX` is required when the per-row expression spans columns (§Iterators); `CALCULATE(SUM())` is cheaper when you only need one column under a different filter. Pick by what the math needs, then by cost.
- **Calculation groups for measure families.** When you'd otherwise author N base measures × M variants (YTD, QTD, PY, …), a **calculation group** defines each variant *once* as a calculation item using `SELECTEDMEASURE()` as the placeholder. This collapses the N×M explosion to N+M, and — the correctness win — the time-intelligence logic lives in one place instead of being copy-pasted (and drifting) across dozens of measures. Mind **precedence** when multiple calculation groups stack. ([SQLBI — Introducing calculation groups](https://www.sqlbi.com/articles/introducing-calculation-groups/)) `[verify-at-use]`

---

## Validating a measure

> Grounded against [SQLBI — Debugging DAX measures in Power BI](https://www.sqlbi.com/articles/debugging-dax-measures-in-power-bi/) and [SQLBI — SUMMARIZECOLUMNS best practices](https://www.sqlbi.com/articles/summarizecolumns-best-practices/) (fetched 2026-06-09).

Never trust a measure that "looks right" in the editor — run it against the live model and read the actual rows.

- **`EVALUATE` + `SUMMARIZECOLUMNS` is the workhorse test.** Group by the dimension(s) the visual uses and project the measure; the result table is the visual's data, decoupled from rendering:

  ```dax
  EVALUATE
  SUMMARIZECOLUMNS (
      Product[Brand],
      "Sales",   [Sales Amount],
      "Margin %", [Margin %]
  )
  ```

  `SUMMARIZECOLUMNS` auto-determines how to scan the model (no source table needed) and handles limited relationships, which `SUMMARIZE` cannot. **Do not place filter arguments directly inside `SUMMARIZECOLUMNS`** — its filter/group-by interaction has "very complex semantics"; wrap it in `CALCULATETABLE(... , TREATAS(...))` instead. Historically it could not be called inside an iteration; that restriction was **lifted in 2025** `[verify-at-use]`. ([SQLBI — SUMMARIZECOLUMNS best practices](https://www.sqlbi.com/articles/summarizecolumns-best-practices/))
- **`DEFINE MEASURE … EVALUATE …`** lets you test a candidate measure (or a modified version) against the live model **without** changing the model — the safe way to validate before committing.
- **Tools:** DAX Studio (capture the visual's query from Performance Analyzer, run/modify it safely, read server timings), the DAX query view in Power BI Desktop, Tabular Editor 3's DAX Debugger (step execution with visible filter context — "the only tool providing a real DAX Debugger"), and `EVALUATEANDLOG` for block-level inspection. ([SQLBI — Debugging DAX measures](https://www.sqlbi.com/articles/debugging-dax-measures-in-power-bi/))
- **`INFO.*` functions** (e.g. `INFO.MEASURES()`, `INFO.TABLES()`, `INFO.RELATIONSHIPS()`) query the model's own metadata via DAX — use them to confirm a measure, relationship, or table exists and is shaped as the DAX assumes, rather than eyeballing the model pane. `[verify-at-use]`
- **Verify filter strings match the data.** The single highest-yield check (see [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md)): before shipping any `Col = "literal"` filter, run `EVALUATE SUMMARIZE(T, T[Col], "n", COUNTROWS(T))` and confirm the literal is one of the returned values. Diagnose against the deployed model via the Fabric REST `executeQueries` endpoint — see [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md).

---

## How AI-generated DAX goes wrong (and the guardrails)

> Grounded against [Learn — Write DAX queries with Copilot](https://learn.microsoft.com/en-us/dax/dax-copilot) and [Learn — Use Copilot with semantic models](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models) (fetched 2026-06-09).

Microsoft is explicit that AI-generated DAX (Copilot or any LLM) can be wrong, and that the author **must validate and understand it before use** — "while the suggested code might work in the initial DAX query, in a different filter context of your report, it could produce unexpected or incorrect results." The recurring failure modes, mapped to the sections above:

| AI failure mode | Where it goes wrong | Guardrail |
|---|---|---|
| **Hallucinated / newer functions** | LLMs invent functions or misuse recently-added ones — Learn warns AI is "more likely to make mistakes with newer DAX functions or syntax." | Validate every function against [dax.guide](https://dax.guide/) / [Learn](https://learn.microsoft.com/en-us/dax/); for new functions, author first, then ask AI to refine. |
| **Wrong context-transition assumption** | Assumes a measure inside an iterator behaves like a plain aggregate, or that a relationship auto-resolves in a row context. | Re-derive against §The one mental model; test the per-group result with `SUMMARIZECOLUMNS`. |
| **Variable misuse** | Learn: "Copilot might try to filter or group a variable that's already been declared, which isn't possible" — and the captured-context bug (§VAR semantics). | Confirm each `VAR` is context-stable at every reference; check it's not being treated as a re-evaluatable table. |
| **ALLSELECTED misuse** | The top LLM failure for percent-of-total — reaches for `ALLSELECTED` (or sticks it in an iterator) where `ALL`/`REMOVEFILTERS` is correct. | §CALCULATE & filter modifiers — never inside an iterator; verify the denominator's filter scope explicitly. |
| **REMOVEFILTERS-as-table** | Uses `REMOVEFILTERS` where a table expression is required (e.g. `SUMX` first arg). | Swap to `ALL`. |
| **Format-string / scale errors** | A 0–100 value formatted `0.0%` reads 100× wrong; AI rarely checks the value's scale. | §DIVIDE/BLANK and [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) §3 (`0.0\%` for 0–100, `0.0%` for 0–1). |

Two structural notes from Learn that change the odds: Copilot's DAX-query path runs a **DAX parser post-check** (reduces *syntax* hallucinations, not *semantic* ones), and a **well-described model** (clear names, measure descriptions ≤200 chars used, hidden unused fields, marked date table) materially improves AI output quality — but **none of this removes the human-validation requirement.** The model is nondeterministic; the same prompt can return different DAX. Treat AI-generated DAX as a *draft to validate*, never a *measure to ship*.

---

## Common wrong → correct rewrite

| # | Wrong | Correct | Why |
|---|---|---|---|
| 1 | `SUMX ( Sales, ..., REMOVEFILTERS ( Product ) )` (as the table arg) | `SUMX ( ALL ( Product ), ... )` | `REMOVEFILTERS` is modifier-only — can't return a table. |
| 2 | `DIVIDE ( [Sales], CALCULATE ( [Sales], ALLSELECTED ( Product ) ) )` *inside an iterator* | Compute the visual-total denominator at measure top level, never per-iterated-row | `ALLSELECTED` uses shadow contexts; inside iteration it's "very dangerous" and wrong. |
| 3 | `CALCULATE ( [Avg], Date[Month] = EARLIER(...) )` over a matrix with Year+Month | `CALCULATE ( [Avg], KEEPFILTERS ( Date[Month] = ... ) )` | Bare filter arg replaces the Month filter and wipes the Year filter (the "Monthly Average Incorrect" bug). |
| 4 | `[Profit] / [Revenue]` | `DIVIDE ( [Profit], [Revenue] )` | `/` errors / mishandles zero-blank denominators; `DIVIDE` is safe + optimized. |
| 5 | `SUMX ( Customers, [Sales] )` *expecting a single total* | `[Sales]` (or `CALCULATE ( [Sales] )` if no per-customer scope needed) | The measure reference transitions context per customer — silently per-customer-then-sum. |
| 6 | `IF ( [Revenue] = 0, BLANK(), [Profit] / [Revenue] )` | `DIVIDE ( [Profit], [Revenue] )` | The `IF` guard is the slower, wordier `DIVIDE`. |
| 7 | `CALCULATE ( [Sales] )` *expecting the OrderDate join when ShipDate is active* | `CALCULATE ( [Sales], USERELATIONSHIP ( Sales[OrderDate], Date[Date] ) )` | Without `USERELATIONSHIP` the measure quietly uses the active (wrong) relationship. |
| 8 | `CALCULATE ( [Sales], DATEADD ( Date[Date], -1, YEAR ) )` over a non-marked / gappy date table | Mark as Date Table + ensure a contiguous date column, then `DATEADD` | `DATEADD` errors / misfires on a non-contiguous context; marking adds the needed `REMOVEFILTERS`. |
| 9 | `SUM ( Sales[Qty] ) * SUM ( Sales[Price] )` | `SUMX ( Sales, Sales[Qty] * Sales[Price] )` | Multiplying two grand totals ≠ summing per-row products. |
| 10 | `SUMX ( Orders, Orders[Qty] * Product[StdCost] )` | `SUMX ( Orders, Orders[Qty] * RELATED ( Product[StdCost] ) )` | Relationships don't auto-resolve in a row context — reach with `RELATED`. |

---

## Measure-authoring accuracy checklist

Run this before committing any non-trivial measure:

- [ ] **Context named.** I know whether each sub-expression evaluates in a *row* context or a *filter* context, and whether any measure reference inside an iterator is *meant* to trigger context transition.
- [ ] **Relationships reached explicitly.** Every cross-table column inside a row context uses `RELATED` / `RELATEDTABLE`; no assumption that a relationship auto-resolves inside `SUMX`.
- [ ] **Right relationship.** If a role-playing/inactive relationship is intended, the measure wraps it in `USERELATIONSHIP`; cross-filter direction changes use `CROSSFILTER`; no accidental reliance on a bidirectional path.
- [ ] **Filter modifier intent.** Each `CALCULATE` filter arg is *meant* to replace (bare) vs intersect (`KEEPFILTERS`); `ALL`/`ALLEXCEPT`/`REMOVEFILTERS` chosen correctly; **no `ALLSELECTED` inside an iterator**; **no `REMOVEFILTERS` where a table is required**.
- [ ] **Predicate not FILTER(table)** unless multi-column/row logic genuinely needs it.
- [ ] **Variables are context-stable** at every reference site (not expected to recompute inside a later `CALCULATE`).
- [ ] **Division via `DIVIDE`**, not `/`; BLANK-vs-0 behavior downstream is intentional.
- [ ] **Branching via `SWITCH(TRUE())`** for >2 cases, conditions ordered most-specific-first, all branches one data type.
- [ ] **Time intelligence preconditions met:** date table is marked + contiguous; `DATEADD` has a contiguous context; table-valued time functions used as filters.
- [ ] **Filter strings verified against live data** (`EVALUATE SUMMARIZE`/`SUMMARIZECOLUMNS`) — no `Col = "literal"` that matches zero rows.
- [ ] **Tested against the model**, not just the editor — `EVALUATE SUMMARIZECOLUMNS` (or `DEFINE MEASURE … EVALUATE`) returns the expected rows at the grain the visual uses.
- [ ] **AI-generated DAX validated**, not shipped raw — every function confirmed real, context behavior re-derived, output tested in the report's actual filter context.

---

## Cross-links

- **Measures that silently *blank* a visual** (REMOVEFILTERS arity, CONCATENATEX over mixed contexts, format-string scale, string-type measures, entity-vs-population context): [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md).
- **Measures that silently return *zero*** (hardcoded string filter matches no rows; the `Domain` calculated-column fix; the `EVALUATE SUMMARIZE` diagnosis): [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md).
- **REST-first diagnosis of a deployed measure** (`executeQueries` against the live model — the first debugging move): [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md).
- **Direct Lake storage-mode overlay for DAX measures** (forward link — the `microsoft-fabric` plugin routes DAX authoring here; that file carries the Direct-Lake-specific measure considerations): [`../../microsoft-fabric/knowledge/dax-measures-for-direct-lake.md`](../../microsoft-fabric/knowledge/dax-measures-for-direct-lake.md).
- **TMDL measure-metadata discipline** (description / formatString / displayFolder): [`../best-practices/enforce-measure-metadata.md`](../best-practices/enforce-measure-metadata.md).

---

## Owners

- **Primary:** `power-bi-engineer` (DAX authoring, measure design, semantic model correctness).
- **Secondary:** `power-platform-tester` (the regression discipline that proves measure correctness against the live model before a release — DAX semantic correctness is in this agent's mandate).
