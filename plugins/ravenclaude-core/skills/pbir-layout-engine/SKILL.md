---
name: pbir-layout-engine
description: "Deterministic layout-arithmetic linter for dashboard/report page definitions. Runs seven checks — no-overlap (AABB), within-canvas, equal-gap, column-alignment, and three PBIR-specific invariants (no-empty-binding, bounded theme-override count, visualType/displayOption schema validity) — against a page JSON, a page directory, or a fixture set. Stdlib-only, no network, exit-coded for CI. The load-bearing technical core under the data-viz-designer agent; usable standalone to lint a Power BI PBIR page layout."
---

# Skill: pbir-layout-engine

## What this is

A **runnable, deterministic linter** — [`lint.py`](lint.py) — that checks a dashboard/report page's visuals against hard **layout arithmetic** plus, for Power BI **PBIR Enhanced** inputs, three PBIR-specific invariants. It is the load-bearing, testable core beneath the `data-viz-designer` agent (Phase 1 of [`docs/research/2026-06-02-data-viz-agent/build-plan.md`](../../../../docs/research/2026-06-02-data-viz-agent/build-plan.md)), and it stands alone: a Power BI author can lint a page's layout without invoking the agent.

It is **not** a style opinion engine — it checks arithmetic facts (do boxes overlap? do they fit the canvas? are gaps equal? are columns aligned?) and schema facts (is the `visualType` in the canon enum?), each with a precise `fix_hint`.

## The seven checks

| Check | Name | Applies to | Default severity |
|---|---|---|---|
| `check-1` | No-overlap (AABB bounding-box) | all stacks | error |
| `check-2` | Within-canvas | all stacks | error |
| `check-3` | Equal-gap (horizontal) | all stacks | warning |
| `check-4` | Column-alignment (vertical) | all stacks | warning |
| `check-5` | No-empty-binding (`queryState` projections present) | PBIR only | error |
| `check-6` | Theme-compliance (bounded override count) | PBIR only | warning |
| `check-7` | Schema-valid (`visualType` / `displayOption` enums) | PBIR only | error |

PBIR checks (5–7) auto-enable when the input carries a `$schema`; force with `--pbir` / disable with `--no-pbir`.

## CLI contract

```text
python3 plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py [OPTIONS] <input-path>
```

`<input-path>` is a single page JSON, a page directory, or a fixture directory. It **MUST NOT** contain `..` and **MUST** resolve inside the repo root (else exit 2 — the purity-contract failure).

| Option | Effect |
|---|---|
| `--pbir` / `--no-pbir` | force PBIR checks on/off (default: auto-detect from `$schema`) |
| `--format text\|json` | output format (default `text`); the JSON envelope is `{schema_version, linter_version, input_path, exit_code, summary, findings[]}` |
| `--strict` | exit non-zero on any finding ≥ `warning` (default: only `error` findings set a non-zero exit) |
| `--tolerance-gap=PX` / `--tolerance-align=PX` | override check-3/4 tolerances (a per-page `_lintConfig` wins) |
| `--list-checks` / `--version` | print the checks / pinned schema version and exit |

**Exit codes:** `0` pass (or only info-level) · `1` error finding (or warning under `--strict`) · `2` I/O, parse, or path-rejection (purity failure) · `3` `visualType` enum could not be parsed from the canon file (see below).

## Suppression — `_lintConfig` and `_lintIgnore`

A page may carry a `_lintConfig.tolerance` block (`equal_gap_px`, `column_align_px`) to widen check-3/4 for a deliberately hand-tuned grid; a visual may carry `_lintIgnore: ["check-3"]` to opt out of a specific check. The `hand-tuned-vertical-grid-passes` fixture exercises this path.

## The one sanctioned cross-plugin read

`check-7` validates `visualType` against the canon enum in [`plugins/power-platform/knowledge/pbir-enhanced-reference.md`](../../../power-platform/knowledge/pbir-enhanced-reference.md) § 1 — parsed **at runtime**, never duplicated here, so the enum and the linter cannot silently drift. This is the linter's **only** cross-plugin filesystem dependency (documented in the module docstring). If § 1 can't be located or parsed, `check-7` cannot run and the process exits `3` rather than passing silently.

## Output Contract

The linter's machine output is the `--format json` envelope above (snake_case keys, `null` over key-omission, `exit_code` mirroring the process exit). When a reviewer critiques a linter integration in a PR, the response ends with the cross-plugin Structured Output JSON block per [`structured-output/SKILL.md`](../structured-output/SKILL.md).

## Proven by Gate 92

[`scripts/audit-gates.sh`](../../../../scripts/audit-gates.sh) Gate 92 + the 12 fixtures under [`tests/fixtures/data-viz/`](../../../../tests/fixtures/data-viz/) are the bidirectional floor: each `bad-page-*` fixture fires **exactly** its targeted check (non-zero exit), and `good-page` + `hand-tuned-vertical-grid-passes` exit `0`. Checks 3/4/6 are `warning` severity, so their bad fixtures are asserted under `--strict`. Companion reference: [`knowledge/pbir-design-lint.md`](../../knowledge/pbir-design-lint.md).

## Scope boundary

This skill is the **linter only**. The chart-selection / WCAG-contrast / IBCS-variance skills, the `data-viz-designer` agent that orchestrates them, and the visual-design knowledge files are separate deliverables of the same build plan (Phases 3–6) and ship independently.
