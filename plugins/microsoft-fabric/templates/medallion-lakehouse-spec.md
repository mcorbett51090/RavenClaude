# Medallion lakehouse spec — <SUBJECT AREA>

> Owned by `lakehouse-engineer`. See `knowledge/medallion-on-onelake.md` for the per-layer rules.

## Sources
| Source | Format | Landing method (shortcut / copy / mirror) | Cadence |
|---|---|---|---|

## Bronze (raw / immutable)
- **Tables:** <list>
- **Format:** <original / Delta>; **shortcut vs copy:** <which, why>
- **Optimization:** ingest-speed priority; V-Order **off**; small files OK; partition only if high-frequency.
- **Not served to Direct Lake / SQL endpoint.**

## Silver (curated)
- **Transforms:** dedup / type-standardize / conform / join — <list>
- **Engine:** <materialized lake view | notebook | Dataflow Gen2 + why>
- **Optimization:** 128-256 MB files; Liquid Clustering on <keys>; deletion vectors on <merge tables>; auto-compaction on; NEE on.
- **Data-quality constraints:** <constraints / expectations>

## Gold (business-ready)
- **Tables / data products:** <list + grain>
- **Engine:** <MLV | notebook | T-SQL if warehouse-served>
- **Optimization:** **V-Order required**; 400 MB-1 GB files; 8M+ row groups; scheduled `OPTIMIZE … VORDER`.
- **Consumed by:** <Direct Lake model | SQL endpoint | Spark> — Direct Lake readiness: <framed? MLV-not-SQL-view?>

## Maintenance schedule
| Layer | OPTIMIZE cadence | VORDER | Notes |
|---|---|---|---|
