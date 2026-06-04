# Every measure ships with DisplayFolder, Description, and FormatString

**Status:** Pattern/Absolute — every Power BI measure committed to source control must carry a `DisplayFolder`, a `Description`, and a `FormatString`. A measure missing any of the three is incomplete. This is the minimum bar for a production-quality semantic model.

**Domain:** Power BI / Fabric semantic models (TMDL, Tabular Editor, BPA)

**Applies to:** `power-bi-engineer`, `power-platform-tester`, any agent authoring or reviewing TMDL measure definitions

> **Discovery credit:** the practice of enforcing this metadata triad as a per-measure gate — and the BPA rule pattern that checks it — is documented in the [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development) marketplace (Kurt Buhler). The rule content here is written from underlying TOM/TMDL and Tabular Editor BPA primary sources; it does not reproduce Data Goblins material. Sources: Tabular Editor BPA docs at https://docs.tabulareditor.com/te2/Best-Practice-Analyzer.html (retrieved 2026-06-03); Microsoft TOM reference `[unverified — training knowledge: confirm property names against current TOM docs]`.

---

## Why this exists

A Power BI semantic model is a shared artifact: measures are authored once and consumed by many report authors, analysts, and now AI agents. A measure with no description forces every consumer to reverse-engineer the DAX to understand what it calculates. A measure with no format string produces inconsistently formatted numbers across visuals — `1234567.89` in one card and `$1.23M` in another, both pointing at the same measure. A measure in no display folder is buried in a flat alphabetical list that becomes unusable past 20 measures.

The three metadata properties address three distinct failure modes:

| Missing property | Failure it causes |
|---|---|
| `DisplayFolder` | Field list is a flat undifferentiated list; consumers cannot find measures; new reports reuse the wrong one or recreate it |
| `Description` | Consumers (humans and agents) cannot determine intent, unit, or filter-context assumptions without reading the DAX |
| `FormatString` | Numbers display inconsistently across visuals; the same measure looks different depending on which visual is used |

A fourth, less obvious failure: **AI-readiness**. An agent generating a new report against a model without descriptions cannot resolve ambiguity between similar measures (e.g., `Revenue`, `Revenue YTD`, `Revenue LY`). Well-described measures reduce agentic authoring errors.

---

## How to apply

### In TMDL (direct file edit)

A TMDL measure block carries the three properties as named fields. A complete measure entry looks like this:

```
measure 'Total Revenue' = SUMX(Sales, Sales[Quantity] * Sales[Unit Price])
    formatString: "$#,##0.00"
    displayFolder: "Revenue"

    /// Total revenue calculated as the sum of quantity multiplied by unit price
    /// across all sales rows in the current filter context. Excludes returns.
```

The `///` triple-slash lines are the TMDL representation of the `Description` property. Both the `formatString:` field and the `displayFolder:` field are named properties in the TMDL block. A measure missing any of these three is flagged by the `validate-tmdl-measure-metadata.sh` hook (see below) and by Tabular Editor BPA. `[unverified — confirm exact TMDL syntax against current TMDL grammar docs]`

### In Tabular Editor

In Tabular Editor, set the three properties on a measure via the Properties pane:

- `Description` — free text; explains what the measure calculates, what filter context it assumes, and the unit.
- `Display Folder` — a backslash-delimited folder path (e.g., `Revenue\YTD` places the measure in a nested folder). Shared folder names group measures in the field list.
- `Format String` — a format string expression (e.g., `"$#,##0"`, `"0.0%"`, `"#,##0"`). For currency measures, the standard format string is `"$#,##0.00"` or the locale-appropriate equivalent. For percentage measures, `"0.00%"`.

### In Tabular Editor C# scripting (bulk application)

```csharp
// Example: set a default format string on all measures missing one.
// Adjust the pattern logic for your model's naming conventions.
foreach (var measure in Model.AllMeasures)
{
    if (string.IsNullOrWhiteSpace(measure.FormatString))
        measure.FormatString = "#,##0";

    if (string.IsNullOrWhiteSpace(measure.Description))
        measure.Description = "[TODO: add description]";

    if (string.IsNullOrWhiteSpace(measure.DisplayFolder))
        measure.DisplayFolder = "Uncategorized";
}
```

Running this script identifies gaps without overwriting existing values.

### Via the BPA rule set

Add the following rules to your Tabular Editor BPA JSON rule set to enforce the triad automatically. These rules produce a Warning or Error result during a BPA scan:

```json
[
  {
    "ID": "MEASURE_MISSING_DESCRIPTION",
    "Name": "Measure is missing a description",
    "Category": "Maintenance",
    "Severity": 2,
    "Scope": "Measure",
    "Expression": "string.IsNullOrWhiteSpace(Description)",
    "FixExpression": null,
    "Description": "Every measure must have a Description explaining its calculation, filter-context assumptions, and unit."
  },
  {
    "ID": "MEASURE_MISSING_FORMAT_STRING",
    "Name": "Measure is missing a FormatString",
    "Category": "Maintenance",
    "Severity": 2,
    "Scope": "Measure",
    "Expression": "string.IsNullOrWhiteSpace(FormatString)",
    "FixExpression": null,
    "Description": "Every measure must have a FormatString to ensure consistent number display."
  },
  {
    "ID": "MEASURE_MISSING_DISPLAY_FOLDER",
    "Name": "Measure is missing a DisplayFolder",
    "Category": "Maintenance",
    "Severity": 1,
    "Scope": "Measure",
    "Expression": "string.IsNullOrWhiteSpace(DisplayFolder)",
    "FixExpression": null,
    "Description": "Every measure should be placed in a DisplayFolder for discoverability."
  }
]
```

`[unverified — training knowledge: confirm BPA JSON rule schema version against your Tabular Editor version]`

### Via the `validate-tmdl-measure-metadata.sh` hook

The `power-platform` plugin ships a `hooks/validate-tmdl-measure-metadata.sh` hook that fires on `*.tmdl` edits and deterministically checks each measure block for the presence of a `///` description, a `formatString:` field, and a `displayFolder:` field. It is a structural file check — it does not evaluate DAX correctness or cross-model referential integrity. The hook is advisory by default (prints to stderr; does not block). To make it blocking, set the final exit to `exit 1`. See `hooks/README.md` for wiring instructions.

---

## Do

- Set `DisplayFolder` using a backslash-delimited hierarchy: `Revenue\Comparisons`, `Inventory\Stock Levels`. Consistent folder names make the field list navigable at scale.
- Write `Description` in plain language from the perspective of a report author who has not seen the DAX: what does this measure calculate, what does the filter context include or exclude, what is the unit?
- For currency measures, use a locale-appropriate format string: `"$#,##0.00"` (USD), `"£#,##0"` (GBP), `"€#,##0.00"` (EUR). Do not rely on "Auto" — it behaves differently depending on the report locale setting.
- For percentage measures, use `"0.00%"` if the underlying value is a decimal fraction (0.123 → 12.30%), or `"0.00"` with a `%` suffix in the description if the value is already multiplied.
- Run BPA in CI on every PR that modifies `.tmdl` files. Gate the PR on BPA severity 2+ violations.
- Populate all three fields on every measure before the PR is opened — backfilling is slower than authoring correctly the first time.

## Don't

- Don't use `DisplayFolder: ""` (empty string) as a substitute for `"Uncategorized"`. An empty folder places the measure at the root. If you have more than 10 measures at the root, it is a field-list usability problem.
- Don't leave `Description` as a placeholder (`"TODO"`, `"measure for revenue"`). A placeholder description is worse than an explicit gap: it passes a string-is-not-empty check while communicating nothing.
- Don't use the model's default format string. For any measure that returns a monetary value, the default format ("General") will display `1234567.89` instead of `$1,234,568`. Report authors will override this with visual-level formatting inconsistently.
- Don't skip `DisplayFolder` on a model with fewer than 15 measures because "it's small." Models grow; a folder structure established early is easy to maintain and hard to retrofit.

---

## Connection to the hook

The `validate-tmdl-measure-metadata.sh` hook checks this rule deterministically on every TMDL file edit. It cannot check DAX correctness, referential integrity, or whether a description is *meaningful* — those require a connected model or human review. It can confirm the three properties are structurally present and non-empty. The BPA rules above run the same check on the connected model in Tabular Editor or CI.

The two mechanisms together form the enforcement pair: the hook fires in-session for fast feedback; BPA fires in CI as the cross-tool backstop.

---

## See also

- [`../knowledge/power-bi-fabric-agentic-toolchain-2026.md`](../knowledge/power-bi-fabric-agentic-toolchain-2026.md) — the full agentic toolchain context (Tabular Editor, BPA, TMDL, `fab`, semantic-link-labs)
- [`bi-measures-not-calculated-columns.md`](./bi-measures-not-calculated-columns.md) — the companion rule on measure-vs-calculated-column selection
- [`tmdl-pbip-source-control-hygiene.md`](./tmdl-pbip-source-control-hygiene.md) — how TMDL is committed to source control
- [`../knowledge/dax-category-name-mismatch-zero-scores.md`](../knowledge/dax-category-name-mismatch-zero-scores.md) — a production lesson on why well-described measures reduce authoring errors
- [`../knowledge/pbir-dax-pitfalls.md`](../knowledge/pbir-dax-pitfalls.md) — companion file on the DAX measure-evaluation pitfalls (REMOVEFILTERS arity, format-string scale, `formatString: @` for text measures) that silently blank visuals
- Tabular Editor BPA docs: https://docs.tabulareditor.com/te2/Best-Practice-Analyzer.html

---

## Appendix — TMDL comment syntax (BMA-CSP Lesson 7, 2026-06-04)

**TL;DR:** `//` comments are valid **inside** DAX measure expressions (indented, within `VAR` / `RETURN`). They are **NOT** valid at the **top level** of a TMDL document. Deploying a TMDL file with a top-level `//` comment fails with `Parsing error type - InvalidLineType` and a near-useless error location.

```tmdl
// WRONG — top-level // comment fails with InvalidLineType on deploy
table Licences
    column 'Licence Number'
        dataType: string
        sourceColumn: cr_licence_number

    measure 'Total Licences' =
        // CORRECT — // is valid INSIDE a measure expression (indented under the measure body)
        VAR _all = COUNTROWS(Licences)
        RETURN _all
        formatString: '#,##0'
```

For documentation that needs to live at the TMDL top level, use a **`///` triple-slash description** on the object instead — those are valid metadata, get picked up by the BPA discipline this best-practice file enforces, and survive serialization:

```tmdl
table Licences
    /// Issued CSP licences. Source: cr_licences table in Dataverse, refreshed nightly.
    column 'Licence Number'
        dataType: string

    /// Count of issued licences, used as the denominator on portfolio-level cards.
    measure 'Total Licences' =
        COUNTROWS(Licences)
        formatString: '#,##0'
```

**The rule:** never `//` at the top level of a TMDL file; use `///` descriptions for metadata, and reserve `//` for inside-measure-body comments only. The TMDL parser gives no helpful error message, so prevention is cheaper than diagnosis. (Source: production session 2026-06-04 on `mcorbettbma/BTCSIReporting`; the verbatim lesson is in [`../../../.ravenclaude/runs/forge/bma-csp-lessons/source.md`](../../../.ravenclaude/runs/forge/bma-csp-lessons/source.md) but that path is gitignored — the lesson is encoded here.)

---

## Provenance

Codifies house opinion §3 #6 and §4 (model quality) from [`../CLAUDE.md`](../CLAUDE.md), the `power-bi-engineer` semantic-model discipline, and the Tabular Editor BPA community standard practice for the measure-metadata triad. The hook reference (`validate-tmdl-measure-metadata.sh`) corresponds to the hook registered in `hooks/hooks.json` and the dev-mirror entry in `.claude/settings.json`.

---

_Last reviewed: 2026-06-04 by `claude` (BMA-CSP Lesson 7 — TMDL comment syntax appendix)._
