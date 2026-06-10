# DAX Measure Accuracy — Deep Research Report

> **Date:** 2026-06-09
> **Provenance:** `deep-research` workflow run `wf_ce9b6c11-71a` — 6 search angles, 30 sources fetched, 143 claims extracted, top 25 adversarially verified (3-vote, need 2/3 to refute), 24 confirmed / 1 refuted, synthesized to 10.
> **Purpose:** ground a measure-authoring-accuracy improvement for `power-platform/power-bi-engineer` (DAX authoring home) and `microsoft-fabric/fabric-semantic-model-engineer` (Direct Lake measures).
> **Source quality:** uniformly high — SQLBI (Russo/Ferrari), Microsoft Learn (reconfirmed Jan 2026), DAX.guide, with practitioner corroboration. Core semantics below are **version-stable** engine behavior, NOT version-volatile (exception: Direct Lake specifics — see gap list).

---

## Part A — VERIFIED findings (3-0 confirmed)

### 1. The root cause of most wrong measures: row context ≠ filter context
Row context **iterates but does not filter** the model; only filter context restricts visible rows. Row context exists ONLY in calculated columns and inside iterators (`FILTER`/`SUMX`/`AVERAGEX`/`ADDCOLUMNS`), on a single row at a time; filter context is set for the whole formula and governs which rows are visible and how data aggregates.
*Sources: sqlbi.com/articles/row-context-and-filter-context-in-dax, /filter-context-in-dax, /understanding-context-transition-in-dax*

### 2. Filter context propagates across relationships; row context does NOT
Filter context traverses relationships per the cross-filter direction. Row context does **not** propagate — to cross a relationship inside a row context you must use `RELATED` (to the one-side parent) or `RELATEDTABLE` (to the many-side). **Top LLM trap:** assuming relationships auto-resolve inside `SUMX`.
*Sources: sqlbi.com/articles/row-context-and-filter-context-in-dax, endjin.com/blog/related-and-related-table-in-dax, dax.guide/related*

### 3. Context transition needs BOTH a CALCULATE *and* an active row context
Context transition converts an active row context into an equivalent filter. It's executed by `CALCULATE`/`CALCULATETABLE` (or any syntax that implicitly invokes them) — **but only when a row context is present**. `CALCULATE` at the top level (no row context) = no transition (no-op). ⚠️ The over-absolute claim "no CALCULATE → no transition, full stop" was **REFUTED 0-3** — it needs both conditions. Matrix cells are filter contexts, not row contexts ("no iteration, no row context").
*Sources: sqlbi.com/articles/understanding-context-transition-in-dax, /context-transition-in-dax-explained-visually, /context-transition-and-filters-in-calculate*

### 4. Every measure reference is auto-wrapped in an implicit CALCULATE
Invoking a measure inside a row context (calc column or iterator) **silently triggers context transition** — each iterated row gets its own filter context. This is the **#1 source of subtle measure bugs**. It's why `SUMX(Customers, [Sales])` computes per-customer-then-sums (often what you want) — and why an LLM pasting a measure into an iterator without intending transition produces wrong numbers.
*Sources: sqlbi.com/articles/understanding-context-transition-in-dax, /context-transition-in-dax-explained-visually*

### 5. Context transition applies ONLY to CALCULATE's first (expression) argument
Filter arguments are evaluated in the **surrounding/original** context (plus any retained outer row context) — they do NOT see the transitioned filter context. This is why `CALCULATE([Sales], 'Date'[Year] = MAX('Date'[Year]))` works: the filter arg reads the outer context.
*Source: sqlbi.com/articles/context-transition-and-filters-in-calculate*

### 6. CALCULATE filter args OVERWRITE by default (same-column replace)
By default the context-transition filter (and `CALCULATE` filter args) **overwrite** existing filters on the same columns. This silently produces wrong results when an arbitrary-shaped filter spans multiple columns and the iterator touches only one (SQLBI's "Monthly Average Incorrect" example: iterating Month overwrites only Month, leaves Year intact, inflates the result). `KEEPFILTERS` is the corrective.
*Sources: sqlbi.com/articles/filter-context-in-dax, /context-transition-in-dax-explained-visually*

### 7. KEEPFILTERS = intersect instead of replace
`KEEPFILTERS` changes `CALCULATE`'s default replace to **intersection** (AND): the filter arg is combined with the existing filter on the same columns rather than replacing it. MS worked example: outer `WA||BC` intersected with `KEEPFILTERS(WA||OR)` collapses to `WA`.
*Sources: dax.guide/keepfilters, learn.microsoft.com/dax/keepfilters-function-dax (updated 2026-01-22), sqlbi.com/articles/all-vs-allselected-vs-allexcept-vs-removefilters*

### 8. REMOVEFILTERS is modifier-only; ALL is dual-role
`REMOVEFILTERS` is an alias for `ALL` but can **only** be used as a `CALCULATE` filter modifier — it **cannot return a table**. Where a table expression is required (a `SUMX`/iterator argument) you must use `ALL`. `SUMX(REMOVEFILTERS(Product), [Sales])` fails; `ALL` substitutes. **Breaks naive AI-generated DAX.** (Reinforces the repo's existing `pbir-dax-pitfalls.md` §1 on REMOVEFILTERS arity.)
*Sources: learn.microsoft.com/dax/removefilters-function-dax (updated 2026-01-13), sqlbi.com/articles/all-vs-allselected-vs-allexcept-vs-removefilters*

### 9. ALLSELECTED is the classic gotcha — never inside an iteration
`ALLSELECTED` ignores filters applied *inside* the query while keeping *outside* filters (the "visual totals" pattern). SQLBI: "very dangerous if you do not follow best practices," it's "the only DAX function that leverages shadow filter contexts," and **"Never use ALLSELECTED inside an iteration."** Top LLM failure: reaching for `ALLSELECTED` for percent-of-total without understanding shadow contexts.
*Sources: sqlbi.com/articles/all-vs-allselected-vs-allexcept-vs-removefilters, learn.microsoft.com/dax/allselected-function-dax*

### 10. Use DIVIDE for division (safe + optimized)
`DIVIDE(num, denom [, alt])` safely handles a zero/BLANK denominator (returns BLANK by default, or `alt`), replacing `IF(denom<>0, num/denom, BLANK())`. MS Learn: "better optimized for testing the denominator value than IF... the performance gain is significant since checking for division by zero is expensive." (SQLBI caveat: DIVIDE vs native `/` can differ on overflow/infinity and DIVIDE forces the Formula Engine — a separate perf nuance.)
*Sources: learn.microsoft.com/dax/best-practices/dax-divide-function-operator, sqlbi.com/blog/marco/2014/07/24/divide-vs-division-operator-in-dax, sqlbi.com/articles/divide-performance*

---

## Part B — REFUTED (must NOT enter any deliverable)
- ❌ "Context transition is invoked exclusively by CALCULATE; if CALCULATE is not present, no transition occurs." (0-3) — correct semantics require BOTH a CALCULATE/implicit-measure-wrap AND an active row context (see finding #3).

---

## Part C — COVERAGE GAPS (sources identified, claims NOT yet adversarially verified)
Treat as **unresearched here**, not "no findings." Authoritative sources were fetched for each; specific claims fell outside the top-25 verification budget. To ground these for the plugin, fetch the listed sources directly at authoring time.

| Brief item | Topic | Identified authoritative sources |
|---|---|---|
| 3 | Iterators vs aggregators depth (SUMX-required-for-correctness; x-aggregator + RELATED) | (covered indirectly by #2, #4) — SQLBI iterators articles |
| 4 | **VAR semantics** — evaluated at DEFINITION site, not use site (major accuracy + LLM trap) | SQLBI variables articles (needs dedicated pass) |
| 5 | IF vs SWITCH(TRUE()); BLANK propagation nuances | DAX.guide, SQLBI |
| 6 | **Time intelligence** — mark-as-date-table, contiguous date table, TOTALYTD vs DATESYTD, SAMEPERIODLASTYEAR/DATEADD, fiscal | sqlbi.com/articles/mark-as-date-table, learn.microsoft.com/dax/dateadd-function-dax, daxpatterns.com/standard-time-related-calculations |
| 7 | **Relationships** — USERELATIONSHIP, bidirectional ambiguity, CROSSFILTER, role-playing | sqlbi.com/articles/bidirectional-relationships-and-ambiguity-in-dax, dax.guide/crossfilter, sqlbi.com/articles/dax-limitations-with-inactive-relationships-and-row-level-security-rls |
| 8 | Performance-correctness — boolean predicate vs FILTER(table), calculation groups | sqlbi.com/articles/filter-arguments-in-calculate, /optimizing-dax-expressions-involving-multiple-measures, /introducing-calculation-groups, /formula-engine-and-storage-engine-in-dax |
| 9 | **Direct Lake DAX** (most version-volatile — mark verify-at-use) | learn.microsoft.com/fabric/fundamentals/direct-lake-develop, /direct-lake-overview, /direct-lake-how-it-works, powerbi blog pure-direct-lake |
| 10 | Validation/testing — EVALUATE+SUMMARIZECOLUMNS, DAX Studio, INFO.* | sqlbi.com/articles/debugging-dax-measures-in-power-bi, /summarizecolumns-best-practices |
| 11 | LLM-failure catalogue (beyond context-transition) + DAX Copilot guardrails | learn.microsoft.com/dax/dax-copilot, learn.microsoft.com/power-bi/create-reports/copilot-semantic-models |

---

## Part D — How this maps to existing repo knowledge
- **Reinforces** `power-platform/knowledge/pbir-dax-pitfalls.md` (REMOVEFILTERS arity = finding #8) and `dax-category-name-mismatch-zero-scores.md` (filter-strings-match-data discipline).
- **Fills the stub** `power-platform/skills/power-bi/resources/dax-patterns-and-performance.md` (~20 lines, no context-transition/CALCULATE-modifier/DIVIDE depth).
- **Net-new** for `microsoft-fabric`: the plugin currently routes DAX authoring OUT to power-bi-engineer (§10 seam) and has no measure-correctness content beyond "measures-not-calc-columns."
