# Use the Hyper API to build and refresh extracts programmatically

**Status:** Pattern
**Domain:** Data / extract engineering
**Applies to:** `tableau`

---

## Why this exists

Tableau's built-in extract refresh (scheduled via Server or Cloud) pulls the
entire source query and re-writes the `.hyper` file. For large, slowly-changing
datasets this is wasteful: an overnight incremental load that appends yesterday's
rows should not re-read 10 years of history. The Hyper API lets you construct
and modify `.hyper` files directly in Python or Java — insert only new rows,
delete obsolete rows, run custom pre-processing — and then publish the result.
Teams that skip the Hyper API end up either over-fetching the source on every
refresh or building a brittle Prep flow that does not have programmatic control.

## How to apply

```python
from tableauhyperapi import HyperProcess, Connection, Telemetry, \
    TableDefinition, TableName, SqlType, Inserter

# Define the schema once
orders_table = TableDefinition(
    table_name=TableName("Extract", "Orders"),
    columns=[
        TableDefinition.Column("order_id",    SqlType.text()),
        TableDefinition.Column("order_date",  SqlType.date()),
        TableDefinition.Column("amount_cents", SqlType.big_int()),
        TableDefinition.Column("currency",    SqlType.text()),
    ]
)

# Incremental insert — append only new rows
def append_new_orders(hyper_path: str, new_rows: list[dict]):
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(hp.endpoint, hyper_path) as conn:
            conn.catalog.create_table_if_not_exists(orders_table)
            with Inserter(conn, orders_table) as ins:
                for row in new_rows:
                    ins.add_row([row["order_id"], row["order_date"],
                                 row["amount_cents"], row["currency"]])
                ins.execute()
```

After writing the `.hyper` file, publish it via the Tableau REST API (or
`tabcmd publish`). Wrap the write in a transaction — the Hyper API is ACID
within a connection.

**Do:**
- Use the Hyper API for programmatic extract builds, incremental appends,
  and bulk deletes.
- Keep the schema definition as the authoritative contract between the pipeline
  and the workbook.
- Publish atomically: write to a temp file, then rename/publish when complete.

**Don't:**
- Directly modify a `.hyper` file that is currently mounted by Tableau Server —
  always publish a new version.
- Use the Hyper API for simple scheduled full-refresh extracts; the built-in
  scheduler is sufficient and lower maintenance.
- Skip `Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU` if your data is sensitive
  and you have not reviewed what telemetry is sent `[verify-at-build]`.

## Edge cases / when the rule does NOT apply

- Small extracts (< 1M rows) that refresh in under 5 minutes from the built-in
  scheduler: the Hyper API overhead is not worth it.

## See also

- [`../agents/tableau-data-architect.md`](../agents/tableau-data-architect.md) — owns extract engineering and Hyper
- [`./data-extract-optimization.md`](./data-extract-optimization.md) — column/row pruning before Hyper API write
- [`./prep-incremental-and-idempotent-flows.md`](./prep-incremental-and-idempotent-flows.md) — Prep flow alternative for non-programmatic incremental refresh

## Provenance

Codifies the Hyper API (Tableau's official programmatic extract API) usage
pattern. Tableau Hyper API documentation `[verify-at-build]`. Standard
extract-engineering practice for large or complex extract pipelines.

---

_Last reviewed: 2026-06-05 by `claude`_
