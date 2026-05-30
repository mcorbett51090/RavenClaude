# Reach for a OneLake shortcut before copying data

**Status:** Pattern — strong default; copy only with a written reason. (Calling Mirroring "free" without the caveat is an outright bug.)

**Domain:** OneLake / data movement

**Applies to:** `microsoft-fabric`

---

## Why this exists

Every Fabric store keeps **one copy of data in OneLake in open Delta format** by default, so the architecture choice is about the *engine and write pattern*, not where the bytes live. Duplicating data that a **shortcut** could virtualize is a smell: it doubles storage, creates a second source of truth that drifts, and bills compute twice. The most expensive misconception is calling **Mirroring** "free" — it is **free to replicate** (up to a CU-based storage allowance, ~1 TB free per CU, F64 ≈ 64 TB) but **never free to query**, and cross-region sources incur egress. Quoting "free" without that caveat sets a wrong cost expectation a client will hold you to.

## How to apply

Walk the "do I copy?" ladder from least to most duplication: **shortcut → auto-mirror → mirror → copy job → pipeline.**

| Option | Copies data? | When |
|---|---|---|
| **Shortcut** | No (virtualization) | Data already lives elsewhere (another workspace/tenant, ADLS/S3/GCS) and you want a single source of truth |
| **Auto-mirror** | Yes, zero-config | The operational store is **already in Fabric** (SQL DB / Cosmos DB in Fabric) — it replicates itself to OneLake Delta automatically |
| **Mirroring** | Yes, managed replica | Near-real-time read-only replica of an **external** operational DB; free to replicate, **billed to query** |
| **Copy job / pipeline** | Yes, you own the state | Incremental/CDC or orchestrated ELT with transforms |

```text
Need to READ data that already exists in OneLake/ADLS/S3/GCS?
  → Shortcut. Compute bills to the consuming capacity; storage stays with the owner. No copy.
```

**Do:**
- Default to a shortcut when you only need to *read* existing data.
- State Mirroring's cost honestly: "free to replicate, billed to query," plus cross-region egress.
- For bronze, if the source is already in OneLake/ADLS/S3/GCS, **shortcut instead of copying** into the lakehouse.

**Don't:**
- Stand up a Copy job or pipeline to duplicate data a shortcut would serve.
- Say "Mirroring is free" without the query-billed caveat — the plugin's anti-pattern hook flags exactly this phrasing.

## Edge cases / when the rule does NOT apply

- **You need transforms or incremental/CDC state** — a shortcut is read-through virtualization, not an ELT engine; use a copy job or pipeline then.
- **The owning store's availability or region is a risk** (cross-tenant, cross-region egress, or a source that may go offline) — a managed replica can be the right call despite the copy.
- **Mirroring vs shortcut for an external operational DB** — a shortcut needs the data already in an accessible lake; an external SQL Server / Snowflake DB is a Mirroring case, not a shortcut case.

## See also

- [`../knowledge/fabric-store-decision-tree.md`](../knowledge/fabric-store-decision-tree.md) — the store + shortcut/mirror/auto-mirror decision tree (`fabric-architect` owns it)
- [`../knowledge/fabric-data-movement-decision-tree.md`](../knowledge/fabric-data-movement-decision-tree.md) — the ingestion-method tree and the Mirroring cost caveats
- [`../agents/fabric-architect.md`](../agents/fabric-architect.md) — owns the "do I copy?" call

## Provenance

Codifies house opinion #1 ("One copy in OneLake … reach for a shortcut before copying; mirroring is free to replicate, not free to query") from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in the cost caveats in [`../knowledge/fabric-data-movement-decision-tree.md`](../knowledge/fabric-data-movement-decision-tree.md) (Microsoft Learn, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
