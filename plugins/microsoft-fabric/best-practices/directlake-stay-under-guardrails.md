# Stay under the Direct Lake guardrails — or know exactly how your mode fails when you don't

**Status:** Absolute rule (on-OneLake side) / Primary diagnostic — exceeding the per-SKU guardrails either silently degrades to DirectQuery (on-SQL) or errors/fails framing (on-OneLake); the failure shape is mode-specific and must be designed for.

**Domain:** Direct Lake / semantic models / capacity

**Applies to:** `microsoft-fabric`

---

## Why this exists

Direct Lake loads Delta into VertiPaq **on demand**, bounded by per-SKU **resource guardrails** (memory, Parquet file count, row-group sizing). What happens when you cross a guardrail depends entirely on the mode (house opinion #8):

- **Direct Lake on SQL** → the query **falls back to DirectQuery**. Report users keep working, but silently slower — a latency regression you only catch in monitoring.
- **Direct Lake on OneLake** → **no fallback**. A table that isn't framed/processed **errors**; **framing itself fails** if a Delta table exceeds the guardrails (e.g. more than **10,000 Parquet files**).

Either way the cure is upstream gold shaping, not a model setting. This rule is the gold-shape ↔ capacity seam: keep the physical table inside the envelope so the model never has to fall back or error.

## How to apply

Shape gold to keep file count, row groups, and memory inside the SKU envelope; then verify before shipping.

```text
File count   → keep well under ~10,000 Parquet files (OPTIMIZE to compact small files).
Row groups   → 1M–16M rows per row group; Direct Lake prefers LARGE column segments.
File size    → 400 MB–1 GB on gold for Direct Lake.
Memory       → table/model footprint must fit the SKU's VertiPaq budget (bigger SKU = bigger budget).
```

- **Compact aggressively** on gold so small-file proliferation never approaches the file-count guardrail (see [`delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md)).
- **Pick the right SKU** — guardrails scale with the SKU; a model that errors/falls back on F64 may be fine on F128. Size for the model, not just the workload (see [`capacity-size-to-average-not-peak.md`](./capacity-size-to-average-not-peak.md)).
- **On-SQL:** you *can* disable fallback (`DirectLakeBehavior`), which converts a silent slowdown into a loud error — sometimes the right call so guardrail breaches surface in testing, not production.

**Do:**
- Design gold to stay under the guardrails regardless of mode — fewer, larger files; large row groups.
- Name the mode first, then design to *its* failure shape (on-OneLake errors/empty; on-SQL falls back).
- Monitor for DirectQuery fallback on-SQL — it's the early warning you're near a guardrail.

**Don't:**
- Assume on-OneLake "falls back gracefully" — it errors; there is no DirectQuery safety net.
- Let gold drift past ~10,000 Parquet files — framing fails outright.
- Treat a fallback as harmless on-SQL — it's a latency regression and a guardrail signal.

## Edge cases / when the rule does NOT apply

- **Small models well inside the SKU envelope** never approach a guardrail — the rule is a large-model concern, but you still name the mode.
- **An intentional composite model** (on-OneLake) mixing Direct Lake + Import/DQ tables is a design choice, not a fallback.
- **Import mode** has no guardrail-fallback behavior — it just refreshes; this rule is Direct-Lake-specific.

## See also

- [`name-your-direct-lake-mode.md`](./name-your-direct-lake-mode.md) — the mode whose failure shape this rule designs for
- [`shape-gold-for-direct-lake.md`](./shape-gold-for-direct-lake.md) · [`delta-optimize-vacuum-cadence.md`](./delta-optimize-vacuum-cadence.md) — the gold shaping + compaction that keeps you under
- [`../knowledge/direct-lake-and-semantic-models.md`](../knowledge/direct-lake-and-semantic-models.md)
- [`../agents/fabric-semantic-model-engineer.md`](../agents/fabric-semantic-model-engineer.md) · [`../agents/fabric-admin.md`](../agents/fabric-admin.md)

## Provenance

Codifies house opinion #8 from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [Direct Lake overview — Fabric capacity requirements](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview), [How Direct Lake works — framing/DirectQuery fallback](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works) (framing may fail past ~10,000 Parquet files; `DirectLakeBehavior` controls fallback, *on-SQL only*; "Direct Lake on OneLake doesn't support DirectQuery fallback") and [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) (row-group 1M–16M, prefer large segments) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
