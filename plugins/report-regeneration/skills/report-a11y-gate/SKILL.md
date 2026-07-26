---
name: report-a11y-gate
description: "report-regeneration a11y gate: a11y_lint.py is a stdlib, machine-checkable WCAG-subset linter over an output HTML deliverable (the Tier-A a11y FLOOR, not axe-core/veraPDF -- that is the later Tier-B upgrade). BLOCKING rules: img-alt (non-decorative <img> with no alt), html-lang, link-name, button-name, control-label, table-headers. ADVISORY -> manual residue: th-scope, heading-order. Catches seeded defect D3 (missing alt-text) as a crisp img-alt BLOCK. Emits a sub-receipt folded into report-qa-gate (blocking a11y violation -> assembled verdict FAILs; manual residue -> reviewer checklist). HONEST about the ~30-50% machine-checkable floor: the rest is manual residue, never claimed passed. Stdlib-only, exit-coded, path-guarded, no network/subprocess."
---

# Skill: report-a11y-gate

## What this is

A **stdlib-only, exit-coded CLI** -- [`a11y_lint.py`](a11y_lint.py) -- that lints an output HTML
deliverable against the **machine-checkable subset of WCAG** and emits an a11y sub-receipt. It is
the report-regeneration a11y **floor**: the ~30-50% of WCAG a structural linter can decide with no
human judgment. Everything else is emitted as `manual_residue`, never claimed as passed.

Read first, before touching the code:
[`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md) §1 (the
honest guarantee) and the FORGE plan §7 (accessibility): *"automated tooling covers only the
machine-checkable ~30-50% of WCAG ... the gate is a floor, not conformance ... an empty manual-
residue section is itself a defect (over-claim)."*

**This is the stdlib floor, deliberately not axe-core/veraPDF.** The plan scopes Playwright + axe
+ veraPDF (and rendered-CSS contrast ratios) as a **later Tier-B upgrade** (§8). This gate runs in
Tier-A -- no browser, no network, no subprocess -- so a11y regressions are caught on every PR; the
browser gate is a strict superset added later.

## The honest guarantee, restated for this skill

Per [`../../CLAUDE.md`](../../CLAUDE.md) §1, the plugin never claims a report is "accessible"
beyond what the checked surfaces prove. A `PASS` here means "no **machine-decidable** WCAG-floor
violation was found," **not** "this report is accessible." That is why the sub-receipt's
`manual_residue` is **never empty** -- the ~30-50% floor note ships on every run, PASS included.

## What it checks

| Rule | WCAG | Tier | Fires when |
|---|---|---|---|
| `img-alt` | 1.1.1 | **BLOCKING** | a non-decorative `<img>` has no `alt` and no accessible-name fallback (role=presentation/none, aria-hidden, aria-label/-labelledby, title). **Catches D3.** |
| `html-lang` | 3.1.1 | **BLOCKING** | the root `<html>` has no non-empty `lang`. |
| `link-name` | 2.4.4 | **BLOCKING** | an `<a href>` has no accessible name (no text, aria-label/-labelledby, title, or child `<img alt>`). |
| `button-name` | 4.1.2 | **BLOCKING** | a `<button>` / `input[type in button,submit,reset,image]` has no accessible name. |
| `control-label` | 1.3.1 | **BLOCKING** | a form control (`<input>` not hidden/button-like, `<select>`, `<textarea>`) has no `<label for>`, wrapping `<label>`, aria-label/-labelledby, or title. |
| `table-headers` | 1.3.1 | **BLOCKING** | a `<table>` has `<td>` data cells but **zero** `<th>` header cells. |
| `th-scope` | 1.3.1 | advisory | a `<th>` in a data table lacks both `scope` and `headers` (simple tables can be fine -- flagged for human confirmation, not failed). |
| `heading-order` | 1.3.1 | advisory | a heading skips a level going deeper (h2 -> h4), or the first heading is not `<h1>`. |

An `<img>` with an explicit `alt=""` is treated as **intentionally decorative** and passes
`img-alt` (matching axe-core's `image-alt` logic) -- only a *missing* `alt` on a non-decorative
image fails.

The gate is **FAIL iff at least one BLOCKING violation** is found; otherwise **PASS** with a
non-empty manual-residue checklist. Advisory findings never fail the gate -- they fold into the
manual residue for human confirmation.

## The sub-receipt

`lint_html(html_text) -> dict` (and the CLI's `--format json`) returns:

```jsonc
{
  "schema": "report-regeneration/a11y-gate@1",
  "gate_version": "1.0.0",
  "gate": "PASS" | "FAIL",
  "coverage": "machine-checkable WCAG floor only (~30-50% ...)",
  "counts": {"blocking": N, "advisory": M, "images": I, "tables": T},
  "violations": [{"rule","wcag","impact","blocking","node","detail"}, ...],
  "manual_residue": ["<the ~30-50% floor items + each advisory violation>", ...]
}
```

This is consumed by [`../report-qa-gate/qa_gate.py`](../report-qa-gate/qa_gate.py): a blocking
a11y violation folds the assembled verdict to **FAIL**; the `manual_residue` folds into the human
reviewer checklist under category `a11y-manual-residue` (blocking violations also appear under
`a11y-blocking`).

## CLI contract

```text
python3 plugins/report-regeneration/skills/report-a11y-gate/a11y_lint.py --html <PATH> [--format text|json] [--pretty]
python3 plugins/report-regeneration/skills/report-a11y-gate/a11y_lint.py --version
```

| Exit code | Meaning |
|---|---|
| `0` | `gate == PASS` (no blocking violation; manual residue still emitted) |
| `1` | `gate == FAIL` (>= 1 blocking violation) |
| `2` | usage / path-guard / I/O error |

`--html` must resolve to a real regular file; NUL bytes and `..` traversal are rejected.

## Dependency / purity contract

Stdlib only (`argparse`, `html.parser`, `json`, `sys`, `pathlib`). No network, no subprocess, no
third-party imports (no axe-core / Playwright -- that is the Tier-B upgrade). Python 3.9.6: no
`X | Y` unions, no `match`; `from __future__ import annotations`.

## Tests

[`tests/test_a11y_lint.py`](tests/test_a11y_lint.py) -- 34 unittest cases: the clean corpus
(`sample-report.html`) passes; the seeded **D3** injector (missing alt-text) is a crisp `img-alt`
BLOCK attributed to `img#chart-region-mix`; every blocking rule has a bidirectional bad/good pair;
`th-scope` + `heading-order` are advisory (non-blocking); the manual residue is never empty; and
the CLI exit codes 0/1/2 + `--version` are exercised via subprocess.

```bash
python3 plugins/report-regeneration/skills/report-a11y-gate/tests/test_a11y_lint.py -v
```

## Scope boundary

This gate lints an **existing** HTML output for the machine-checkable WCAG floor. It does not
render, does not run a browser, does not check contrast RATIOS (which need rendered CSS -- the
Tier-B axe/veraPDF upgrade), and never claims conformance. It is the a11y arm of the QA gate; the
six fidelity legs live in `report-fidelity-harness`, and prompt-injection defense lives in
`report-injection-guard`.
