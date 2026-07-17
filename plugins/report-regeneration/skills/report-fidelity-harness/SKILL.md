---
name: report-fidelity-harness
description: "The load-bearing wall of report-regeneration — the 6-leg + period-coherence fidelity verifier. Runs V1 value-accuracy, V2 frozen-complement diff, V3 re-inference isomorphism, V4 taint-egress over the decoded container, V5 render referee, V6 manifest-coverage, plus period-coherence over a regenerated HTML output, and emits a schema-valid fidelity-receipt (PROBE_ERROR != pass; any not_captured => PARTIAL, never a fake PASS). V2/V4/V6/period-coherence are genuinely ML-free. Stdlib-only, Python 3.9-safe, no network. Reach for this to prove a regenerated report leaked no old-client data and changed nothing outside its bound anchors. NOT for report generation or inference (that is the infer/rebind track)."
---

# Skill: report-fidelity-harness

The **load-bearing wall** of `report-regeneration`. No off-the-shelf verifier exists, so the
harness is composed of **six independent legs plus a period-coherence check**, each a runnable
deterministic checker that emits one entry in a `structured-output` **fidelity-receipt**
([`../../knowledge/fidelity-receipt.schema.json`](../../knowledge/fidelity-receipt.schema.json)).
It inherits the W5 discipline verbatim: **`PROBE_ERROR ≠ pass`** (a parse/harness crash never
reads as "fidelity OK"), **any `not_captured` ⇒ overall `PARTIAL`, never `PASS`**, receipts are
TTL'd and environment-fingerprinted, and each leg is labeled **proven** (deterministic) vs
**judged** (behavioral).

Design authority: [`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md)
§5 (the leg matrix), §4 (the node taxonomy), §6 (the security posture). If this skill and the spec
ever disagree, the spec wins.

## The legs

| Leg | Question | ML-free? | Tier |
|---|---|---|---|
| **V1** value accuracy | did value V land at region R? | recompute (2nd path) + anchor **partly**; set-membership + cross-slot **ML-free** | proven, blocking |
| **V2** frozen-complement diff | did anything change outside the bound anchors? | **fully ML-free** | proven, blocking |
| **V3** re-inference isomorphism | is the output's structure the template's? | coarse count cross-check **ML-free**; fine isomorphism inference-adjacent | proven, blocking |
| **V4** taint egress | did any old-client data survive? | **fully ML-free** | proven, **BLOCKING** |
| **V5** render referee | does it render / lay out? | rendering engine ≠ authoring path | judged; `not_captured` when no renderer |
| **V6** manifest coverage | is the *partition itself* correct? | **fully ML-free** | proven, blocking |
| **period-coherence** | does the label match the value's period? | **fully ML-free** | proven, blocking |

- **V1** recomputes each expected value straight from `--new-data` (a genuine second execution
  path, distinct from the binding's inference path), then (a) locates it at the binding's anchor
  and (b) verifies it appears *somewhere* via position-agnostic **set-membership** (catches a
  mis-anchored value as "appears nowhere"), plus a **cross-slot** check (a KPI and the table it
  summarizes must agree).
- **V2** canonically node-diffs the output against the template restricted to everything
  **outside** the `surgical`/`regenerate` anchors → must be empty. Comments are excluded (purged
  pre-emit, spec §6.6); the DOCTYPE and every other node are compared.
- **V3** reads section/table/image/heading/row counts straight from the container (ML-free) and
  compares tag skeletons.
- **V4** scans the **decoded delivered container** — visible text + every attribute value +
  `script`/`style` CDATA + base64/data-URI blobs — against a taint dictionary of the old
  artifact's distinct values + identity strings, normalized to typed value-space so a
  reformat/round/locale survival still matches.
- **V5** returns `not_captured` (never a fake pass) when Playwright/LibreOffice is absent.
- **V6** audits the partition instead of trusting it: a value slot the manifest calls
  `surgical`/`regenerate` that the output presents as `frozen`/unbound while still carrying a
  dataset value is a **coverage failure** (silent staleness); a value-shaped literal in a
  `frozen` region force-demotes to advisory needs-review (the §4 hard rule).
- **period-coherence** asserts every rendered period label and every value/PBI-asset provenance
  period matches the new reporting period.

## Usage

```bash
python3 harness.py \
  --template  ../../../../tests/fixtures/report-regeneration/sample-report.html \
  --output    <regenerated-output.html> \
  --manifest  fixtures/clean-manifest.json \
  --new-data  fixtures/clean-new-data.json \
  --format    json
```

Optional flags:

- `--taint taint.json` — override the taint dictionary (default: derive the old-artifact literals
  from the template's documented `TAINT DICTIONARY` block).
- `--disable-leg V4` (repeatable) — neuter a leg. This is the **must-fail mutant knob**: a
  disabled leg reports `pass` unconditionally, so a test can prove the *enabled* leg has real
  teeth (defect caught with it on, slips with it off).
- `--ttl <seconds>` / `--pretty`.

**Exit codes:** `0` = PASS or PARTIAL (no blocking failure), `1` = FAIL (a blocking leg fired),
`2` = usage / path-guard error. The authoritative verdict is the receipt's `overall_gate`.

The Python API mirrors the CLI: `harness.run_harness(template, output, manifest, new_data,
taint=None, disabled_legs=(), ttl_seconds=3600) -> receipt_dict` (already schema-validated).

## The receipt

`overall_gate` is **PASS** only when every leg verdict is `pass`; **FAIL** if any blocking leg
`fail`s or `PROBE_ERROR`s; **PARTIAL** otherwise (e.g. V5 `not_captured`). A missing Tier-B leg
yields PARTIAL, never PASS. The harness **fail-closes**: it validates its own receipt against the
frozen schema before emitting and refuses to emit an invalid one.

## Tests (TDD against the seeded-defect corpus)

`tests/test_harness.py` is the acceptance suite. It injects each defect from
[`../../scripts/seed_defects.py`](../../scripts/seed_defects.py) (the D1–D14 oracle) and asserts:

1. **Clean control passes** every blocking leg (V5 → `not_captured` → gate PARTIAL, honest).
2. **Each defect is caught by its mapped leg** — D1/D2 → V1, D5 → V3, D6/D12 → V4, D7 → V1
   cross-slot, D8/D14 → period-coherence, D11 → V6 (leg-to-defect attribution, not "something
   fired").
3. **Must-fail halves prove teeth** — for each ML-free leg (V2, V4, V6, period-coherence),
   disabling it lets its defect slip.
4. **Receipts are schema-valid** and the ML-free legs are labeled `inference_independent`.

```bash
python3 tests/test_harness.py          # standalone (no pytest needed)
```

## Constraints honored

Stdlib-only (`html.parser` / `re` / `json` / `base64` / `hashlib` / `difflib`-free node-diff),
runs on Python 3.9.6, `from __future__ import annotations`, no `X|Y`/`match`, no pip installs, no
network, read-only + path-guarded. V4 and V6 are genuinely ML-free; the harness codes to the RSG /
binding-manifest / fidelity-receipt **schemas** so the infer and rebind stages can run in parallel.
