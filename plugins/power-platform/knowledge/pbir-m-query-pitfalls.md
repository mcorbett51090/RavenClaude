# PBIR / Power Query (M) — load-stage pitfalls that silently drop data

> **Last reviewed:** 2026-06-04. Source: production session on the BMA-CSP-Risk-Scoring report (Bermuda Monetary Authority CSP engagement, `mcorbettbma/ContosoReporting`, 2026-06-04). Two M Query load-stage pitfalls each caused **silent data loss** that the report had no way to surface — entities literally missing from the output with no warning, no count discrepancy in the UI. Refresh when (a) Power Query M's `Workbook.*` semantics change or (b) the Dataverse connector's lookup-display-field format changes.
>
> **Claim-grounding note.** The `Workbook{[Item="Form",Kind="Table"]}` error semantics and `Table.RemoveRowsWithErrors` silent-drop behavior are documented on Microsoft Learn (Power Query M reference) and were reproduced 2026-06-04 against the BMA-CSP SharePoint Excel source. The Dataverse-lookup pipe-delimited format (`"Class|Name|Date"`) was observed in production on the `Licences.Licensee Name` column on the same date — [verify-at-use] for whether the specific connector version in your engagement uses the same delimiter format (Microsoft has tightened lookup display semantics across connector versions).
>
> **When to read this file.** When you're authoring or reviewing a Power Query M load step that reads from SharePoint Excel, a folder of Excel files, or a Dataverse lookup column — and you want to avoid the two most common shapes of **silent data loss** at the load stage. These are the failures the report cannot tell you about, because by the time the data hits the visual layer, the missing rows are already gone.

---

## 1. `Table.RemoveRowsWithErrors` on a brittle `Workbook{[Item=...]}` step silently drops files (Lesson 2)

**Symptom:** Some entities have no score in the deployed report even though they submitted Excel files. The Diagnostics page shows their `Entity_ID` is correctly extracted on the *files that loaded*, but the missing entities never appear at all — they're not in the dataset.

**Why:** A common `TransformFile` pattern looks like this:

```powerquery
// BRITTLE — throws an error per workbook that does NOT have a table named exactly "Form"
let
    Source = Excel.Workbook(File.Contents(WorkbookPath), null, true),
    FormTable = Source{[Item="Form", Kind="Table"]}[Data],
    Promoted = Table.PromoteHeaders(FormTable)
in
    Promoted
```

If `TransformFile` is then applied to a folder of Excel workbooks, and any of those workbooks lacks a table named exactly `"Form"`, the `Source{[Item="Form", ...]}[Data]` step **throws an error for that workbook**. Pair that with the very common downstream pattern:

```powerquery
ExpandedFiles = Table.ExpandTableColumn(
                    Table.RemoveRowsWithErrors(
                        Table.AddColumn(Files, "Content", each TransformFile([Content]))
                    ),
                    "Content", ColumnNames)
```

`Table.RemoveRowsWithErrors` **silently discards** the rows for workbooks that threw — no warning, no diagnostic, no count anywhere. The entire workbook is gone from the dataset.

**Fix — defensive `TransformFile` with a sheet-fallback path:**

```powerquery
TransformFile = (WorkbookPath as binary) as table =>
    let
        Source = Excel.Workbook(WorkbookPath, null, true),

        // 1. Try the named table first (preferred — preserves type metadata).
        NamedTable =
            try Source{[Item="Form", Kind="Table"]}[Data]
            otherwise null,

        // 2. Fall back to the first sheet's Data + promote headers manually.
        SheetFallback =
            try Table.PromoteHeaders(Source{0}[Data], [PromoteAllScalars=true])
            otherwise null,

        // 3. Pick whichever resolved.
        Resolved = if NamedTable <> null then NamedTable else SheetFallback,

        // 4. Defensive column-name matching — workbook authors rename columns; don't hardcode.
        AllCols = Table.ColumnNames(Resolved),
        QNumCol = List.First(List.Select(AllCols, each Text.Contains(_, "Cumul") or Text.Contains(_, "Serial")), null),
        AnswerCol = List.First(List.Select(AllCols, each Text.Contains(_, "Selected") or Text.Contains(_, "value")), null),
        Renamed = Table.RenameColumns(Resolved, {{QNumCol, "Question_Number"}, {AnswerCol, "Value"}}, MissingField.Ignore),

        // 5. Drop empty Entity_ID rows EXPLICITLY (so the absence is visible if it happens systemically).
        NonEmpty = Table.SelectRows(Renamed, each [Entity_ID] <> null and [Entity_ID] <> "")
    in
        NonEmpty
```

**Anti-pattern guard — never combine these two:** a step that can `throw an error per row` (like `Workbook{[Item=ExactName]}`) PLUS a downstream `Table.RemoveRowsWithErrors`. That combination is a silent-data-loss generator. Always either (a) handle the failure case explicitly with `try ... otherwise`, or (b) replace `RemoveRowsWithErrors` with `Table.ReplaceErrorValues` so failures are visible as marker rows.

---

## 2. Add a "load count" KPI so silent drops are immediately visible

The structural prevention for Lesson 2's failure mode is to surface a **diagnostic KPI** that exposes the count discrepancy. Add a measure like this and pin it to a Diagnostics page:

```dax
// Counts rows in the Licences table — should match the number of submitted workbooks.
// If this diverges from the number of files in the source folder, something dropped silently.
Total Submissions Loaded =
    CALCULATE(
        COUNTROWS(Licences),
        REMOVEFILTERS(Licences)
    )
```

Compare against the expected count (manually known, or from a separate `SharePoint.Files` query that doesn't go through `TransformFile`). Discrepancy = silent drop, investigate immediately.

The general rule: **any load step that can silently discard rows must have a corresponding count-measure on a Diagnostics page** — a load drop without a count is undetectable until the report is wrong in production.

---

## 3. Dataverse lookup display fields are pipe-delimited — extract in M, not DAX (Lesson 6)

**Symptom:** A column sourced from a Dataverse lookup (e.g. `Licences.Licensee Name`) displays as `"CSP|ALEXANDER MANAGEMENT LTD|11/16/2017"` in every visual — raw pipe-delimited metadata, not just the name.

**Why:** The Dataverse connector returns lookup **display fields** (typically named `_<lookup>_value@OData.Community.Display.V1.FormattedValue` on the OData side, surfaced as `_<lookup>name` or `<Lookup> Name` in the connector's friendly column) as a concatenated metadata string. The format is roughly **`<Classification>|<Name>|<EffectiveDate>`** but the specific delimiter and field order depend on the lookup target entity's primary-name configuration and the connector version.

**Fix — extract in the M Query, not in DAX:**

```powerquery
// In the Power Query M transformation for the Licences table.
let
    Source = Dataverse.Database("yourorg.crm.dynamics.com"),
    Licences = Source{[Schema="dbo", Item="cr_licences"]}[Data],

    // The raw lookup-display column comes back pipe-delimited.
    // Extract the NAME segment specifically (between the 1st and 2nd '|').
    WithCleanName = Table.AddColumn(Licences, "Licensee Name (Clean)",
        each
            let
                raw = [#"Licensee Name"],
                // Text.BetweenDelimiters with the same delimiter twice = "between the 1st and 2nd occurrence"
                name = if raw = null then null
                       else if not Text.Contains(raw, "|") then raw    // already clean
                       else Text.BetweenDelimiters(raw, "|", "|", 0, 0)
            in
                name,
        type text),

    // Drop the original raw column once the clean one is verified.
    Final = Table.RemoveColumns(WithCleanName, {"Licensee Name"})
in
    Final
```

Or, if the format is reliably 3 fields and you want all three:

```powerquery
WithSplit = Table.AddColumn(Licences, "Licensee Parts",
    each if [#"Licensee Name"] = null then null else Text.Split([#"Licensee Name"], "|"),
    type list),

WithFields = Table.AddColumn(WithSplit, "Licensee Class",  each try [#"Licensee Parts"]{0} otherwise null, type text),
WithFields2 = Table.AddColumn(WithFields, "Licensee Name (Clean)", each try [#"Licensee Parts"]{1} otherwise null, type text),
WithFields3 = Table.AddColumn(WithFields2, "Licence Issue Date", each try Date.FromText([#"Licensee Parts"]{2}) otherwise null, type date),
```

**Why M and not DAX:** doing this in M means **every downstream measure and visual sees a clean string column from day one**. Doing it in DAX (as a calculated column or a wrapper measure) requires every consuming measure to remember to call the cleanup function — a per-measure discipline that drifts. Clean at the load boundary; downstream code is unconditional.

**Anti-pattern guard:** when a Dataverse connector query lands in your report, audit every column with a lookup-name shape (`_xxxname` or `xxx Name`) **before** building any visual. Concatenated metadata in lookup display fields is a Dataverse-connector behavior, not a one-off bug — it will show up on every lookup column.

---

## 4. Cross-links

- **Diagnosis tool for any load-stage suspicion** (count discrepancy, missing rows, schema drift): [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) — the REST `executeQueries` analogue for "what's actually in the deployed semantic model" against the M-query "what should have loaded".
- **Once data is loaded, the next class of silent-fail is measure-level:** [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md).
- **String-literal-vs-actual-column-value mismatch (the same shape as Lesson 6 applied to DAX):** [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md). The `Domain` calc-column pattern documented there is the FIX-B-style permanent solution; this file's M-stage cleanup is the FIX-A "do it at the load boundary" complement.
- **The visual-structure pitfalls for the same family of silent-blank failures:** [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) (e.g. `tableEx` vs `pivotTable`).

---

## 5. Owners

- **Primary:** `power-bi-engineer` (Power Query M, dataflows, dataset load discipline).
- **Secondary:** `dataverse-architect` (when the lookup-display-field format is the root cause — Dataverse connector behavior).
- **Tertiary:** `power-platform-tester` (the "Total Submissions Loaded" diagnostic-KPI discipline is in this agent's mandate — load-stage testing).
