# Test DAX measures as code — EVALUATE against a frozen dataset, expected vs actual

**Status:** Pattern — strong default for any non-trivial measure; the cheapest correctness evidence Power BI offers.

**Domain:** Power BI / testing

**Applies to:** `power-platform`

---

## Why this exists

A DAX measure that "looks right" in a visual is not tested — the visual hides which filter context it evaluated under, and a measure can be correct on the maker's slice and wrong under a different filter, a different security role, or an empty selection. The `power-platform-tester` agent's stance: *"Knows the difference between 'the formula is correct' and 'the formula returns the right row from the right source under the user's security context'"*, and names **DAX Studio's `EVALUATE`-based unit tests** as the cheapest evidence for every new or modified measure. Treating measures as code — a frozen input dataset, a written expected value, an `EVALUATE` query that produces the actual — turns "I think it's right" into a repeatable assertion that catches regressions when someone refactors the model later.

## How to apply

Freeze a small known dataset, write the expected number, then run an `EVALUATE` (or `DEFINE MEASURE` + `EVALUATE`) in DAX Studio / the XMLA endpoint and compare. Test the **edge filter contexts**, not just the happy slice:

```dax
-- Correctness test for [Total Margin] against a frozen fixture (known: 3 orders, margin = 450).
DEFINE
    MEASURE Sales[_TestMargin] = SUMX ( Sales, Sales[Amount] - Sales[Cost] )
EVALUATE
ROW (
    "AllRows",        [_TestMargin],                                   -- expect 450
    "Filtered_East",  CALCULATE ( [_TestMargin], Region[Name] = "East" ), -- expect 120
    "Empty_Filter",   CALCULATE ( [_TestMargin], Region[Name] = "Nowhere" ) -- expect BLANK(), not 0
)

-- Run via DAX Studio against a frozen .pbix / model; diff actuals against the expected comment.
-- For divide-safety, also assert [Margin %] returns BLANK (not an error) on a zero-revenue slice.
```

**Do:**
- Write the **expected value** before running — a test with no pre-stated expectation just confirms whatever the model returned.
- Test **edge filter contexts**: empty selection (expect `BLANK()`, not 0), single member, all members, and a slice with no matching rows.
- Run against a **frozen** model/dataset so expected values stay stable (pairs with `test-data-isolation-and-teardown.md`).
- Re-run the suite **after any model refactor** — measures break silently when relationships or columns change.
- Capture **VertiPaq Analyzer** + **DAX Studio Server Timings** before/after for performance-sensitive measures (flag growth > 20%).

**Don't:**
- Eyeball a card visual and call the measure tested — the filter context is invisible.
- Use `/` where `DIVIDE()` belongs and then not test the divide-by-zero path.
- Test only the maker's default slice — the regression hides in the filter contexts you didn't open.

## Edge cases / when the rule does NOT apply

- A **trivial aggregation** (`SUM(Sales[Amount])`) over a well-modeled fact rarely needs a unit test — reserve the effort for measures with `CALCULATE`, context transition, time intelligence, or RLS interaction.
- **RLS-dependent** measures must be tested under **View as role** with a real account, not as the author (see `bi-row-level-security-tested-as-role.md`) — the `EVALUATE` alone won't catch a role leak.
- **Direct Lake / DirectQuery** measures may fall back or push down differently than Import — verify the query actually ran in the mode you think it did (Server Timings shows storage-engine vs formula-engine split).

## See also

- [`bi-measures-not-calculated-columns.md`](./bi-measures-not-calculated-columns.md) — the thing under test (`DIVIDE`, `VAR`, filter context)
- [`bi-row-level-security-tested-as-role.md`](./bi-row-level-security-tested-as-role.md) — measures interacting with RLS need the role test too
- [`test-data-isolation-and-teardown.md`](./test-data-isolation-and-teardown.md) — the frozen-dataset discipline this depends on
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power BI — Measure vs calculated column`
- [`../skills/power-bi/resources/dax-patterns-and-performance.md`](../skills/power-bi/resources/dax-patterns-and-performance.md) — DAX Studio, VertiPaq Analyzer, Server Timings
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — owner of the `EVALUATE` suite

## Provenance

Grounded in the `power-platform-tester` agent's "Power BI / DAX" coverage (EVALUATE unit tests, VertiPaq Analyzer, Server Timings) and [DAX queries (EVALUATE)](https://learn.microsoft.com/dax/dax-queries) (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
