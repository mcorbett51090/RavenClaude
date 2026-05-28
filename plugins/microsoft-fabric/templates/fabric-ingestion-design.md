# Fabric ingestion design — <SOURCE → DESTINATION>

> Owned by `data-factory-engineer`. Traverse `knowledge/fabric-data-movement-decision-tree.md` first.

## Decision
- **Source:** <system / format / connector>
- **Destination:** <lakehouse / warehouse / eventhouse table in OneLake>
- **Method:** <mirroring | copy-job | pipeline+copy-activity | eventstream | dataflow-gen2>
- **Why (from the tree):** <in-Fabric auto-mirror? streaming? turn-key replica? incremental/CDC without a pipeline? orchestration?>

## Load pattern
- **Mode:** <full | watermark-incremental | CDC | continuous>
- **Watermark / CDC key:** <column / mechanism>
- **Idempotency:** <how re-runs avoid dupes>
- **Schedule / trigger:** <cron | event | continuous>

## Cost & capacity
- **Mirroring note (if used):** free to replicate up to the CU storage allowance; **query compute always billed**; cross-region egress = <yes/no>.
- **Capacity impact:** <background CU consumer; scheduled to ride 24-h smoothing?>
- **Fast Copy (if Dataflow Gen2):** <eligible? folding-safe steps only?>

## Validation
- [ ] First-run row counts reconcile to source
- [ ] Incremental run picks up only deltas
- [ ] Failure/retry behavior verified
