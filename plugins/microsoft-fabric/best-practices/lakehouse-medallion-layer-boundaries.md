# Bronze raw, silver curated, gold business-ready — keep the layer boundaries

**Status:** Pattern — medallion is the strong default; skipping a layer or smearing responsibilities across layers needs a written reason.

**Domain:** Medallion / lakehouse layout

**Applies to:** `microsoft-fabric`

---

## Why this exists

The medallion shape (bronze → silver → gold) only pays off when each layer keeps **one job**. The most common engagement failure is a "silver-gold" table that is simultaneously raw-ish, conformed, *and* pre-aggregated — so nothing can be reasoned about: you cannot replay from an immutable source, you cannot point a Direct Lake model at a clean star, and a schema change at the source ripples straight into the BI layer. Each layer is **its own lakehouse/warehouse, ideally its own workspace**, so the layer boundary is also a control + governance boundary (house opinion #3). The write pattern flips across the layers — bronze prioritizes ingest speed, gold prioritizes read — which is exactly why the optimization that helps one hurts another (see [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md)).

## How to apply

Assign each layer its single responsibility and write pattern, and **never collapse two layers to save a hop**:

| Layer | Holds | Write pattern | Immutable? |
|---|---|---|---|
| **Bronze (raw)** | source data exactly as it arrives; original format or Delta | ingest speed | **yes — append-only** |
| **Silver (curated)** | cleansed, deduped, conformed, joined, type-standardized | balance read + write | no |
| **Gold (business-ready)** | aggregated, denormalized, access-controlled data products | read speed | no |

Two deployment patterns are both valid:
- **Pattern 1** — every layer a Lakehouse; consumers read via the SQL analytics endpoint.
- **Pattern 2** — bronze + silver Lakehouses, **gold a Warehouse** for SQL-first reporting.

For bronze, if the source already lives in OneLake / ADLS / S3 / GCS, **shortcut instead of copying** (house opinion #1). Silver + gold are always Delta.

**Do:**
- Keep bronze **immutable and append-only** — it is your replay source; transformations belong downstream.
- Give each layer its own lakehouse/workspace so access + governance land on the boundary.
- Conform and dedupe in **silver**; aggregate and denormalize for a consumer in **gold**.

**Don't:**
- Build a single "silver-gold" table that does conforming and aggregation at once — you lose both replayability and a clean star.
- Serve **bronze** to Direct Lake or the SQL analytics endpoint (house opinion #3).
- Mutate bronze in place — a corrected source row is a new bronze append + a silver re-derivation, not an `UPDATE` on raw.

## Edge cases / when the rule does NOT apply

- **Tiny, single-source, throwaway POC** — a two-layer (bronze→gold) shape can be defensible; *write down* that silver was deliberately skipped so the next engineer doesn't assume it's missing by accident.
- **Already-clean operational source auto-mirroring into OneLake** (SQL DB / Cosmos DB in Fabric) — the mirrored Delta is effectively a managed bronze; build silver/gold on top of it rather than re-copying.
- **Real-time telemetry** belongs in an Eventhouse, not a lakehouse medallion — the layers map to KQL update policies / materialized views instead (see [`rti-eventhouse-shaping.md`](./rti-eventhouse-shaping.md)).

## See also

- [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) — the per-layer optimization matrix and the three transform options (MLV / notebook / Dataflow Gen2)
- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) — the gold-table physical-shape contract the boundary protects
- [`delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md) — per-layer maintenance cadence
- [`../agents/lakehouse-engineer.md`](../agents/lakehouse-engineer.md) · [`../agents/fabric-architect.md`](../agents/fabric-architect.md) — own the medallion build + the layer-to-workspace topology

## Provenance

Codifies house opinion #3 ("Medallion or justify its absence … never serve bronze to Direct Lake / the SQL endpoint") from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Medallion on OneLake](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture) and the per-layer table in [`../knowledge/medallion-on-onelake.md`](../knowledge/medallion-on-onelake.md) (Microsoft Learn, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
