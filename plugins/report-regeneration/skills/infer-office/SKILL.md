---
name: infer-office
description: "Stage 1 of the report-regeneration OFFICE (docx) pipeline. Parses a Word .docx template into a schema-valid Report Structure Graph (RSG) via stdlib zipfile + xml.etree over word/document.xml: per-node OOXML body-walk anchor, role, rebind class, confidence, provenance, plus the deterministic data-shaped-literal detector reused from the HTML lane. Stdlib-only, Python 3.9; python-docx optional."
---

# infer-office

The **first stage** of the `report-regeneration` **Office (Word/`.docx`)** pipeline — the exact
analogue of [`infer-report-structure`](../infer-report-structure/SKILL.md) for OOXML. It reads a
Word `.docx` **template** and emits a **Report Structure Graph (RSG)** — the same format-neutral
ordered tree, node taxonomy, and deterministic detector as the HTML lane, but keyed on **OOXML
anchors** instead of CSS selectors. The RSG is an **addressing-and-verification structure, NEVER a
generator** (`knowledge/core-architecture-spec.md` §2).

## How it parses (stdlib-first)

`infer_office.py` opens the `.docx` (an OPC/ZIP package) with **`zipfile`**, reads
`word/document.xml`, and walks `w:body` in **document order** (order is load-bearing — the V2
frozen-complement diff and V3 re-inference isomorphism both depend on it) with **`xml.etree`**. It
emits one RSG node per content element: paragraphs (`w:p`), runs (`w:r`), tables
(`w:tbl`/`w:tr`/`w:tc`), and inline images (`w:drawing`). Non-content property elements
(`w:pPr`/`w:rPr`/`w:sectPr`/…) are not emitted as nodes but are still counted in anchor indices.

`python-docx` is **optional acceleration** via a graceful `try`/import that changes nothing when
absent (the stdlib `zipfile` + `xml.etree` walk is the sole code path). No network, no live LLM call.

## The OOXML anchor grammar (owned by the shared resolver)

Every anchor is `kind:"ooxml_path"` (the only Office kind the RSG schema admits) and is **produced
by — and resolves back through — the shared grammar in [`scripts/rr_anchor.py`](../../scripts/rr_anchor.py)**,
which OWNS the Office anchor contract. Two forms, both pinned in `core-architecture-spec.md` §2:

| Anchor | When | Example |
|---|---|---|
| `body`-rooted body-walk path | the default for any node | `body/p[3]/r[1]`, `body/tbl[1]/tr[2]/tc[2]/p[1]/r[1]` |
| `bookmark(NAME)` path | a `w:bookmarkStart` governs the node (the surgical-KPI archetype) | `bookmark(revenue_total)` |

A `step` is `local[n]` — a **namespace-stripped** local name plus a **1-based index among
same-local-name element siblings, document order**. Because indices bucket by local name, property
elements never perturb a run's or paragraph's index. Both the producer (this skill, over `xml.etree`
children) and the resolver (`rr_anchor`, over `expat` children) apply the **one** shared indexing
rule (`rr_anchor.ooxml_sibling_index`), and a cross-check test locks their agreement in both
directions — so producer/consumer anchor grammar cannot drift. `rebind-office` and the Office
fidelity-harness extension build on this contract next wave.

## The load-bearing detector — reused verbatim

The `data_shaped_literal` field is the output of **the same** deterministic, non-inference detector
as the HTML lane (`infer.detect_data_shaped_literal` is imported directly — single source of truth),
flagging currency / number / date / percent / unit / known-entity shapes on each run's own text.

## The two SPEC hard rules (override any inference)

1. **Construction rule (§4/§6.4)** — a `w:drawing`/raster/embedded-binary node is FORCED to
   `regenerate` (a transplanted binary cannot be proven data-free).
2. **Earned-frozen rule (§4)** — a data-shaped literal in a candidate-`frozen` node FORCE-DEMOTES it
   to `needs-review`, regardless of classifier confidence.

Semantic role/class labeling is a **rule-based STUB** (`method:"rule-based"`) keyed on OOXML
structure: paragraph style (`pStyle` = `Title`/`Heading*` → heading), **bookmark governance** = an
explicit data-binding marker (bookmarked + data-shaped run → `surgical`), table-cell membership, and
drawing presence. A data-shaped run with **no** bind marker (an unmarked numeric table cell, a bare
`+8.5%`) surfaces as `needs-review` (the V6 coverage gap). There is **no live LLM call**.

## Security

Stdlib XML parsers are XXE / billion-laughs vulnerable and `defusedxml` is off this plugin's
stdlib-only path, so both this skill and `rr_anchor` **reject any DOCTYPE/DTD/ENTITY** in
`document.xml` (a valid OOXML body never carries one; the rejection closes external-entity and
entity-expansion attacks at the source and treats a hostile template as **data, never
instructions**).

## Usage

```shell
# From the repo root (paths are relative + path-guarded, or an in-repo absolute path):
python3 plugins/report-regeneration/skills/infer-office/infer_office.py \
    --in  tests/fixtures/report-regeneration/sample-report.docx \
    --out tests/fixtures/report-regeneration/_out/rsg.office.json

# JSON summary on stdout (exit-coded: 0 ok, 2 usage/path/parse/schema error):
python3 .../infer_office.py --in <template.docx> --out <rsg.json> --format json
```

Flags: `--in`, `--out` (required), `--template-id` (default: input filename stem),
`--confidence-threshold` (default `0.6`), `--format {text,json}`.

## Fixture

The synthetic `.docx` fixture
[`tests/fixtures/report-regeneration/sample-report.docx`](../../../../tests/fixtures/report-regeneration/sample-report.docx)
is built programmatically with stdlib `zipfile` by
[`scripts/build_sample_docx.py`](../../scripts/build_sample_docx.py) — a valid minimal Word document
(title, three sections, a table with numeric cells, a bookmarked currency value, an inline image),
entirely fabricated ("Northwind Traders", Q2 2025). It is **byte-reproducible** from its generator
(a test asserts the committed binary matches).

## Constraints

Stdlib-only (`argparse`/`zipfile`/`xml.etree`/`json`/`re`/`os`/`sys`), runs on **Python 3.9.6 with
no pip installs**; `python-docx` is optional acceleration only. No network, no subprocess (beyond the
CLI test). Path-guarded (rejects `..` and repo-escape, reusing `infer._safe_path`). The emitted RSG
is **validated against `rsg.schema.json` before it is written** — an invalid build refuses to write
and exits `2`.

## Tests

[`tests/test_infer_office.py`](tests/test_infer_office.py) asserts the sample docx parses, the RSG
validates against the schema (format `office`), the bookmarked currency run is `surgical`, the
period-label surfaces, the earned-frozen demotion + drawing construction rule fire, numeric cells
surface, the detector is reused from the HTML lane, the XXE guard rejects a DOCTYPE, and the fixture
is byte-reproducible. Runs under `pytest` **or** as a plain script (`python3
tests/test_infer_office.py`). The producer↔resolver cross-check lives in
[`../../scripts/tests/test_rr_anchor.py`](../../scripts/tests/test_rr_anchor.py).
