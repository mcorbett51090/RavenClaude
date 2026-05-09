# Formula Columns

Formula columns perform real-time calculations on the same record using Power Fx expressions.
Unlike rollup fields, they calculate instantly and don't require async jobs.

## Creating via API

Set the `FormulaDefinition` property on the column metadata:

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8

{
    "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
    "SchemaName": "cnt_FullName",
    "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [{ "Label": "Full Name", "LanguageCode": 1033 }]
    },
    "FormulaDefinition": "cnt_firstname & \" \" & cnt_lastname",
    "MaxLength": 200,
    "RequiredLevel": { "Value": "None" }
}
```

## Supported Output Types

| Output Type | @odata.type | Notes |
|---|---|---|
| Text | `StringAttributeMetadata` | Default for concatenation, conditional text |
| Whole Number | `IntegerAttributeMetadata` | For counting, integer math |
| Decimal | `DecimalAttributeMetadata` | For precise decimal calculations |
| Float | `DoubleAttributeMetadata` | For floating-point calculations |
| Yes/No | `BooleanAttributeMetadata` | For conditional logic returning true/false |
| Choice | `PicklistAttributeMetadata` | For categorization formulas |
| DateTime | `DateTimeAttributeMetadata` | For date calculations |

## Unsupported Output Types

- Currency (use Decimal instead)
- Language, Duration, TimeZone format types
- Email, URL, TextArea, TickerSymbol format types

## Common Formula Examples

```
// String concatenation
cnt_firstname & " " & cnt_lastname

// Conditional text
If(cnt_score > 100, "Expert", If(cnt_score > 50, "Intermediate", "Beginner"))

// Date math (days until due)
DateDiff(Now(), cnt_duedate, TimeUnit.Days)

// Numeric calculation
cnt_quantity * cnt_unitprice

// Status indicator
If(cnt_duedate < Now(), "Overdue", "On Track")
```

## Supported Functions

**Text:** Concat, Left, Right, Mid, Len, Lower, Upper, Trim, Substitute, Replace, Text, Value
**Math:** Abs, Round, RoundUp, RoundDown, Int, Mod, Power, Sqrt, Sum, Min, Max
**Logic:** If, Switch, And, Or, Not, IsBlank, Coalesce
**Date:** Now, Today, DateAdd, DateDiff, Year, Month, Day, Hour, Minute, Second, Weekday
**Type Conversion:** Text, Value, DateValue, DateTimeValue, Boolean

## Limitations

- **1000 character max** for the formula expression
- **10 depth max** for nested functions
- **No cyclic references** — Column A can't reference Column B if B references A
- **No self-reference** — A column can't reference itself
- **No rollup usage with UTCNow** — Can't combine rollup fields with UTCNow in formulas
- **Sorting disabled** when formula references related tables, logical columns, or calculated columns
- **Null handling:** Null values are treated as 0 (numeric) or empty string (text) — differs from calculated columns
- **Type immutability:** Cannot change the formula column's output type after creation
- **Same-record only:** Cannot reference fields on related records (use rollup or plugin for that)

## When to Use What

| Need | Solution |
|---|---|
| Same-record text concatenation | Formula column |
| Same-record arithmetic | Formula column |
| Same-record conditional logic | Formula column |
| Cross-record aggregation (SUM, COUNT) | Plugin or code-based update |
| Complex business logic with side effects | Plugin |
| Real-time calculation on related record change | Plugin (PostOperation on child) |
| Async batch calculations | Custom workflow / Power Automate |
