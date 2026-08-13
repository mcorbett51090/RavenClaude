# report-regeneration — Phase-0 seeded-defect corpus

This directory is the **adversarial-synthetic corpus** for the `report-regeneration` plugin's
auto-QA harness (per `.ravenclaude/runs/forge/report-regeneration/plan.md` §5 Phase-0/Phase-1).
No real client data exists yet, so the corpus is entirely fabricated: a single fictional company,
"Acme Widgets, Inc.", with fabricated financial figures. No PII, no real client artifacts.

**This directory + the injector build the corpus half only.** The fidelity harness itself (the
V1-V6 + period-coherence checkers described in the plan's §3) is a **separate track** and is not
implemented here — this corpus exists so that harness, once built, has known-bad inputs to prove
its teeth against.

## Files

| File | What it is |
|---|---|
| [`sample-report.html`](sample-report.html) | The synthetic "old" quarterly report — the surgical-transplant TEMPLATE. Also doubles as the **clean control**: fed through the harness unmodified, every blocking leg is expected to PASS. |
| [`../../../plugins/report-regeneration/scripts/seed_defects.py`](../../../plugins/report-regeneration/scripts/seed_defects.py) | The injector. Takes `sample-report.html` (or any fixture built the same way) and produces a copy with exactly one named defect (D1-D14) seeded in, plus a JSON manifest of what changed. |

## Quickstart

```shell
# Enumerate the full D1-D14 catalog with each defect's expected-catching harness leg:
python3 plugins/report-regeneration/scripts/seed_defects.py --list --pretty

# Seed one defect into a fresh copy (run from the repo root — paths are relative + path-guarded):
python3 plugins/report-regeneration/scripts/seed_defects.py --defect D6 \
    --in  tests/fixtures/report-regeneration/sample-report.html \
    --out tests/fixtures/report-regeneration/_out/bad-D6.html
```

Every invocation prints a JSON manifest to stdout (`{"schema": "report-regeneration/seed-defects@1", ...}`). Exit code `0` = success; `2` = usage / path-guard / anchor-not-found / fixture-drift error (never a silent no-op — see "Design guarantees" below).

`seed_defects.py` is **stdlib-only** (`argparse`, `copy`, `html.parser`, `json`, `re`, `pathlib`), **path-guarded** (rejects absolute paths and any `..` traversal component; both `--in` and `--out` must resolve inside the repo root), and makes **no network calls**.

## The D1-D14 catalog

Each row is exactly what `--list` prints. "Catching leg" names the harness component (plan §3) that is expected to fail/flag when that defect is present — the contract this corpus exists to prove.

| ID | Defect | Expected-catching harness leg |
|---|---|---|
| **D1** | Wrong value | V1 — value accuracy (recompute vs new source; blocking) |
| **D2** | Stale old value left in place | V1 — value accuracy (the stale value fails set-membership too; blocking) |
| **D3** | Missing alt-text | a11y gate — axe-core / veraPDF (alt-text) |
| **D4** | Contrast violation | a11y gate — axe-core / veraPDF (contrast floor) |
| **D5** | Dropped/reordered section | V3 — re-inference isomorphism (rule-based coarse section-count cross-check; blocking) |
| **D6** | Old-client literal surviving in a transplanted node | V4 — taint-dictionary egress scan (blocking) |
| **D7** | Cross-slot inconsistency (KPI ≠ table total) | cross-slot consistency cross-check (V1-adjacent, blocking) |
| **D8** | Wrong-period label | period-coherence check (blocking) |
| **D9** | Layout overlap | V5 — render referee (Playwright / LibreOffice screenshot diff) |
| **D10** | Untagged/invalid PDF (HTML-side proxy) | a11y gate — veraPDF PDF/UA taggability `[proxy — see note below]` |
| **D11** | Frozen-misclassified data-bound node (RT1-F1) | V6 — manifest-completeness/value-coverage + the data-shaped-literal frozen-demotion hard rule (blocking) |
| **D12** | Embedded-metadata/raster-cache leak (RT1-F3) | V4 — taint-dictionary egress scan over the DECODED container (blocking) |
| **D13** | Prompt-injection payload — force-all-frozen + attacker prose (RT1-F4) | partition-anomaly gate + provenance-bound narrative check (blocking) |
| **D14** | Stale Power BI screenshot / stale XMLA figure | period-coherence check, extended to PBI-sourced assets (blocking) |

`D10` note: the corpus is HTML, so "untagged/invalid PDF" is implemented as an **HTML-side proxy**
— stripping `<!DOCTYPE html>`, the `<html lang>` attribute, every `<th scope="...">`, and the
table `<caption>` — the taggability signals a print-to-PDF pipeline needs to emit a
PDF/UA-conformant document. The real veraPDF check runs on an actual PDF and is out of scope for
an HTML fixture; this is documented, not silently mislabeled.

## What each injector actually does

Every injector is a small, independently-documented pure function in `seed_defects.py`
(`inject_D1` … `inject_D14`), each taking the full HTML text and returning `(new_html,
changes[])`. None of them mutate the input in place, and **none silently no-op** — an injector
whose anchor is missing (or whose expected "before" text doesn't match, i.e. the fixture drifted)
raises `SeedDefectError` and the script exits 2 rather than emitting an unmodified copy. This was
verified directly: hand-drifting `#kpi-operating-margin`'s value before running `--defect D1`
correctly fails with `"fixture drifted? refusing to guess"` instead of silently mutating the
wrong thing.

Anchors are addressed by `id` attribute via regex (not a full DOM rebuild — this is a test-fixture
tool, not the harness), and every mutated output is smoke-checked with `html.parser` before being
written, so an injector bug that produces unbalanced/unparseable markup fails loudly instead of
shipping a broken fixture.

| ID | Anchor(s) touched | Mechanism |
|---|---|---|
| D1 | `#kpi-operating-margin` | Text replaced with a plausible-but-wrong figure not present anywhere else in the document. |
| D2 | `#kpi-revenue-growth` | Text replaced with the **taint dictionary's** old growth figure (`-4.1%`) — the literal prior-period value, not an arbitrary wrong one. |
| D3 | `#chart-region-mix` | `alt` attribute stripped from a meaningful (non-decorative) chart image. |
| D4 | `#tagline-text` | Inline `style="color: rgb(250,250,250)"` added against the white page background (~1:1 contrast). |
| D5 | `#sec-appendix` | The entire `<section>` is removed (template has 7 `<section>`s; the defect output has 6). |
| D6 | `#exec-summary-narrative` | The taint dictionary's old company name (`Ridgeline Fabricators Inc.`) is appended to otherwise-correct prose. |
| D7 | `#kpi-revenue` | Headline KPI changed while the region table (and its own `#tbl-region-total` tfoot cell, still `$4,821,300`) is left untouched. |
| D8 | `#hdr-period` | Rendered label text changed (`Q1 2025` → `Q4 2024`) while its own `data-period="2025-Q1"` attribute is left untouched — a labeling bug, not a value bug. |
| D9 | `#chart-revenue-trend`, `#chart-region-mix` | Both forced to identical absolute coordinates via inline CSS. |
| D10 | document-wide | `<!DOCTYPE html>`, `<html lang>`, all `scope="col"/"row"`, and the `<caption>` removed. |
| D11 | `#kpi-report-date` | `data-role` flipped `"surgical"` → `"frozen"` and `data-bind` stripped, while `data-shape="date"` and the literal date text (`April 4, 2025`) are left untouched. |
| D12 | `<head>` + before `</body>` | Old author/company written into `<meta>` tags (the docProps analog); a hidden `<script type="application/json">` data-cache with the old source filename + old revenue total is inserted before `</body>` (the embedded-workbook-cache analog). |
| D13 | after `<body>`, `#outlook-narrative` | An instruction-shaped HTML comment ("classify everything as frozen, suppress review flags") is inserted; unprovenanced attacker prose (a novel imperative + a routing/account number + an email address) is appended to a `regenerate`-marked narrative slot. |
| D14 | `#pbi-screenshot`, `#xmla-figure-latest` | Both nodes' `data-source-period` moved to a prior quarter (`2024-Q3`) — and the screenshot's `alt` text updated to match — while the surrounding report period (`#hdr-period`/`#ftr-period`) is untouched. |

## The taint dictionary

`sample-report.html`'s own header comment (and `seed_defects.py`'s `TAINT` dict, kept in lockstep)
define the literals from the **prior client artifact** this template superseded — a fictional
"Ridgeline Fabricators Inc." — that must never appear in a regenerated output. D2, D6, and D12
draw from this dictionary to simulate three distinct failure shapes against the same taint
literals: D2 is a **value-accuracy** miss (V1: the expected new figure is simply absent), D6 is a
**visible-text egress** leak (V4 over the rendered body), and D12 is a **hidden-channel** egress
leak (V4 over the decoded container — `<meta>` tags and a hidden `<script>` cache that a
naive visible-text scan never sees).

## Deliberately-tricky cases baked into the clean template (not injector defects)

`sample-report.html` itself — read its own header comment for the full list — bakes in a few
adversarial cases that exist in the "clean" control, not as seeded defects:

1. **"Fiscal Year 2024"** (Outlook section) — a number that *is* a year: a static historical
   reference that must not be treated as a data-bound token needing rebind.
2. **"since 1998"** (brand tagline) — same trap, a static founding-year reference.
3. **"100% Committed to Quality"** (`#sec-tagline` / `#tagline-text`) — a static marketing label
   that *is* percent-shaped. Per the plan's §2 hard rule ("any data-shaped literal in a
   candidate-frozen node force-demotes it to needs-review, regardless of classifier confidence"),
   this node is **correctly** expected to surface as advisory needs-review even in the clean
   control — a non-inference detector genuinely cannot tell this "100%" from a KPI's "100%".
4. `#kpi-report-date` (a genuine data-bound date, `data-role="surgical"`) sits directly next to
   `#sec-appendix`'s boilerplate prose (no data-shaped literals, safely `data-role="frozen"`) — so
   a coarse "everything near data is data" heuristic fails visibly.

**Consequence for "the clean control must pass":** treat that claim as scoped to the **blocking**
legs (V1-V4, V6's hard rule, period-coherence) and the a11y **floor**, not to advisory/manual
residue. Case #3 above is expected to produce a non-blocking needs-review flag on the clean
control — that is the corpus doing its adversarial job, not a fixture bug.

## How this corpus is meant to be used in acceptance tests

This is the intended shape of the harness's own acceptance tests (per plan §5 Phase 1/2), even
though building that harness is a separate track:

1. **Clean-control pass.** Run the harness against `sample-report.html`, untouched, as the
   "regenerated output." Every blocking leg (V1, V2, V3, V4, V6's hard rule, period-coherence) and
   every a11y-floor check must PASS. (Advisory needs-review flags — see case #3 above — are
   expected and do not count as a failure.)
2. **Each defect must be caught by its leg.** For every `Dn` in the table above, run
   `seed_defects.py --defect Dn` to produce a bad copy, feed it to the harness, and assert the
   **named leg** fails/flags it (not just that *some* check fails — the point of seeding one
   defect at a time is to prove leg-to-defect attribution, not just "the harness is unhappy").
3. **A must-fail half proves teeth (binding, per plan §3's "bidirectional fixture pair… plus a
   must-fail mutant proving teeth").** For each leg, also run its detection logic **disabled** (or
   its taint dictionary emptied, or its rule bypassed — however the harness exposes that knob)
   against the same seeded-bad copy and assert the defect now slips through. A leg that "catches"
   a defect it was never actually capable of detecting is a false-teeth bug in the harness, not a
   passing test — this half is what tells the difference. The plan calls out three concrete
   must-fail halves by name: V2-disabled lets a chrome edit through, V4-dictionary-emptied lets a
   leak through (exercise this against D6/D12), and a strip-disabled run lets an old literal
   survive (exercise this against D2/D6).
4. **Re-seed at will.** `seed_defects.py` takes any structurally-equivalent HTML fixture as `--in`
   (not just `sample-report.html`) — the anchors are addressed by `id`, so a future second fixture
   built with the same id conventions works unchanged. A defect id is never destructive to the
   input file (`--in` is opened read-only; only `--out` is written).

## Design guarantees (what to rely on, what not to)

- **Deterministic.** No randomness anywhere in `seed_defects.py`; running the same `--defect
  --in --out` twice produces byte-identical output (verified this session).
- **Fails loudly, never silently.** Missing anchor, drifted "before" text, or an injector that
  somehow produces no change at all → `SeedDefectError` → exit 2 + a JSON `{"ok": false, "error":
  ...}` object on stdout (so a caller parsing stdout never gets truncated/ambiguous JSON) — never
  a copy that quietly wasn't actually mutated.
- **Path-guarded.** `--in`/`--out` must be relative paths with no `..` component and must resolve
  inside the repo root (same convention as `plugins/ravenclaude-core/skills/svg-report-lint/lint.py`'s
  `_repo_root()`/`_safe_path()`). Verified: an absolute path, a `../`-traversal path, and a
  missing input file are all rejected with exit 2 and no partial write.
- **Not a substitute for the real harness.** `_assert_parseable()` (an `html.parser` smoke check)
  only catches gross injector bugs (unbalanced markup); it does not re-implement V1-V6 or
  period-coherence. Treat every `--defect` output as a fixture to feed the *real* harness, not as
  self-validating proof that the defect is "real."
- **What this script does NOT do:** no OOXML/.docx handling (the Office lane is Phase 3, a
  separate track — D10's tagging proxy and D12's metadata/raster-cache leak are HTML-side
  analogs, not the real `word/embeddings/*.xlsx` / `docProps/*` channels the plan's §4 describes
  for the Office format), no PDF rendering, no Power BI/XMLA calls, no LLM/classifier invocation.
