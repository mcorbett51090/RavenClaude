---
name: rebind-manifest
description: "Pipeline stage 2 of report-regeneration (detect -> strip -> rebind): turn an RSG + the OLD template + the new dataset into a schema-valid Binding Manifest and a taint dictionary. Enforces the earned-frozen rule (a data-shaped literal / old-taint / new-dataset value demotes a candidate-frozen node to needs-review), forces raster/embedded-cache nodes to regenerate, and proposes each node's data_query. Reach for this when building or amending a Binding Manifest."
---

# Skill: rebind-manifest (report-regeneration stage 2)

The **surgeon planning the transplant.** Given a Report Structure Graph (RSG), the OLD
template, and the new dataset, this stage builds a versioned, human-reviewable **Binding
Manifest** plus the **taint dictionary** that the V4 egress leg scans against. It addresses +
classifies + proposes queries — it never renders.

> **The honest guarantee (verbatim — never soften it):** the plugin GUARANTEES only (a) **no
> old-client-data leak** and (b) **every low-confidence classification is surfaced for human
> review**. It does NOT guarantee a human-free-correct report. `needs-review` is guarantee (b)
> made mechanical.

## Run it

```shell
python3 build_manifest.py \
    --rsg <rsg.json> --template <old-template.html> --new-data <data.json> \
    --out <manifest.json> [--taint-out <taint-dict.json>] \
    [--manifest-version 0.1.0] [--confidence-threshold 0.7] [--format json|text] [--pretty]
```

Exit codes: `0` valid manifest; `2` usage / path-guard / parse error / **input RSG failed
`rsg.schema.json`** (fail-closed); `3` manifest built but **failed** `binding-manifest.schema.json`.

`--new-data` shape: `{"source_ref": "...", "source_period": "...", "values": [...] | {...}}`.
`values` is the new value domain the earned-frozen rule tests against; if omitted, every scalar
leaf (minus reserved metadata keys) is the domain.

## What it does (mirrors `knowledge/core-architecture-spec.md` §3/§4/§6)

1. **Taint dictionary** from the OLD template — distinct rendered value literals (via the
   pinned, non-inference data-shaped-literal detector) + identity strings (author / company /
   title / source-filename), including a declared prior-artifact taint block
   (`old_company: "..."` comment convention) when present.
2. **Earned-`frozen` rule.** `frozen` is never the default. A candidate-`frozen` node is
   demoted to `needs-review` if an **independent re-run** of the detector over its rendered
   text fires (or the RSG already flagged it), OR the text carries an old-taint value, OR it
   carries a new-dataset value. A **data-shaped literal force-demotes regardless of classifier
   confidence.** (The RSG is already schema-forbidden from carrying `frozen` + `data_shaped_literal:true`,
   so the demotion authority here is the independent detector, not the RSG flag.)
3. **Raster / embedded-cache force.** Any node that renders as a raster or carries an embedded
   binary/data cache is forced to `regenerate` — a transplanted blob cannot be proven data-free.
4. **Propose one binding per NON-static node:** `node_id`, `anchor`, `class`, `confidence`,
   `provenance {source, source_period, method, pbi_route}`, `data_query`. A `frozen` binding
   carries **no** `data_query`; every non-frozen class **must** carry one.
5. **Validate** the manifest against `binding-manifest.schema.json` (stdlib-only validator).

## Conservative-by-design note

The detector is deliberately non-inference: it fires on `"100%"` in a marketing tagline exactly
as on a KPI's `"100%"`. Over-flagging a candidate-`frozen` node to `needs-review` is the **safe**
direction (guarantee (b)); under-flagging a data-bound node classed `frozen` is what a leak
looks like.

## Constraints

Stdlib only (`argparse` / `html.parser` / `re` / `json` / `pathlib`), Python 3.9.6, no pip, no
network, no subprocess. Path-guarded (rejects `..` traversal). Code is written to the schemas in
[`../../knowledge/`](../../knowledge/).

## Tests

`python3 -m unittest tests.test_manifest` (run from this skill directory) — demotion, taint dict
(inline + real corpus), raster→regenerate, and schema-validity.
