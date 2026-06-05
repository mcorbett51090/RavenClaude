---
name: fabric-ingestion-method-selection
description: "Decision playbook for choosing the right Fabric data ingestion method — Mirroring, Copy job, pipeline Copy activity, Dataflow Gen2, or Eventstream — based on source type, latency, cost, and CDC requirements."
---

# Fabric Ingestion Method Selection

## When to Use This Skill

Use when a new data source needs to land in OneLake and the right ingestion method is not obvious, or when an existing pipeline is slow, expensive, or architecturally mismatched.

## 1. The Primary Decision Tree

| Question | If YES | If NO |
|---|---|---|
| Is the source a supported Mirroring source (Azure SQL, Cosmos DB, Snowflake, Azure DB for PostgreSQL)? | **Mirroring** (first choice) | Continue |
| Is this real-time streaming (IoT, telemetry, Kafka, Event Hub)? | **Eventstream** | Continue |
| Is this a one-time or low-frequency bulk copy (file, HTTP, cloud storage)? | **Copy job** (simple) or **Copy activity in pipeline** (orchestrated) | Continue |
| Does the transformation logic belong in a low-code tool (non-engineer author)? | **Dataflow Gen2** | Continue |
| Complex orchestration: dependencies, loops, error handling, branching? | **Pipeline** (with Copy activity + Notebook) | Continue |
| Otherwise | **Dataflow Gen2 with Fast Copy** for medium-complexity | — |

## 2. Method Comparison Table

| Method | Latency | Cost model | CDC | Best for |
|---|---|---|---|---|
| **Mirroring** | Near-real-time (seconds) | Replication: free; query: billed | Yes (change feed) | Supported SaaS + Azure DBs; zero-code CDC |
| **Eventstream** | Sub-second | CU per event + storage | Yes (stream) | IoT, telemetry, Event Hub/Kafka, Activator triggers |
| **Copy job** | Scheduled (minutes) | CU per run | No | Simple file/blob/lake copies, one-time migrations |
| **Copy activity (pipeline)** | Scheduled or event-driven | CU per run | Via watermark/timestamp | Orchestrated batch, multi-step pipelines |
| **Dataflow Gen2** | Scheduled (minutes) | CU per refresh | Via incremental refresh | Low-code M/Power Query transformations; citizen data engineers |
| **Dataflow Gen2 (Fast Copy)** | Faster for large volumes | CU per run | Via incremental refresh | Large-volume Dataflow ingestion with staging enabled |

## 3. Mirroring: the "Free Replication" Caveat

Mirroring replicates data to OneLake at **no CU cost**. However:
- **Querying the mirrored data bills CUs** — do not serve mirrored bronze directly to Direct Lake or high-frequency reports without a silver/gold transform step.
- Mirroring is a read-only replica — you cannot write back to the mirrored table.
- Auto-mirror (for supported sources) is simpler than manual Mirroring configuration — prefer it when available. [verify-at-build: Auto-mirror availability varies by source.]

**Supported Mirroring sources (as of 2026-06):** Azure SQL Database, Azure Cosmos DB, Snowflake, Azure Database for PostgreSQL, Google BigQuery, and Azure SQL Managed Instance. [verify-at-build]

## 4. Incremental Load Patterns

When full-refresh is too expensive (large tables), use an incremental pattern:

**Watermark approach (Copy activity in pipeline):**
```
1. Read max(updated_at) from the target table (or a watermark metadata store)
2. SELECT * FROM source WHERE updated_at > @watermark
3. Upsert into silver via MERGE with deletion vectors
4. Update watermark to now()
```

**CDC via Mirroring:** No watermark logic needed — change events arrive automatically.

**Dataflow Gen2 incremental refresh:** Configure in the Dataflow settings → "Incremental refresh" → define the date/time range column.

## 5. Eventstream to Eventhouse (Real-Time Path)

```
Source (Event Hub / Kafka / IoT Hub / custom)
  → Eventstream (transform, filter, fan-out)
    → Eventhouse (KQL database)
      → Real-Time dashboard
        → Activator (alert rules)
```

Only use Eventstream → Lakehouse (Delta sink) when you need batch analytics on the same stream. Avoid dual-sinking (Eventhouse + Lakehouse) unless the use cases genuinely differ.

## 6. Dataflow Gen2 vs Notebook: When to Use Which

| Factor | Dataflow Gen2 | Notebook (PySpark) |
|---|---|---|
| Author skill | Citizen data engineer / Power Query | Data engineer / Python |
| Transformation complexity | Low-medium (M/Power Query) | High (arbitrary code) |
| Large-volume performance | Good with Fast Copy staging | Better for very large Delta merges |
| ALM (Git) | TMDL/JSON (workspace Git integration) | `.ipynb` (Git integration) |
| Debug experience | Dataflow editor, limited | Full Spark UI, logs |

## 7. Selection Checklist

- [ ] Source type identified and checked against Mirroring support list
- [ ] Latency requirement confirmed (real-time → Eventstream/Mirroring; batch → Copy/Dataflow/pipeline)
- [ ] CDC requirement assessed — Mirroring handles it natively; watermark patterns add maintenance cost
- [ ] Author skill assessed — citizen data engineers use Dataflow Gen2; engineers use notebooks/pipelines
- [ ] Cost model reviewed — Mirroring replication is free; query cost is not

## Pitfalls

- Calling Mirroring "free" without the query-billing caveat — consumers over-query mirrored tables and get surprise CU charges
- Using a full-refresh pipeline on a 100M-row table when Mirroring or watermark CDC would land the same data incrementally
- Using Dataflow Gen2 for complex multi-step transformations — the M engine has limits; a notebook is more maintainable
- Building a custom CDC pipeline for a source that Mirroring already supports

## See Also

- [`../../agents/data-factory-engineer.md`](../../agents/data-factory-engineer.md) — data movement decisions, connector selection, and incremental/CDC patterns
- [`../../agents/realtime-intelligence-engineer.md`](../../agents/realtime-intelligence-engineer.md) — Eventstream, Eventhouse, and Activator
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: shortcut before copy; Mirroring caveat
