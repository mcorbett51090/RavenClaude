---
name: rebind-html
description: "Pipeline stage 3 (the HTML surgical output engine) for report-regeneration. Applies a Binding Manifest to a COPY of an HTML report template and emits the regenerated HTML: frozen nodes stay byte-identical, surgical/regenerate nodes are rebuilt under the zero-literal construction rule (strip the old value, THEN write the new one), needs-review nodes are left untouched but visibly flagged + logged. Stdlib-only (re/html.parser/json), jinja2 optional acceleration, runs on Python 3.9.6. NOT for structure inference (that's an earlier pipeline stage) or the fidelity harness (a separate downstream track) or Office/docx output (a later release lane)."
---

# Skill: rebind-html

## What this is

The **HTML surgical output engine** for `report-regeneration` — pipeline stage 3. Given
a template HTML file, a Binding Manifest
([`../../knowledge/binding-manifest.schema.json`](../../knowledge/binding-manifest.schema.json)),
and resolved new-source data, it produces a **same-format review-ready draft** by
performing schema-validated surgery on a **copy** of the template — never by
re-rendering from an abstract model. This is the "surgeon, not a renderer" model from
[`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md)
§1, applied to the HTML/web→PDF output format.

The engine consumes a manifest; it does **not** infer structure or propose bindings
(that is an earlier pipeline stage) and it does **not** run the fidelity harness (V1-V6 +
period-coherence — a separate, downstream track). Its one job is: **apply exactly what
the manifest says, per node class, and prove the frozen ones didn't move.**

## The four node classes (§4 of the architecture spec)

| Class | What this engine does |
|---|---|
| `frozen` | **No mutation.** After every other binding is applied, the engine re-checks that the node's exact byte span is identical between template and output (`_assert_frozen_unchanged`) — a defensive proof, not an assumption. |
| `surgical` | **Strip, then write** — two separate mutations, in that order. `strip_inner_by_id` (or `strip_attr_by_id` for a void element) empties the old value; `write_inner_by_id`/`write_attr_by_id` writes the new one. At the instant between the two calls the node provably carries no old instance value — by construction, not a downstream check. |
| `regenerate` | Same strip-then-write invariant, but the new value is **rendered** from a template string against the new-data JSON (stdlib `string.Template`, dotted-placeholder subclass — jinja2 is optional acceleration for templates that use native `{{ }}`/`{% %}` control syntax). A raster/void node (an `<img>`) is rebound by **attribute** (`src`, + `alt` if provided) — never by transplanting the old binary, per the spec's construction rule: "a transplanted binary blob cannot be proven data-free." |
| `needs-review` | **Left completely untouched** — content and attributes unchanged — but flagged: a machine-readable `data-rebind-flag="needs-review"` (+confidence) attribute on the opening tag, plus a visible on-page badge (`⚠ NEEDS REVIEW — human sign-off required (...)`) inserted as the node's first child (or as a sibling for a void element). Logged in the printed change-manifest. Never ships silently — this is guarantee #2 made mechanical. |

## Usage

```bash
python3 plugins/report-regeneration/skills/rebind-html/rebind_html.py \
    --template  tests/fixtures/report-regeneration/sample-report.html \
    --manifest  path/to/binding-manifest.json \
    --new-data  path/to/new-data.json \
    --out       tests/fixtures/report-regeneration/_out/regenerated.html
```

Add `--pretty` to pretty-print the printed JSON change-manifest. Every invocation prints
a JSON object to stdout: `{"schema": "report-regeneration/rebind-html@1", "ok": true|false,
..., "changes": [...]}`. Exit code `0` = success; `2` = usage / path-guard /
manifest-schema / anchor-not-found / missing-data-query / missing-new-data-key error
(never a silent partial write — a failure aborts the whole run and touches `--out` not at
all).

`--template`/`--manifest`/`--new-data`/`--out` are **relative paths, path-guarded**
(mirrors [`../../scripts/seed_defects.py`](../../scripts/seed_defects.py) and
`ravenclaude-core`'s `skills/svg-report-lint/lint.py` `_repo_root()`/`_safe_path()`
convention): no absolute paths, no `..` traversal, must resolve inside the repo root.
`--out` may never equal `--template` — this script works on a **copy**; the template file
on disk is never mutated (verified in `tests/test_rebind.py`'s CLI suite via a
before/after SHA-256 hash of the template file).

## The new-data lookup + template contract

A binding's `data_query.expression` is a **dot-path** into the `--new-data` JSON (e.g.
`"revenue.total"` looks up `{"revenue": {"total": ...}}`). `surgical` writes the resolved
value directly. `regenerate` treats the resolved value as either:

- a **plain string** — a template, rendered with `${dotted.path}` placeholders resolved
  against the SAME new-data object (stdlib-only, always works); or a native Jinja
  template (`{{ }}`/`{% %}`) — rendered via `jinja2` if it's importable, else a loud
  `RebindError` (never a silent stdlib mis-render of control-flow syntax that stdlib
  templating cannot express); or
- an **object** — for a raster/void node, `{"src": "...", "alt": "..."}` (alt optional);
  for a text node with an explicit template key, `{"template": "..."}`.

A missing dot-path segment, an unresolvable anchor, or a class/data_query mismatch
against the schema's `allOf` rule (frozen carries no `data_query`; every other class
must) is a loud `RebindError` → exit 2 — never a guess.

## Anchor support (this is an HTML-only engine)

Only `anchor.kind == "element_id"` and a simple `anchor.kind == "css_selector"` of the
shape `"#element-id"` are resolvable (both reduce to the same `id`-attribute lookup, via
regex — deliberately not a full DOM rebuild, matching `seed_defects.py`'s convention).
`json_pointer` and `ooxml_path` anchors are Office/docx-format anchors from the same
manifest schema; this engine rejects them loudly (`RebindError`) rather than guessing —
Office output is a later release lane (v0.2.0 per the plugin's CLAUDE.md).

## Tests

[`tests/test_rebind.py`](tests/test_rebind.py) — stdlib `unittest`, no pytest required:

- **`TestCoreMechanics`** — a small synthetic fixture exercising all four classes: frozen
  byte-identity (+ a must-fail check that a genuinely mutated frozen node IS caught),
  surgical strip-then-write with the old value asserted absent at both the strip midpoint
  and the final node, regenerate text + regenerate raster (both asserting the old
  value/asset is gone), needs-review flagging + untouched content, `html.parser`
  parseability, the stdlib `${dotted.path}` template renderer, the jinja2-absent
  loud-failure path, and three manifest-schema-violation rejections.
- **`TestSampleReportCorpus`** — end-to-end against the real
  [`tests/fixtures/report-regeneration/sample-report.html`](../../../../tests/fixtures/report-regeneration/sample-report.html)
  corpus fixture: a hand-built manifest covering a frozen void element (`#logo-header`),
  two surgical text nodes (`#kpi-revenue`, `#hdr-period`), a regenerate narrative
  (`#exec-summary-narrative`), a regenerate raster (`#chart-region-mix`), and the
  fixture's own deliberately-tricky needs-review case (`#tagline-text`, the
  percent-shaped marketing literal called out in the corpus README) — asserting new
  values present / old values absent at each node, the template file untouched on disk,
  and the whole output still parses.
- **`TestCLI`** — process-boundary tests: happy path (exit 0, output written, template
  SHA-256 unchanged), `--out == --template` rejection, path-traversal rejection, and
  absolute-path rejection (all exit 2).

Run: `python3 plugins/report-regeneration/skills/rebind-html/tests/test_rebind.py -v`

## Purity contract

- **Stdlib-only** — `argparse`, `html.parser`, `json`, `re`, `string`, `pathlib`, `sys`.
  No pip installs required. `jinja2` is imported via a graceful `try/except` and is
  **optional acceleration only** — every `${dotted.path}`-only template (which is what
  this skill's whole test suite exercises) works with jinja2 absent.
- **Runs unmodified on Python 3.9.6** — `from __future__ import annotations`; no PEP 604
  union syntax (`X | Y`), no `match` statement.
- **No network, no subprocess** inside the engine itself.
- **Path-guarded** — see Usage above.
- **Exit-coded** — deterministic `0`/`2`; no partial write on failure.
- **Zero-literal construction, by construction** — every surgical/regenerate mutation is
  a strip call followed by a write call; there is no code path that writes a new value
  without first stripping the old one at that anchor.
