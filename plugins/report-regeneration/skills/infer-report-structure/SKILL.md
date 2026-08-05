---
name: infer-report-structure
description: "Stage 1 of the report-regeneration HTML pipeline. Parses an HTML template into a schema-valid Report Structure Graph (RSG): per-node stable anchor, role, rebind class, confidence, provenance, plus the deterministic non-inference data-shaped-literal detector that drives the earned-frozen rule. Stdlib-only, runs on Python 3.9."
---

# infer-report-structure

The **first stage** of the `report-regeneration` HTML pipeline. It reads an HTML report
**template** and emits a **Report Structure Graph (RSG)** — a format-neutral ordered tree that
downstream stages (binding-manifest generation, surgical rebind, the fidelity harness) address
and verify against. The RSG is an **addressing-and-verification structure, NEVER a generator**
(`knowledge/core-architecture-spec.md` §2).

## What it produces

`infer.py` walks the template in **document order** (order is load-bearing — the V2 frozen-
complement diff and V3 re-inference isomorphism both depend on it) and emits one RSG node per
element. Each node validates against [`knowledge/rsg.schema.json`](../../knowledge/rsg.schema.json)
and carries:

| Field | Source |
|---|---|
| `anchor` | a **stable node identity** — `element_id` when the element has an `id`, else a `css_selector` built from `nth-of-type` steps anchored at the nearest id-bearing ancestor. **Never a raw char-offset** (RT1-F10). |
| `role` | rule-based semantic role (`kpi-value`/`table-cell`/`narrative`/`chart`/`image`/`period-label`/`heading`/`metadata`/`static-chrome`/`unknown`). |
| `class` | rebind class (`frozen`/`surgical`/`regenerate`/`needs-review`). |
| `confidence` | 0–1; sub-threshold ⇒ `needs-review`. |
| `provenance` | `method` (`native-parse`/`rule-based`/`llm-labeled`), `source`, **`source_period`**, and `pbi_route` (`xmla`/`rest`/`screenshot`/null) for Power-BI-sourced nodes. |
| `data_shaped_literal` | output of the pinned, **non-inference, deterministic** detector. |

## The load-bearing detector — `data_shaped_literal`

`detect_data_shaped_literal(text)` flags **currency / number / date / percent / unit /
known-entity** shapes deterministically. It is intentionally blind to meaning: it **cannot** tell
`100%` the marketing tagline from `100%` the KPI, or `Fiscal Year 2024` the static citation from a
data-bound period — and it must not try. That is exactly why it is the right tool for the
**earned-frozen** rule (§4): **any data-shaped literal in a candidate-`frozen` node force-demotes
it to `needs-review`, regardless of classifier confidence.** It is independent of the LLM-accuracy
ceiling.

## The two SPEC hard rules (override any annotation or confidence)

1. **Construction rule (§4/§6.4)** — a node that renders as a **raster** or carries an
   **embedded binary/data cache** is FORCED to `regenerate` (a transplanted binary cannot be
   proven data-free). This holds even when the fixture annotates the image `data-role="frozen"`
   (e.g. the header logo, the Power BI screenshot).
2. **Earned-frozen rule (§4)** — a data-shaped literal in a candidate-`frozen` node FORCE-DEMOTES
   it to `needs-review`.

Semantic role/class labeling here is a **rule-based STUB** (`method: "rule-based"`) that reads the
fixture's explicit annotation scheme (`data-role` / `data-bind` / `data-shape` / `data-period` /
`data-section-role` / `data-source`). There is **no live LLM call** — the model-assisted slot
labeling of §2 lands in a later stage.

## Usage

```shell
# From the repo root (paths are relative + path-guarded, or an in-repo absolute path):
python3 plugins/report-regeneration/skills/infer-report-structure/infer.py \
    --in  tests/fixtures/report-regeneration/sample-report.html \
    --out tests/fixtures/report-regeneration/_out/rsg.sample.json

# JSON summary on stdout (exit-coded: 0 ok, 2 usage/path/parse/schema error):
python3 .../infer.py --in <template.html> --out <rsg.json> --format json
```

Flags: `--in`, `--out` (required), `--template-id` (default: input filename stem),
`--confidence-threshold` (default `0.6`), `--format {text,json}`.

## Companion fixture

[`tests/fixtures/report-regeneration/new-data.sample.json`](../../../../tests/fixtures/report-regeneration/new-data.sample.json)
holds plausible NEW-period (Q2 2025) values keyed to every `data-bind` in the corpus, so the
downstream rebind/harness stages and the acceptance test share one consistent new dataset.

## Constraints

Stdlib-only (`argparse`/`html.parser`/`json`/`re`/`os`/`sys`), runs on **Python 3.9.6 with no pip
installs**; `lxml`/`selectolax` are optional acceleration via a graceful `try`/import that changes
nothing when absent. No network, no subprocess. Path-guarded (rejects `..` and repo-escape,
mirroring `svg-report-lint.py`). The emitted RSG is **validated against `rsg.schema.json` before it
is written** — an invalid build refuses to write and exits `2`.

## Tests

[`tests/test_infer.py`](tests/test_infer.py) asserts the sample report parses, the RSG validates
against the schema, every `data-bind` node is found, the detector flags the tricky cases (a year,
a percent-shaped tagline), the earned-frozen demotion fires, and the companion new-data fixture
covers every binding. Runs under `pytest` **or** as a plain script (`python3 tests/test_infer.py`)
so it needs no third-party test runner.
