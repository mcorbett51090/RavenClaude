# Lakehouse Design — <workload name>

> Produced by `lakehouse-architect`. Every volatile runtime/feature/pricing fact carries a `[verify-at-use, retrieved <date>]` marker.

## 1. Readers & SLOs (fill this FIRST)

| Consumer          | Query shape           | Freshness SLO | Volume / growth |
| ----------------- | --------------------- | ------------- | --------------- |
| <BI dashboard>    | <aggregate by region> | <daily>       | <rows/day>      |
| <ML feature job>  | <point-in-time join>  | <hourly>      | <...>           |

## 2. Batch vs streaming

- **Decision:** <scheduled batch | Auto Loader | Structured Streaming | DLT>
- **Why (tie to the SLO above):** <...>
- If streaming: **trigger** <...>, **checkpoint** <location>, **exactly-once/idempotency** approach <...>

## 3. Medallion layering

| Layer  | What lands here            | Write pattern           | Justification (what it earns) |
| ------ | -------------------------- | ----------------------- | ----------------------------- |
| Bronze | <raw, append-only>         | append                  | <replay/audit anchor>         |
| Silver | <conformed, deduped, typed> | MERGE on <keys> / CDC   | <canonical clean model>       |
| Gold   | <serving aggregates>       | overwrite / MERGE       | <read by consumer above>      |

## 4. Delta table strategy (per table)

| Table         | Partition / clustering            | File-size target | OPTIMIZE / Z-ORDER | VACUUM retention |
| ------------- | --------------------------------- | ---------------- | ------------------ | ---------------- |
| <silver.orders> | <partition order_date / liquid> | <...>            | <Z-ORDER region>   | <safe window>    |

- **Over-partitioning check:** confirm no high-cardinality partition column. ✅ / ⚠️ <...>

## 5. Unity Catalog governance

- **Catalog/schema layout:** <catalog-per-env | per-domain> — <names>
- **Managed vs external:** <...> (external where <...>)
- **Grants:** to **groups** — <group → privilege> (no user-level grants)
- **PII tagging / masking:** <columns> — org policy owner: `data-governance-privacy`
- **Lineage/audit:** <how used>

## 6. Compute & DBU cost envelope

| Workload        | Compute                     | Scaling / termination        | Photon | Est. DBU (order-of-mag, verify-at-use) |
| --------------- | --------------------------- | ---------------------------- | ------ | -------------------------------------- |
| <nightly ETL>   | jobs compute                | autoscale N–M, auto-term Xm  | on/off | <...>                                  |
| <BI dashboard>  | SQL warehouse (right-sized) | auto-stop Xm / serverless    | n/a    | <...>                                  |

- **Top cost drivers to watch:** <idle warehouse | small files | Photon-on-UDF-job | all-purpose-for-jobs>

## 7. Seams & flip conditions

| Boundary                          | Owner                        |
| --------------------------------- | ---------------------------- |
| dbt / semantic modeling (gold)    | `analytics-engineering`      |
| External orchestration            | `data-orchestration`         |
| Org privacy/retention policy      | `data-governance-privacy`    |
| ML training/serving lifecycle     | `ml-engineering`             |

- **What would flip this design:** <1–2 facts, e.g. "if the freshness SLO drops to sub-minute, silver becomes a stream">

## 8. Open questions / verify-at-use list

- [ ] <feature GA status to confirm>
- [ ] <current DBU pricing for the chosen SKU>
