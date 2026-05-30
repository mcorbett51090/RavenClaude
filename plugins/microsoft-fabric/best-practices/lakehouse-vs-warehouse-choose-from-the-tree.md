# Choose lakehouse vs warehouse from the decision tree, not from the word "SQL"

**Status:** Pattern — the store-selection decision tree is the strong default; picking a store by habit (or by the presence of the word "SQL" in the ask) is the documented anti-pattern.

**Domain:** Store selection / architecture

**Applies to:** `microsoft-fabric`

---

## Why this exists

Lakehouse and Warehouse share the **same OneLake Delta storage and the same SQL surface**, so the bytes live in the same place either way — which is exactly why people pick by habit and get it wrong. The lakehouse's **SQL analytics endpoint is read-only T-SQL** (DQL + views/TVFs, **no DML**); the warehouse is **full T-SQL with multi-table ACID**. A team that hears "SQL" and provisions a Warehouse for a Spark/Python data-engineering workload pays in friction; a team that lands a structured star schema needing multi-statement transactions in a Lakehouse discovers the read-only endpoint can't `UPDATE`. The choice is about the **engine and write pattern**, not where the data sits (house opinion #2: pick the store from the tree, not from habit).

## How to apply

Traverse [`../knowledge/fabric-store-decision-tree.md`](../knowledge/fabric-store-decision-tree.md) top-to-bottom. The lakehouse-vs-warehouse call comes down to three questions:

| Question | Lakehouse | Warehouse |
|---|---|---|
| **How do you develop?** | Spark / Python / notebooks | T-SQL |
| **Multi-table ACID transactions?** | No (read-only SQL endpoint) | **Yes** (full T-SQL DQL/DML/DDL) |
| **Data complexity?** | un/semi/structured, or "don't know yet" | structured only |

```text
Spark/Python OR mixed/unknown skills   → LAKEHOUSE
T-SQL + multi-statement transactions   → WAREHOUSE
"It's SQL so it must be a warehouse"   → STOP — traverse the tree first
```

Many teams correctly use **both** (medallion pattern 2): land + transform in a **Lakehouse** with Spark, then expose curated gold to a **Warehouse** for SQL-first reporting. That's not indecision — it's the engine matched to each layer's job.

**Do:**
- Name the store *after* traversing the tree, citing the branch that decided it.
- Default to **Lakehouse** when skills are mixed or the dev profile is unclear — it's the lower-regret choice and the SQL endpoint still serves read-only T-SQL.
- Reach for the **Warehouse** the moment multi-table ACID or full DML is a hard requirement.

**Don't:**
- Map "SQL" → Warehouse reflexively; the lakehouse SQL endpoint covers most read-only reporting.
- Provision a Warehouse for a Spark/notebook ELT pipeline because the team "knows SQL."
- Treat lakehouse-or-warehouse as either/or when the medallion answer is "both, by layer."

## Edge cases / when the rule does NOT apply

- **Streaming / telemetry / time-series** is neither — that's an **Eventhouse / KQL DB** (earlier branch of the tree).
- **OLTP / operational app writes** is a **SQL database in Fabric** (which auto-mirrors to OneLake), not a Warehouse.
- **Data already exists elsewhere** (another workspace/tenant, ADLS/S3/GCS) — **shortcut first**, before any managed store.

## See also

- [`../knowledge/fabric-store-decision-tree.md`](../knowledge/fabric-store-decision-tree.md) — the full store + lakehouse-vs-warehouse decision tree
- [`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) — canonical `## Decision Tree:` for lakehouse vs warehouse vs KQL DB
- [`one-copy-shortcut-before-copying.md`](./one-copy-shortcut-before-copying.md) — the shortcut-first branch that precedes the store choice
- [`../agents/fabric-architect.md`](../agents/fabric-architect.md) · [`../agents/warehouse-engineer.md`](../agents/warehouse-engineer.md)

## Provenance

Codifies house opinion #2 ("Pick the store from the decision tree, not from habit") from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Warehouse vs Lakehouse decision guide](https://learn.microsoft.com/fabric/fundamentals/decision-guide-lakehouse-warehouse) and [Choose the right data store](https://learn.microsoft.com/fabric/fundamentals/decision-guide-data-store) (Microsoft Learn, retrieved 2026-05-30). The read-only-SQL-endpoint vs full-T-SQL distinction is from the same guides.

---

_Last reviewed: 2026-05-30 by `claude`_
