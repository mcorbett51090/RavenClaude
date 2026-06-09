# DAX measures for Direct Lake — the everyday-correctness spine

> **Last reviewed:** 2026-06-09 · **Confidence:** high for the DAX accuracy spine (pre-verified against SQLBI + Microsoft Learn `dax/*`); high for Direct Lake behavior (first-party Microsoft Learn, retrieved 2026-06-09).
> **Refresh trigger:** re-read when authoring or reviewing a DAX measure on a Direct Lake model; **re-verify the Direct-Lake-tagged claims every quarter** — Fabric ships monthly and calculated-column/table support on Direct Lake is currently **preview** (house opinion #9). Anything that gates an irreversible model change must be re-checked at use.

This file gives `fabric-semantic-model-engineer` the **accuracy spine** for authoring *correct* everyday DAX measures (aggregations, ratios, simple time intelligence) on a Direct Lake semantic model, plus the Direct-Lake-specific facts that change *where the math lives*. It is deliberately tighter than the deep authoring file — **advanced DAX (complex measure libraries, calculation groups, perf tuning, server-timings) escalates to `power-platform/power-bi-engineer`** (the §10 seam, restated below).

**Read this when:** you are writing or reviewing a measure on a Direct Lake model, deciding whether logic belongs in the measure or in the gold Delta table, or diagnosing a measure that returns a surprising number.

---

## The accuracy spine (read the deep file for depth)

These are storage-mode-independent — they govern *every* DAX measure, Import or Direct Lake. They are the everyday-correctness core and the most common source of a measure that "runs but is wrong." Each is pre-verified; the full treatment lives in the forward-linked deep file [`../../power-platform/knowledge/dax-measure-accuracy.md`](../../power-platform/knowledge/dax-measure-accuracy.md).

| Rule | The trap |
|---|---|
| **Row context iterates, it does not filter.** Only *filter context* restricts which rows are visible; row context exists only inside calculated columns and iterators (`SUMX`, `FILTER`, …). [SQLBI: row-context-and-filter-context-in-dax] | Expecting a bare column reference to "respect the current row" outside an iterator — it doesn't; there's no row to respect. |
| **Every measure reference is auto-wrapped in `CALCULATE` → context transition.** A measure called inside an iterator silently turns each row into its own filter context. This is the **#1 subtle-bug source.** [SQLBI: understanding-context-transition-in-dax] | `SUMX ( Sales, [Total Margin] )` re-evaluates `[Total Margin]` per row under context transition — rarely what you meant; you usually wanted the column expression, not the measure. |
| **Row context does NOT propagate across relationships.** Use `RELATED` (many→one) / `RELATEDTABLE` (one→many) to reach the other table inside an iterator. [SQLBI: row-context-and-filter-context-in-dax] | `SUMX ( Sales, Sales[qty] * Product[price] )` errors or misbehaves — wrap the far column in `RELATED ( Product[price] )`. |
| **`CALCULATE` filter args OVERWRITE same-column filters by default; `KEEPFILTERS` intersects.** [SQLBI: filter-context-in-dax; learn.microsoft.com/dax/keepfilters-function-dax] | `CALCULATE ( [Sales], Product[color] = "Red" )` *replaces* any color filter from the visual; if you wanted "Red **and** whatever the user picked," you needed `KEEPFILTERS`. |
| **`REMOVEFILTERS` is a modifier only.** Where a *table expression* is required (e.g. the first arg of `SUMX`), use `ALL`. [learn.microsoft.com/dax/removefilters-function-dax] | Trying to use `REMOVEFILTERS` as an iterator's table argument — it isn't one. |
| **Never put `ALLSELECTED` inside an iteration.** It depends on shadow filter contexts and is unreliable / ill-defined inside a row iteration. [learn.microsoft.com/dax/allselected-function-dax] | `% of visible total` measures that nest `ALLSELECTED` inside `SUMX` and return numbers that drift with the iteration. |
| **Use `DIVIDE`, not `/`, for division.** Safe (handles divide-by-zero) and query-optimized. [learn.microsoft.com/dax/best-practices/dax-divide-function-operator] | A ratio measure throwing `Infinity`/blank-storms on zero denominators instead of a clean `DIVIDE ( num, den )`. |

> These hold identically on Direct Lake — the VertiPaq engine evaluates DAX the same way it does for Import (see the next section). The spine is where everyday measures go right or wrong; Direct Lake changes *where the inputs live*, not how DAX context works.

---

## Direct Lake changes WHERE the math lives

Direct Lake reads columns straight from Delta tables in OneLake into VertiPaq on demand (transcoding), and "refresh" is metadata **framing**, not a data copy. [direct-lake-overview; direct-lake-how-it-works] Two consequences for measure design:

**1. Row-level derivation belongs in the GOLD Delta table, not a calculated column.**
Microsoft Learn now lists calculated columns and calculated tables as **`Supported (preview)` on Direct Lake on OneLake** (columns are *unmaterialized*) and **`Not supported` on Direct Lake on SQL**. [direct-lake-overview "Considerations and limitations", retrieved 2026-06-09] `[verify-at-use]` — this is **preview** on on-OneLake and absent on on-SQL, so it is not a stable foundation. The durable, mode-independent home for a derived row value (e.g. `line_total = qty * price`) is the **gold Delta table**, computed upstream in Spark or T-SQL — Learn states plainly that *"Direct Lake depends on data preparation being done in the data lake … Spark jobs for Fabric lakehouses, T-SQL DML statements for Fabric warehouses, dataflows, pipelines."* [direct-lake-overview] This reinforces [`../best-practices/semantic-measures-not-calc-columns.md`](../best-practices/semantic-measures-not-calc-columns.md): **measures are the home for aggregation / ratio / time intelligence; gold is the home for row-level derivation; a calculated column is a rare exception** (and on Direct Lake, a preview-only or unavailable one).

```text
Row-level derived value (line_total = qty * price)   → compute in GOLD (Spark/T-SQL), store the column.
Aggregation / ratio / simple time intelligence       → DAX MEASURE (no storage, filter-context aware).
A grouping key you must materialize                  → gold column first; calc column only if it truly can't live in gold
                                                         (and on Direct Lake on SQL it can't exist at all).
```

**2. The on-OneLake vs on-SQL split shapes measure risk.** [direct-lake-overview; direct-lake-how-it-works — retrieved 2026-06-09]

| | Direct Lake on OneLake | Direct Lake on SQL |
|---|---|---|
| DirectQuery fallback | **None.** *"Direct Lake on OneLake doesn't fall back to DirectQuery mode."* A column that can't load → the query **errors** (or returns empty on an OneLake-security mismatch). | **Yes.** Falls back when a column can't load, on a SQL view, when SQL-endpoint RLS/OLS is enforced, or when capacity guardrails are exceeded. |
| Calc columns / tables | Supported **(preview)**, unmaterialized `[verify-at-use]` | **Not supported** (except calc groups / what-if / field params) |
| Measure-design implication | Every gold column a measure touches must be framed and loadable, and OneLake-security roles correct, or the measure errors. | A measure can *silently* push the query into DirectQuery (slower, and SQL-side semantics) — design gold to stay under guardrails and avoid view-backed / source-RLS tables. |

For the full mode comparison, framing, and fallback triage, see [`direct-lake-and-semantic-models.md`](direct-lake-and-semantic-models.md) and [`direct-lake-fallback-triage-decision-tree.md`](direct-lake-fallback-triage-decision-tree.md).

---

## Direct Lake DAX considerations

Grounded in Microsoft Learn (retrieved 2026-06-09); marked `[verify-at-use]` where the sources don't pin a detail down — **no function-level "unsupported on Direct Lake" list is fabricated here.**

- **DAX evaluation is the same engine as Import.** Direct Lake and Import queries are both *"processed by the VertiPaq engine."* [direct-lake-overview] The accuracy spine above therefore applies unchanged — context transition, `RELATED`, `KEEPFILTERS`, `DIVIDE` all behave as in Import.

- **The Learn sources do NOT enumerate function-level DAX differences vs Import.** They describe *model-feature* limitations (calculated tables/columns preview-or-unsupported, no model-side table partitions, no user-defined aggregations, no hybrid tables, complex/binary/GUID Delta column types unsupported, string values capped at 32,764 chars, no non-numeric floats like `NaN`). They do **not** publish a list of DAX *functions* that fail on Direct Lake. **So: do not claim a specific DAX function is "unsupported on Direct Lake."** If a measure misbehaves, treat it as a framing/fallback/data-type issue first, and mark any function-level suspicion `[verify-at-use]` and test it in a `Direct Lake only` model. [direct-lake-overview "Considerations and limitations"]

- **Unprocessed columns are a correctness, not just performance, risk.** A measure referencing a column whose table is unframed/unprocessed **errors** on on-OneLake and **falls back to DirectQuery** on on-SQL (or fails if fallback is disabled). [direct-lake-overview; direct-lake-how-it-works] `[verify-at-use]`

- **Author against "pure Direct Lake" to surface hidden fallback.** Set the model's `DirectLakeBehavior` to **`Direct Lake only`** during authoring so a measure that would silently fall back instead **errors loudly**, revealing the real problem; the property only affects on-SQL (on-OneLake never falls back). [Power BI blog "Leveraging pure Direct Lake mode", retrieved 2026-06-09; direct-lake-how-it-works `Model.DirectLakeBehavior`] `[verify-at-use]`

- **Unsupported source data types break measures at the column level.** Binary/GUID and complex Delta column types are unsupported — convert them to strings or supported types in **gold** so the measure has clean inputs. [direct-lake-overview] `[verify-at-use]`

- **What "measure-first" means for a Direct Lake gold model:** the gold Delta table carries the *grain, keys, and pre-derived row values*; the semantic model adds *only* relationships + measures + a marked date table. Aggregation, ratio, and time-intelligence logic lives in measures (filter-context aware, zero storage); anything row-level lives in gold (so Direct Lake can just load it and never needs a preview-only calculated column).

---

## The seam — when to escalate to `power-bi-engineer`

**Everyday Direct Lake measures stay here** (`fabric-semantic-model-engineer`): sums, counts, distinct counts, ratios via `DIVIDE`, simple time intelligence (`TOTALYTD`, prior-period via `DATEADD`), share-of-total, and the gold-shaping that feeds them.

**Escalate to [`power-platform/power-bi-engineer`](../../power-platform/CLAUDE.md)** for advanced DAX craft:

- Complex / reusable **measure libraries** and deep measure refactoring.
- **Calculation groups**, field parameters, what-if parameters as a modeling pattern.
- **Performance tuning** of DAX (storage-engine vs formula-engine splits, materialization).
- **DAX Studio / server-timings** profiling and query-plan analysis.

**Litmus test (from CLAUDE.md §10):** *if the question is about a measure's DAX depth, a visual, or a `.pbix` → `power-bi-engineer`; if it's about the Delta tables, the OneLake storage mode, framing, or why Direct Lake fell back → this plugin.* The deep authoring home for DAX correctness is [`../../power-platform/knowledge/dax-measure-accuracy.md`](../../power-platform/knowledge/dax-measure-accuracy.md).

---

## Direct Lake measure accuracy checklist

Paste-ready — run before shipping a Direct Lake measure:

- [ ] **Row-level math is in gold**, not a calculated column (calc columns are preview on on-OneLake, unsupported on on-SQL). `[verify-at-use]`
- [ ] **No measure called inside an iterator** unless context transition is intended (the #1 subtle bug).
- [ ] **Cross-table references inside iterators use `RELATED` / `RELATEDTABLE`** (row context doesn't cross relationships).
- [ ] **`CALCULATE` filters are intentional about overwrite vs intersect** — `KEEPFILTERS` where the user's filter must survive.
- [ ] **`ALL` (not `REMOVEFILTERS`) where a table expression is required**; **no `ALLSELECTED` inside an iteration.**
- [ ] **All division uses `DIVIDE`** (safe + optimized), not `/`.
- [ ] **Every column the measure touches is framed/processed** — else on-OneLake errors, on-SQL falls back.
- [ ] **No unsupported source types** (binary/GUID/complex/`NaN`) in the columns the measure reads — converted in gold. `[verify-at-use]`
- [ ] **Validated against `DirectLakeBehavior = Direct Lake only`** so hidden fallback surfaces as an error, not a slow query (on-SQL). `[verify-at-use]`
- [ ] **A marked date table** backs any time-intelligence measure (auto date/time is on-OneLake-only and limited). `[verify-at-use]`
- [ ] **Advanced DAX (calc groups, perf tuning, measure libraries) routed to `power-platform/power-bi-engineer`.**

---

## Provenance

DAX accuracy spine — pre-verified against:
- SQLBI: [Row context and filter context in DAX](https://www.sqlbi.com/articles/row-context-and-filter-context-in-dax/), [Understanding context transition in DAX](https://www.sqlbi.com/articles/understanding-context-transition-in-dax/), [Filter context in DAX](https://www.sqlbi.com/articles/filter-context-in-dax/)
- Microsoft Learn DAX reference: [`KEEPFILTERS`](https://learn.microsoft.com/dax/keepfilters-function-dax), [`REMOVEFILTERS`](https://learn.microsoft.com/dax/removefilters-function-dax), [`ALLSELECTED`](https://learn.microsoft.com/dax/allselected-function-dax), [`DIVIDE` best practice](https://learn.microsoft.com/dax/best-practices/dax-divide-function-operator)

Direct Lake specifics — fetched and grounded from Microsoft Learn / Power BI, **retrieved 2026-06-09**:
- [Direct Lake overview](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview) — storage mode, on-OneLake vs on-SQL, calculated columns/tables (preview / not supported) + considerations-and-limitations table, "data preparation done in the data lake."
- [Develop Direct Lake semantic models](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-develop) — model/table design, on-OneLake vs on-SQL creation + connectors, composite models.
- [How Direct Lake works](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works) — transcoding, framing, DirectQuery fallback triggers, `Model.DirectLakeBehavior`.
- [Leveraging pure Direct Lake mode for maximum query performance](https://powerbi.microsoft.com/en-us/blog/leveraging-pure-direct-lake-mode-for-maximum-query-performance/) — `DirectLakeBehavior` (Automatic / Direct Lake only / DirectQuery only) and authoring against pure Direct Lake. *(URL 301-redirects to the Fabric Community blog mirror; content grounded from the mirror.)*

Fabric ships monthly and Direct Lake calc-column/table support is **preview** — every Direct-Lake-tagged claim is dated and `[verify-at-use]` per house opinion #9.

---

## See also

- [`direct-lake-and-semantic-models.md`](direct-lake-and-semantic-models.md) — the two Direct Lake modes, framing, fallback, gold shaping (the storage-mode context this file sits on).
- [`../best-practices/semantic-measures-not-calc-columns.md`](../best-practices/semantic-measures-not-calc-columns.md) — where the math lives (gold vs measure vs calc column).
- [`direct-lake-fallback-triage-decision-tree.md`](direct-lake-fallback-triage-decision-tree.md) — diagnosing a model that fell back / errored / returned empty.
- [`../../power-platform/knowledge/dax-measure-accuracy.md`](../../power-platform/knowledge/dax-measure-accuracy.md) — **the deep DAX authoring home** (forward link; the encyclopedia this surface points to).

---

_Owned by `fabric-semantic-model-engineer`. Last reviewed 2026-06-09 by `claude`. Advanced DAX authoring escalates to `power-platform/power-bi-engineer` (CLAUDE.md §10)._
