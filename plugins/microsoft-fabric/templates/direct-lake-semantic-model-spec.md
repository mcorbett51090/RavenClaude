# Direct Lake semantic-model spec — <MODEL NAME>

> Owned by `fabric-semantic-model-engineer`. See `knowledge/direct-lake-and-semantic-models.md`.

## Storage mode
- **Mode:** <Import | DirectQuery | **Direct Lake**>
- **Direct Lake mode:** <**on OneLake** (no fallback, composite OK) | **on SQL** (falls back; OLS/RLS forces it)>
- **Why this mode:** <freshness vs perf vs feature need>

## Tables & relationships
| Table | Source (lakehouse/warehouse gold) | Role (fact/dim) | Grain |
|---|---|---|---|

- Relationships: <list>

## Gold-table requirements (coordinate with lakehouse/warehouse engineer)
- [ ] V-Order on; 400 MB-1 GB files; 8M+ row groups
- [ ] Framed and current (framing posture: <on refresh / on schedule>)
- [ ] If on-OneLake: built on a table or **materialized lake view**, not a non-materialized SQL view
- [ ] OneLake-security roles correct (on-OneLake misconfig → *empty* results, not error)

## Fallback / failure posture
- **On-SQL:** what would force DirectQuery (guardrails / unsupported features / SQL OLS-RLS) and how avoided.
- **On-OneLake:** what would error (unprocessed table) or return empty (security) and how avoided.

## Deployment
- PBIP + TMDL in git; live-edit against the workspace model; **publish via Fabric Git integration** (not Desktop Publish).
- **DAX measures / visuals →** `power-platform/power-bi-engineer`.
