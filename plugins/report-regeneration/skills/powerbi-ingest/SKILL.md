---
name: powerbi-ingest
description: "Pipeline-facing Power BI ingestion adapter, wrapping scripts/powerbi_probe.py for two modes: `data` runs every dax-kind Binding Manifest binding via REST executeQueries (service-principal/token from ENV ONLY), returning a data.json-shaped fragment keyed by data_query.expression with source_period stamped -- a genuinely independent V1 recompute source for a PBI-sourced value. `shot` captures a fresh report image via ExportToFile (Playwright fallback), packaging it as the embedded image for a regenerate-class PBI node with source_period stamped so period-coherence can catch a stale screenshot. Fail-closed throughout: no creds/route/period => not_captured + the named fallback (manual-figure-labeled-unverified for data, user-provided-image for shot), never a fabricated value or period. Token never logged. Reach for this to turn a Binding Manifest's PBI-sourced bindings into pipeline artifacts. NOT for manifest construction (rebind-manifest) or running the fidelity harness itself (report-fidelity-harness)."
---

# Skill: powerbi-ingest

The **pipeline-facing adapter** over the Phase-0 `scripts/powerbi_probe.py` probe.
Where the probe answers "can we reach Power BI at all" (a one-shot CLI receipt),
this skill answers the pipeline's actual question: *given a Binding Manifest,
produce the artifact the next stage needs.*

> **The honest guarantee (verbatim — never soften it):** the plugin GUARANTEES only
> (a) **no old-client-data leak** and (b) **every low-confidence classification is
> surfaced for human review**. A successful `data`/`shot` capture is NOT a claim
> the value is correct or the screenshot's period is current — those are the
> fidelity harness's V1 and period-coherence legs, run downstream of this adapter.

## Read first

- [`../../scripts/powerbi_probe.py`](../../scripts/powerbi_probe.py) — the probe
  this adapter wraps (auth, routes, fail-closed contract, env vars).
- [`../../knowledge/powerbi-ingest-contract.md`](../../knowledge/powerbi-ingest-contract.md)
  §3 (how a pulled figure becomes a verifiable V1 source) and §4 (the screenshot is
  a `regenerate` asset, always period-coherence-guarded).
- [`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md)
  §3 (the `data_query` kinds — `dax`, `screenshot-capture` — and provenance's
  `source_period` + `pbi_route`).

## Two pipeline-facing modes

### `data` — manifest dax-kind bindings → new-data fragment

```shell
python3 powerbi_ingest.py data --manifest <manifest.json> \
    [--source-period 2025-Q1] [--out <data-fragment.json>] \
    [--receipt-out <receipt.json>] [--format json|text] [--pretty]
```

Runs every binding whose `data_query.kind == "dax"` through
`powerbi_probe.execute_dax_query()` (REST `executeQueries`, a **fresh HTTP
round-trip per binding** — never a cached result from manifest-build time) and
assembles:

```json
{
  "dataset_id": "<POWERBI_DATASET_ID>",
  "period": "2025-Q1",
  "values": {
    "EVALUATE ROW(\"revenue_total\", [Revenue Total])": {"value": "4821300", "type": "number", "period": "2025-Q1"}
  }
}
```

This is a **data.json-shaped fragment**, keyed by each binding's
`data_query.expression` — the exact key
[`report-fidelity-harness`](../report-fidelity-harness/harness.py)'s V1 leg
(`leg_v1()`) indexes new-data by (`expr_bindings.setdefault(dq["expression"], ...)`).
Merge it into (or use it as) a `--new-data` file for the harness, and the PBI
value becomes a genuinely independent V1 recompute source — the fresh query, not
the binding's own inference path (contract §3).

**`period` resolution (mirrors the harness's own `leg_period()` fallback exactly,
so this adapter's default agrees with what the harness would fall back to
anyway):** `--source-period` if given, else the first non-null
`provenance.source_period` across the manifest's dax-kind bindings (document
order). If neither resolves, the run fails closed rather than stamping an
unattributed value.

### `shot` — ExportToFile capture → `regenerate`-node embed

```shell
python3 powerbi_ingest.py shot --manifest <manifest.json> --node-id <id> \
    [--source-period 2025-Q1] [--out <capture-out-path>] \
    [--receipt-out <receipt.json>] [--format json|text] [--pretty]
```

Looks up `--node-id` in the manifest (fatal, exit 2, if absent — a caller bug),
resolves `source_period` (CLI override, else the binding's own
`provenance.source_period`; **fails closed BEFORE any network call** if neither
resolves — an unstamped screenshot cannot be period-coherence-guarded), then
calls `powerbi_probe.probe_shot()` unchanged (ExportToFile primary, Playwright
fallback) and wraps the result:

```json
{
  "verdict": "PASS",
  "node_id": "pbi-screenshot",
  "class": "regenerate",
  "route": "export-to-file",
  "path": "/tmp/....png",
  "source_period": "2025-Q1",
  "period_coherence_checked": false
}
```

`class` is **always** `"regenerate"` — the embed's own construction rule, matching
core-architecture-spec.md §4 ("any node that renders as a raster... MUST be
`regenerate`"), independent of whatever class the looked-up binding happens to
carry (a mismatch is surfaced as a non-fatal `warnings` entry, since manifest
classification correctness is `rebind-manifest`'s job, not this adapter's).
`period_coherence_checked` stays `false` on every successful capture — this
adapter proves capture feasibility + period **attribution**, never period
**correctness**; that check is `report-fidelity-harness`'s job.

## Fail-closed contract (binding, inherited from the probe verbatim)

| Condition | Result |
|---|---|
| No `dax`-kind bindings in the manifest | `data` → `not_captured`, no network call |
| Missing `POWERBI_ACCESS_TOKEN`/`WORKSPACE_ID`/`DATASET_ID` | `data` → `not_captured`, fallback names the manual-figure-labeled-unverified path (contract §3) |
| No resolvable `source_period` | `data`/`shot` → `not_captured` **before any network call** — never a guessed period |
| A DAX result is `NULL`, or a query returns >1 row | that binding → `failed`, never a silently-picked/fabricated value |
| Neither ExportToFile nor Playwright succeeds | `shot` → `not_captured`, fallback names the user-provided-image path (contract §4/§5) |
| Some dax bindings succeed, some fail | `data` → `verdict: "PARTIAL"` (mirrors the harness's own PASS/PARTIAL/`not_captured` vocabulary) |

Tokens are read from `POWERBI_ACCESS_TOKEN` / `POWERBI_WORKSPACE_ID` /
`POWERBI_DATASET_ID` / `POWERBI_REPORT_ID` **env vars only** (identical to the
probe) and are **never** printed, logged, or embedded in any returned or written
structure — proven in `tests/test_powerbi_ingest.py` by asserting the fake token
is absent from stdout, the written fragment, and the written receipt.

## What this adapter deliberately does NOT do

- Validate the manifest against `binding-manifest.schema.json` (`rebind-manifest`'s
  job) — this stage duck-types only the shape it needs.
- Run the period-coherence check itself (`report-fidelity-harness`'s job).
- Support more than one target semantic model per invocation
  (`POWERBI_WORKSPACE_ID`/`POWERBI_DATASET_ID`). A dax-kind binding whose
  `data_query.source_ref` disagrees with the env dataset is not an error
  (`source_ref` may be a label, not a literal GUID) but is surfaced under
  `source_ref_mismatches` for a human to check — see "what breaks next" below.

## What breaks next

- **Percent-fraction ambiguity.** DAX often returns a percent-formatted measure as
  a raw 0–1 fraction (e.g. `0.187`), while the template may render `"18.7%"`.
  `infer_type_and_value()` deliberately does NOT guess a ×100 conversion from
  magnitude or column-name heuristics (that would be an unverified assumption
  baked into a "verifiable" source) — it labels every numeric DAX result `"number"`
  and passes the raw magnitude through. If the regenerate stage later renders that
  raw fraction as a percent string, V1's `canon_number()` comparison will disagree
  even though the underlying figure is correct. Detect it: a `data` run reports
  PASS but the downstream `report-fidelity-harness` V1 leg fails on a percent-typed
  node with a 100x-off magnitude in its evidence string.
- **Multiple semantic models in one manifest.** Only one `POWERBI_DATASET_ID` is
  queried per invocation; check `source_ref_mismatches` in the receipt if a
  manifest spans more than one PBI model.

## Constraints

Stdlib only (`argparse` / `json` / `os` / `re` / `sys` / `pathlib`), Python 3.9.6,
no pip, no third-party imports beyond the sibling `powerbi_probe` module. No
network at import — every network-capable branch is inside `ingest_data()` /
`ingest_shot()`, invoked only from `main()`. Path-guarded (rejects `..`
traversal). Does NOT auto-run.

## Tests

```shell
python3 -m unittest tests.test_powerbi_ingest -v   # run from this skill directory
```

A stdlib `http.server` mock stands in for the three Power BI REST endpoints this
adapter drives (`executeQueries`, `ExportTo` trigger, poll, file download) —
proving the `data` + `shot` flows end-to-end **offline**: real HTTP round-trips
against a loopback mock, a genuine `Running → Succeeded` poll loop for `shot`, a
partial-failure (`PARTIAL`) DAX scenario, every fail-closed-before-network path
(missing creds, missing period, no dax bindings, bad `--node-id`), and the token
never appearing in stdout / the written fragment / the written receipt. Also
regression-tests that the `scripts/powerbi_probe.py` refactor (extracting the
shared `execute_dax_query()`) did not change `probe_data()`'s own behavior.
