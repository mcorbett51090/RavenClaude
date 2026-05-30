# Decision tree: how to get data into Fabric?

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28).
**Owner:** `data-factory-engineer` (traverse before recommending an ingestion method).
**Source:** [Choose a data movement strategy](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-movement), [Choose a data integration strategy](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-integration), [Get data into Fabric](https://learn.microsoft.com/fabric/fundamentals/get-data).

```mermaid
flowchart TD
    A[Bring data into Fabric] --> S{Is the source already a<br/>SQL DB or Cosmos DB *in Fabric*?}
    S -->|Yes| AM[Nothing to do — it auto-mirrors<br/>to OneLake Delta, zero-config]
    S -->|No| B{Real-time / streaming events?}
    B -->|Yes| ES[Eventstream<br/>→ Eventhouse / Lakehouse / Activator]
    B -->|No| C{Replicating a whole operational DB<br/>for analytics, minimal setup?}
    C -->|Yes, turn-key + free| MIR[Mirroring<br/>near-real-time read-only Delta replica]
    C -->|No| D{Need incremental / CDC / bulk<br/>without building a pipeline?}
    D -->|Yes| CJ[Copy job<br/>watermark + native CDC, 50+ connectors]
    D -->|No, need orchestration<br/>+ heavy transforms| E{Low-code transforms or<br/>custom orchestration?}
    E -->|Low-code 300+ transforms| DF[Dataflow Gen2<br/>+ Fast Copy for extract-load]
    E -->|Orchestrated pipeline,<br/>control flow, custom code| PL[Pipeline + Copy activity<br/>you manage incremental state]
```

---

## Decision Tree: Fabric data movement — how to get a source into Fabric

**When this applies:** you have a named source (an operational SQL/Cosmos DB, a streaming event feed, a file landing in ADLS/S3/GCS, or an in-Fabric store) and must pick *how* the data arrives in OneLake. Observable entry terms: the source type is known, you are choosing between Mirroring / Copy job / pipeline / Eventstream / Dataflow Gen2, and you have not yet committed to one. **Traverse top-to-bottom before naming a method — do NOT keyword-match "real-time" or "CDC" to a method without checking the earlier branches.**

**Last verified:** 2026-05-30 against Microsoft Learn (Fabric Data Factory decision guides, retrieved 2026-05-28; convention re-confirmed 2026-05-30).

```mermaid
flowchart TD
    A[Bring data into Fabric] --> S{Source already a SQL DB<br/>or Cosmos DB *in Fabric*?}
    S -->|Yes| AM[AUTO-MIRROR — nothing to do<br/>auto-replicates to OneLake Delta]
    S -->|No| B{Real-time / streaming events?}
    B -->|Yes| ES[EVENTSTREAM<br/>→ Eventhouse / Lakehouse / Activator]
    B -->|No| C{Replicate a whole operational DB,<br/>minimal setup, read-only OK?}
    C -->|Yes| MIR[MIRRORING<br/>near-real-time read-only replica]
    C -->|No| D{Need incremental / CDC / bulk<br/>without building a pipeline?}
    D -->|Yes| CJ[COPY JOB<br/>watermark + native CDC]
    D -->|No, need orchestration<br/>+ heavy transforms| E{Low-code transforms<br/>or custom orchestration?}
    E -->|Low-code 300+ transforms| DF[DATAFLOW GEN2<br/>+ Fast Copy for extract-load]
    E -->|Orchestrated control flow,<br/>custom code| PL[PIPELINE + Copy activity<br/>you own incremental state]
```

**Rationale per leaf:**

- *Auto-mirror* — if the source is **already a SQL DB / Cosmos DB in Fabric**, it replicates itself to OneLake Delta with zero config (HTAP); there is nothing to set up.
- *Eventstream* — the only **no-code low-latency streaming** path; also does CDC initial-snapshot and content-based routing to Eventhouse / Lakehouse / Activator.
- *Mirroring* — turn-key **near-real-time read-only Delta replica** of an *external* operational DB; **free to replicate, billed to query**, single read-only destination.
- *Copy job* — fills the gap between Mirroring (too simple) and pipelines (too much to manage): native **incremental + CDC**, 50+ connectors, no pipeline scaffolding.
- *Dataflow Gen2* — **low-code 300+ transforms** with Fast Copy for extract-load; the analyst-led path. Fast Copy is 13–21× faster but only on folding-friendly extract-load steps.
- *Pipeline* — **orchestration**: `ForEach` / `Lookup` / notebook / SQL / Dataflow activities, schedule or event triggers; you own incremental state via watermark + control table.

**Tradeoffs summary table:**

| Method | Copies data? | CDC | Incremental | Cost | Use when |
|---|---|---|---|---|---|
| **Auto-mirror** | Yes, zero-config | Yes | continuous | CU-billed query, replicate-free | Source is a SQL/Cosmos DB already in Fabric |
| **Mirroring** | Yes, read-only replica | Yes | — | **free to replicate, billed to query** | Replicate an external operational DB, minimal setup |
| **Eventstream** | continuous | Yes (snapshot) | — (continuous) | billed | Real-time / streaming / event-driven |
| **Copy job** | Yes | Yes | Yes (watermark) | billed | Incremental / CDC / bulk, no pipeline to build |
| **Dataflow Gen2** | Yes | — | — | billed | Low-code transforms (300+) + Fast Copy ingest |
| **Pipeline** | Yes | — | manual (control table) | billed | Orchestrated ELT, control flow, custom code |

> If the situation matches multiple branches, prefer the **earlier** leaf (less to build, less duplication): shortcut/auto-mirror before mirror before copy job before pipeline.

---

## The comparison

| Method | Use case | Flexibility | CDC | Incremental | Cost |
|---|---|---|---|---|---|
| **Mirroring** | near-real-time replica of an operational DB | fixed, simple | Yes | — | **free to replicate, not free to query** |
| **Copy job** | bulk / incremental / CDC, no pipeline to build | easy + advanced options | Yes | Yes (watermark) | billed |
| **Copy activity (pipeline)** | orchestrated, fully customizable ELT | advanced | — | manual (control table) | billed |
| **Eventstream** | real-time streaming, event-driven, CDC initial snapshot | simple + customizable | Yes | — (continuous) | billed |
| **Dataflow Gen2** | low-code transforms (300+); Fast Copy for extract-load | low-code | — | — | billed |

Sources: [data-movement decision guide table](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-movement#data-movement-decision-guide).

## Sharp edges (state these to the client)

- **Mirroring is "free to replicate, not free to query."** Replication compute + storage are free only up to a CU-based allowance (~1 TB free per CU; F64 ≈ 64 TB); beyond that or when the capacity is paused, OneLake storage is billed. **Query compute is always billed at normal rates**, and cross-region sources incur egress. Mirroring writes a **single read-only** Delta destination. Source: [Data Factory overview](https://learn.microsoft.com/fabric/data-factory/data-factory-overview).
- **Dataflow Gen2 Fast Copy** is up to **13-21× faster** than Gen1 because it bypasses the mashup engine — but only for extract-load steps that meet the [Fast Copy prerequisites](https://learn.microsoft.com/fabric/data-factory/dataflows-gen2-fast-copy); any folding-breaking transform falls back to the standard engine. Treat Fast Copy as the *default for ingestion*; reserve heavy reshaping for notebooks/Spark. Source: [dataflow strategy benchmarks](https://learn.microsoft.com/fabric/data-factory/decision-guide-data-transformation).
- **Copy job** fills the gap between Mirroring (too simple) and pipelines (too much to manage): native incremental + CDC, no pipeline scaffolding.
- **Pipelines** orchestrate everything else: `ForEach`, `Lookup`, notebook/SQL/Dataflow activities, schedule or event triggers; you own incremental state via watermark expressions + control tables.
- **Eventstream** is the only no-code path for low-latency streaming; it can also do CDC initial-snapshot replication and content-based routing to Eventhouse / Lakehouse / Activator. See [`../knowledge/fabric-2026-capability-map.md`](fabric-2026-capability-map.md).

> House-opinion link: **#1 shortcut-first** (if you only need to read it, shortcut beats any copy) and **#5 capacity is shared** (ingestion is a background CU consumer — schedule heavy loads with smoothing in mind).
