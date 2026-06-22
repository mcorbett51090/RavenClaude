---
name: direct-lake-gold-shaping
description: "Playbook for shaping OneLake gold Delta tables to serve a Direct Lake semantic model efficiently — covers framing prerequisites, column naming rules, fallback prevention, and the on-OneLake vs on-SQL mode selection."
---

# Direct Lake Gold Shaping

## When to Use This Skill

Use when building or debugging a Direct Lake semantic model, specifically to ensure the underlying Delta tables are shaped correctly so the model frames efficiently and never falls back to DirectQuery unexpectedly.

## 1. The Two Direct Lake Modes

| Mode | Source | DirectQuery fallback? | RLS/CLS/OLS enforcement |
|---|---|---|---|
| **On-OneLake** | Delta tables in a Lakehouse | **No fallback** — errors or returns empty on unsupported operations | OneLake security (row-level, column-level) |
| **On-SQL** | SQL analytics endpoint / Warehouse | **Falls back to DirectQuery** when framing unsupported | SQL-native RLS/CLS/OLS (forces fallback) |

Choose the mode before shaping gold. On-OneLake is faster and never falls back; on-SQL is needed when SQL-native security or T-SQL views are required.

## 2. Framing Prerequisites (on-OneLake mode)

| Requirement | Detail |
|---|---|
| Delta format | Tables must be in Delta Lake format (not Parquet-only) |
| V-Order enabled | Required for efficient column-stripe reads by the framing engine |
| No spaces in column names | Column names with spaces prevent framing |
| No mixed-case duplicates | `CustomerID` and `customerid` in the same table cause framing errors |
| Supported data types | Avoid `MAP`, `ARRAY`, `STRUCT` columns in framed tables — use scalar types |
| Schema enabled Lakehouse | Required for the OneLake-security data-preview pane (not for Spark RLS/CLS enforcement) |

## 3. Gold Table Schema Checklist

```python
from pyspark.sql.types import StructType, StructField, StringType, LongType, DecimalType, TimestampType

gold_schema = StructType([
    StructField("OrderId", StringType(), False),          # No spaces, consistent casing
    StructField("CustomerId", StringType(), False),
    StructField("OrderDate", TimestampType(), False),
    StructField("TotalAmount", DecimalType(18, 2), False),
    StructField("StatusCode", StringType(), True),
])

# Write with V-Order
(df.write
   .format("delta")
   .option("delta.parquet.vorder.enabled", "true")
   .option("overwriteSchema", "true")
   .mode("overwrite")
   .saveAsTable("gold.fact_orders"))
```

## 4. Framing Verification

```python
# After writing the gold table, verify it can be framed
# In a Fabric notebook:
from sempy import fabric

# Check if the table satisfies Direct Lake framing requirements
tables = fabric.list_tables(dataset="MySemanticModel", workspace="MyWorkspace")
print(tables[["name", "mode"]])  # mode should show "DirectLake"
```

Alternatively, open the semantic model in the Fabric portal → "Refresh history" → look for fallback events.

## 5. Common Fallback Triggers (on-OneLake mode)

| Trigger | Fix |
|---|---|
| Column name has a space | Rename: `Order Date` → `OrderDate` |
| `MAP` or `ARRAY` column type | Explode/flatten before gold write |
| Missing V-Order | `ALTER TABLE gold.fact_orders SET TBLPROPERTIES ('delta.parquet.vorder.enabled' = 'true')` |
| Non-Delta format (plain Parquet) | Re-register as a Delta table |
| Composite model with import table mixed in | Expected; only on-SQL mode allows composites with fallback |

## 6. Composite Model Considerations

If the semantic model mixes on-OneLake Direct Lake tables with Import-mode tables (e.g. a small date dimension imported for performance):

- The on-OneLake tables still frame efficiently
- Cross-table joins that span the boundary may trigger DirectQuery fallback depending on the DAX query shape — test with DAX Studio and Performance Analyzer
- On-SQL mode is needed if the security model requires SQL-native RLS (which forces DirectQuery fallback for all affected queries)

## 7. Gold Shaping Workflow

1. Profile the silver table — identify columns used by the semantic model
2. Remove PII columns and apply masking at the silver→gold transform step
3. Flatten any nested structs/arrays into scalar columns
4. Rename columns to PascalCase with no spaces
5. Enable V-Order and write to `gold` schema
6. Run `OPTIMIZE` and `VACUUM` as a post-write step
7. Validate framing via Fabric portal or `sempy`
8. Add the table to the semantic model and check mode = `DirectLake`

## Pitfalls

- Assuming on-OneLake falls back like DirectQuery — it does not; an unsatisfied framing requirement returns empty results or errors, not a slow-but-correct DirectQuery result
- Skipping V-Order optimization — the model still works but column-stripe reads are significantly slower
- Using SQL-native RLS on an on-OneLake model — SQL OLS forces DirectQuery fallback on every query that touches the secured table; use OneLake security row-level filters instead
- Naming gold tables after bronze tables and forgetting to reshape — column names from source systems often have spaces and special characters

## See Also

- [`../../agents/fabric-semantic-model-engineer.md`](../../agents/fabric-semantic-model-engineer.md) — Direct Lake mode selection, framing, and fallback debugging
- [`../../agents/lakehouse-engineer.md`](../../agents/lakehouse-engineer.md) — gold table write patterns and V-Order configuration
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinions on Direct Lake mode and V-Order on gold
