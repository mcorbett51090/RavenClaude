# PBIR / dashboard layout-arithmetic lint

> **Last reviewed:** 2026-06-04. Companion doc for the runnable layout linter at
> [`../skills/pbir-layout-engine/lint.py`](../skills/pbir-layout-engine/lint.py).
> Refresh when the linter's check set, exit-code contract, or the PBIR
> `visualType` enum source changes.

## What this is

`lint.py` is a deterministic, stdlib-only Python linter that checks a dashboard
or report **page** against hard layout arithmetic and — for Power BI PBIR
Enhanced inputs — three PBIR-specific invariants. It is the load-bearing
verification artifact behind the `data-viz-designer` agent: a layout the agent
proposes is not "done" until `lint.py` returns no error-severity findings.

## The seven checks

| Check ID  | Name                        | Applies to | Default severity |
| --------- | --------------------------- | ---------- | ---------------- |
| `check-1` | No-overlap (AABB)           | All stacks | error            |
| `check-2` | Within-canvas               | All stacks | error            |
| `check-3` | Equal-gap (horizontal)      | All stacks | warning          |
| `check-4` | Column-alignment (vertical) | All stacks | warning          |
| `check-5` | No-empty-binding            | PBIR only  | error            |
| `check-6` | Theme-compliance (count)    | PBIR only  | warning          |
| `check-7` | Schema-valid                | PBIR only  | error            |

`check-1`, `check-2`, `check-5`, and `check-7` are **errors** (exit 1 by
default). `check-3`, `check-4`, and `check-6` are **warnings** — they only push
the exit code to 1 when you pass `--strict`.

## How to run it

```bash
# Auto-detect PBIR from $schema; text output.
python3 plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py <page.json>

# Treat warnings as failures (gating a "done" claim on equal-gap/alignment too).
python3 .../lint.py --strict <page.json>

# Force PBIR checks on / off regardless of $schema.
python3 .../lint.py --pbir <page.json>
python3 .../lint.py --no-pbir <page.json>

# Machine-readable envelope (snake_case keys, matches the Finding dataclass).
python3 .../lint.py --format json <page.json>

# Discoverability.
python3 .../lint.py --list-checks
python3 .../lint.py --version
```

### Exit codes

| Code | Meaning                                                                 |
| ---- | ----------------------------------------------------------------------- |
| 0    | All checks pass (or only info-level findings).                          |
| 1    | One or more error-severity findings (or warning-severity with --strict).|
| 2    | I/O error, parse error, or argv path rejection (purity-contract).       |
| 3    | Schema-enum parse failure from `pbir-enhanced-reference.md` § 1.         |

## Suppression

- **Per-page tolerances** — set `_lintConfig.tolerance.equal_gap_px` (default 4)
  and `_lintConfig.tolerance.column_align_px` (default 0) on the page object.
  A per-page value wins over the `--tolerance-gap` / `--tolerance-align` flags.
  A hand-tuned grid that intentionally varies a column's x can raise
  `column_align_px` to suppress `check-4`.
- **Per-visual ignore** — set `_lintIgnore: ["check-3", ...]` on a visual to omit
  that visual from the listed checks.

## The one sanctioned cross-plugin read

`check-7` validates each visual's `visualType` against the canonical enum that
lives in
[`../../power-platform/knowledge/pbir-enhanced-reference.md`](../../power-platform/knowledge/pbir-enhanced-reference.md)
§ 1. The linter parses that section at runtime rather than duplicating the enum
— so the two cannot silently drift (an audit gate watches that drift; the linter
is its runtime consumer). This is the **only** cross-plugin filesystem
dependency in `lint.py`; it is documented in the module's purity-contract
docstring. If the reference file is unreadable or § 1 is unparseable, the linter
exits 3. The page-level `displayOption` enum (`FitToPage` / `FitToWidth` /
`ActualSize`) is a pinned constant in `lint.py`.

## Fixtures + the audit gate

The bidirectional fixture corpus lives under
[`../../../tests/fixtures/data-viz/`](../../../tests/fixtures/data-viz/): one
`good-page.json` that passes all seven checks, one `bad-page-*` per check that
fails exactly its target check, and a `hand-tuned-vertical-grid-passes.json`
that exercises the `_lintConfig` suppression mechanic. `scripts/audit-gates.sh`
Gate 92 proves the linter fails on a bad fixture and passes on the good one.
