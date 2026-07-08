# Changelog — analytics-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.5] — 2026-07-08

Weekly Tier-A news sweep (2026-07-08) — **correction** in `CLAUDE.md`: `dbt-mcp` latest is **1.21.2** (re-verified via the PyPI JSON API), superseding the documented **1.20.1**. **Migration:** none — knowledge-file content only.

## [0.3.3] — 2026-07-01

Research-sweep **correction** (Tier-A weekly news sweep) — the dbt Fusion status line understated a scoped-GA flip. `knowledge/analytics-engineering-decision-trees.md` said "Fusion engine Stable for new envs"; per docs.getdbt.com (about-fusion) the Fusion engine is **GA for dbt-platform projects on Snowflake and in preview for other adapters** (BigQuery/Redshift/Databricks) — a narrower, and materially different, reality than an unqualified "Stable" (an engineer on a non-Snowflake adapter could otherwise adopt Fusion into a new env expecting production readiness that only exists on the Snowflake-on-dbt-platform path). Corrected **both** occurrences (the prose note :145 and the capability-map row :224) to the scoped GA + `[verify-at-use 2026-07-01]`; the **"dbt Core v2.0 in alpha — not GA"** clause is preserved (still true). Panels: usefulness → USEFUL/high; detailed review → APPROVE. **Migration:** none — knowledge-file content only.

## [0.3.2] — 2026-06-22

Version bump previously unlogged here; the change that set `0.3.2`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.3.1] — 2026-06-11

Research-sweep **correction** — refreshed the stale dbt version anchor, re-verified 2026-06-11 against the dbt-core v2 roadmap (primary).

### Fixed

- **`knowledge/analytics-engineering-decision-trees.md`** — the "Last verified … dbt Core docs (v1.8)" anchor and the capability-map "dbt Core / Cloud — GA" row now state: **v1.x remains the production default**; **dbt Core v2.0** (Rust engine shared with Fusion, Apache-2.0) was announced 2026-06-01 at Snowflake Summit in **alpha — NOT GA**; the Fusion engine reached Stable as the default for *new* dbt platform environments with a supported adapter. **Pin v1.x for production until v2.0 GA.** Explicit anti-fabrication note that secondary "v2.0 is here" coverage elides the alpha status. Source: [dbt-core v2 roadmap](https://github.com/dbt-labs/dbt-core/blob/main/docs/roadmap/2026-06-announcing-v2.md).
- Version **0.3.0 → 0.3.1** in `.claude-plugin/plugin.json` + `marketplace.json` (lockstep).

## [0.3.0] — 2026-06-05

Value-add build-out — extending PR #315 (which added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`) against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §8 "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `fan-out-join-double-counting` (re-aggregate the many-side to the grain; `DISTINCT` doesn't fix a grain bug), `incremental-late-arriving-data` (watermark on load time, not event time; merge on the business key), `semantic-layer-metric-drift` (distinguish drift from different questions; name the metrics), `test-coverage-gap-silent-corruption` (`relationships` + row-count anomaly catch the silent INNER-JOIN drop PK tests miss). Matches the existing `scenarios/README.md` index and the 9-field schema (the README/index was staged by PR #315; this build wrote the narrative files it pointed at).
- **Decision-tree knowledge.** `knowledge/data-quality-and-contract-decision-trees.md` — two new Mermaid trees: which dbt test expresses a given data-quality guarantee (not_null/unique/accepted_values/relationships/range/anomaly/custom-generic/singular + severity), and model-contract-vs-test-vs-both at a published boundary, plus a dated capability note. Complements PR #315's `analytics-engineering-decision-trees.md` (which already covers materialization / model-layer / star-vs-OBT / freshness / metric-placement / DQ-triage / incremental-strategy / semantic-tool).
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP runtime tier — recommend-not-bundle), §7 (bundled-MCP disposition — `dbt-mcp` recommend-not-bundle), §8 (value-add completeness table), §9 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** The obvious candidate — first-party `dbt-mcp` (dbt Labs, Apache-2.0, `1.20.1` as of 2026-06-04) — fails the doctrine's bundling bar on three independent counts: first-party-from-vendor, per-tenant + authenticated (a dbt Platform token is a secret), and write-capable (CLI tools can modify warehouse objects). Documented the `uvx` / `claude mcp add` path + `DISABLE_*` least-privilege posture + `security-reviewer` gate instead of an `mcpServers` entry. No invented servers.
- **No bundled LSP (`.lsp.json`).** dbt's primary file type is Jinja-templated SQL, which generic SQL LSPs can't navigate (lineage is dbt's compiled DAG, not an LSP concept). `sqls` is live-DB-backed (a secret) + pre-1.0 + not Jinja-aware; `sqlfluff-lsp` is dbt-Jinja-aware but needs a per-project `.sqlfluff` (dialect + project dir), so neither ships zero-config. Recommended SQLFluff (its LSP or pre-commit/CI) configured to the consumer's dialect instead.
- **No `scripts/`, `bin/`, monitors, output-styles, settings, or themes.** The high-value runtime checks for this domain are dbt's own (`dbt build`/`test`/`source freshness`/model contracts) and SQLFluff's; a hand-rolled script would re-implement dbt badly or assume a project layout we can't. Nothing else cleared the "groundable + broadly valuable, doesn't duplicate an existing surface" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover modeling / semantic layer / testing / incrementals / CI governance; no 6th skill added (the scenarios + second decision-tree file extend reach without a new agent, per the team-growth-as-knowledge house rule).
- **No `NOTICE.md`** — nothing third-party is bundled; `dbt-mcp` / `sqls` / `sqlfluff-lsp` are referenced and cited, not vendored.

### Verify-at-use

- `dbt-mcp` version (`1.20.1`, 2026-06-04), tool count (~60+), and the exact env-var / `DISABLE_*` toggle names — re-confirm against the repo `.env.example` and docs.getdbt.com. `sqls` (sqls-server/sqls) maintenance status / pre-1.0 state; `sqlfluff-lsp` (VasanthakumarV) and SQLFluff 4.0.x Rust routines. dbt test inventory (`dbt_utils`, `dbt_expectations` package contents) and model-contract constraint support per warehouse. All version-volatile — re-confirm against the vendor before quoting.

## [0.2.2] — earlier

3-agent analytics-engineering team (analytics-engineer, semantic-layer-engineer, data-quality-testing-engineer): 5 skills, a consolidated decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook. PR #315 added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`. Seams to data-platform, database-engineering, tableau, microsoft-fabric, applied-statistics.
