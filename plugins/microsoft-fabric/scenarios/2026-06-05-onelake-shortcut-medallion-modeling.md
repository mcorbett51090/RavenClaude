---
scenario_id: 2026-06-05-onelake-shortcut-medallion-modeling
contributed_at: 2026-06-05
plugin: microsoft-fabric
product: onelake
product_version: "2026.05"
scope: likely-general
tags: [onelake, shortcut, medallion, one-copy, mirroring, gold]
confidence: medium
reviewed: false
---

## Problem

A new Fabric workspace had been stood up by a partner who "copied everything into the lakehouse to be safe": a nightly Data Factory pipeline `Copy`-ied an ADLS Gen2 landing zone into a bronze Delta table, a second copy duplicated a sibling team's already-curated OneLake dimension tables into this workspace, and CU consumption plus OneLake storage were both climbing. The team asked for a medallion redesign and assumed they needed a bigger SKU to keep up with the copy jobs.

## Constraints context

- Source data already lived in two accessible places: an **ADLS Gen2** account (raw landing) and **another OneLake workspace** (a platform team's curated conformed dimensions).
- The partner's pattern was copy-first everywhere — violating house opinion #1 ("one copy in OneLake; reach for a shortcut before copying").
- F32 capacity; the redundant copy pipelines were a meaningful slice of daily CU.
- Schema-enabled lakehouse; gold consumed by a Direct Lake on-OneLake model downstream.

## Attempts

- Tried: traversing the OneLake-access tree ([`../knowledge/fabric-decision-trees.md`](../knowledge/fabric-decision-trees.md) "OneLake access — Shortcut vs Copy/Ingest") for each source instead of accepting the copy-everything pattern. Two of the three "ingests" were **read-only consumption of data that already existed in an accessible lake** — textbook **shortcut** candidates, not copies. Outcome: identified that the cross-workspace dimension copy and the ADLS raw copy could both become shortcuts.
- Tried (the moves that worked):
  1. Replaced the **cross-workspace dimension copy** with a **OneLake shortcut** to the platform team's curated tables — one source of truth, zero copy, storage stays with the owner and compute bills to this consuming capacity. Removed a whole pipeline.
  2. Replaced the **ADLS raw copy** with an **ADLS shortcut** into bronze; bronze became a virtualized view of the landing zone (still immutable, still the raw layer) rather than a duplicated dataset.
  3. **Kept the silver→gold transform as a real copy** — that is genuine ELT (cleansing, conforming, V-Ordering gold for the downstream Direct Lake model), which a shortcut cannot do (a shortcut is read-through, not a transform engine). Medallion boundaries preserved: bronze raw/immutable (now shortcut-backed), silver curated, gold business-ready.
- Tried (considered, ruled out): **mirroring** for the cross-workspace dimensions. Mirroring is for an *external operational DB*, not for data already sitting in OneLake — and it would have reintroduced a replica ("free to replicate, billed to query," not free either way). The data was already in OneLake, so a shortcut was the earlier/cheaper leaf. Outcome: ruled out.

## Resolution

The fix was **shortcut-first medallion modeling**, not a bigger SKU. Two of three "ingests" were read-only consumption of data already in an accessible lake → **shortcuts** (no copy, one source of truth); only the silver→gold transform stayed a real copy because it does work a shortcut can't. Removing the redundant copy pipelines cut daily CU and OneLake storage and removed a class of "which copy is current?" drift. Picking the **earliest matching leaf** (shortcut → auto-mirror → mirror → copy/ingest) is the rule.

**Action for the next consultant hitting this pattern:** when you inherit a "copied everything to be safe" workspace, do **not** size for the copy load — audit each ingest against the OneLake-access tree and convert every *read-only-consumption-of-already-accessible-data* copy into a **shortcut**, reserving real copies for genuine transforms (silver→gold). Confirm the source actually lives in an accessible lake before shortcutting (a shortcut to an external operational DB isn't a thing — that's mirroring). Apply [`../best-practices/one-copy-shortcut-before-copying.md`](../best-practices/one-copy-shortcut-before-copying.md) and [`../best-practices/lakehouse-medallion-layer-boundaries.md`](../best-practices/lakehouse-medallion-layer-boundaries.md). Field-note complement to those canonical rules.

**Sources (Microsoft Learn, retrieved 2026-06-05 — `[verify-at-use]`):** [OneLake shortcuts](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts) · [Choose the right data store](https://learn.microsoft.com/fabric/fundamentals/decision-guide-data-store) · [Medallion architecture in OneLake](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture). Shortcut billing (compute-to-consumer / storage-to-owner) and mirroring cost shape re-confirm before quoting to a client (house opinion #1 / #9).
