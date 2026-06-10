---
name: svg-report-lint
description: "Lint a standalone SVG file for geometry soundness, legibility, and security before committing to a report or embedding in Power BI/Tableau. Checks viewBox presence and aspect ratio, minimum text font-size, and the security floor: no <script>, no on* handlers, no <foreignObject>, no remote href/use. Gate 103. Complements declarative-visualization (Vega-Lite/JSON spec lint, Gate 101) and pbir-layout-engine (coordinate arithmetic). NOT for Vega-Lite JSON specs (use declarative-visualization) or coordinate layout arithmetic (pbir-layout-engine)."
---

# Skill: svg-report-lint

## What this is

A **stdlib-only, exit-coded SVG linter** for standalone SVG files used in reports,
dashboards, and embedded graphics. It checks for geometry soundness (viewBox,
aspect ratio), legibility (minimum font-size), and the security floor (no script
injection vectors). It is the SVG analog of `pbir-layout-engine` (geometry) and
`declarative-visualization/lint.py` (spec security).

The conceptual canon and surface-delivery map live in
[`../../knowledge/declarative-visualization.md`](../../knowledge/declarative-visualization.md).
Design-first workflow guidance lives in
[`../../knowledge/design-first-report-workflow.md`](../../knowledge/design-first-report-workflow.md).

## Usage

```bash
python3 plugins/ravenclaude-core/skills/svg-report-lint/lint.py <file.svg>
python3 plugins/ravenclaude-core/skills/svg-report-lint/lint.py <file.svg> --min-fontsize 10
python3 plugins/ravenclaude-core/skills/svg-report-lint/lint.py --list-checks
```

Exit 0 = clean. Exit 1 = violation (reject the SVG and fix). Exit 2 = I/O or path error.

## Checks (all → exit 1)

| ID | Check | What it catches |
|---|---|---|
| `viewbox-present` | root `<svg>` has a `viewBox` attribute | SVGs without viewBox scale unpredictably on different screen sizes |
| `viewbox-sane-aspect` | viewBox width/height ratio between 0.05 and 20 | Extreme aspect ratios (e.g. 1000×1) indicate a broken canvas definition |
| `text-min-fontsize` | `<text>` / `<tspan>` font-size ≥ 8px (configurable) | Text below the threshold is illegible at report scale |
| `no-script` | No `<script>` element | Script injection in SVG context |
| `no-inline-handlers` | No `on*` event attributes (`onclick`, `onload`, etc.) | Inline JS execution |
| `no-foreign-object` | No `<foreignObject>` element | HTML injection / XSS-escalation |
| `no-remote-href` | No remote or `javascript:` `href`/`xlink:href` | Network fetch + potential JS execution |
| `no-remote-use` | No `<use>` referencing a remote URL | External SVG inclusion / data exfiltration |

The security checks (`no-script`, `no-inline-handlers`, `no-foreign-object`,
`no-remote-href`, `no-remote-use`) are **default-fail with no `--lenient` option**.
A script-carrying SVG is never acceptable in a committed report.

## Relationship to the viz spine

| Concern | Right tool |
|---|---|
| Vega-Lite / Deneb / Vega spec (JSON) security + quality | `declarative-visualization/lint.py` (Gate 101) |
| Standalone SVG geometry + security | **This skill** (Gate 103) |
| PBIR coordinate layout arithmetic | `pbir-layout-engine/lint.py` (Gate 92) |
| Render→see→critique loop | `visual-feedback-loop/driver.py` (Gate 100) |
| Spec review + design-honesty judgment | `viz-spec-reviewer` agent |

## For SVG-in-DAX (Power BI Image visual)

DAX-constructed SVG strings carry the same injection surface as a file-based SVG.
To lint an SVG-in-DAX badge:
1. Extract the SVG string from the DAX measure (everything after `"data:image/svg+xml;utf8,"`).
2. URL-decode (`%20` → space, `%3C` → `<`, etc.) if the string uses URL encoding.
3. Save to a temporary `.svg` file.
4. Run `lint.py` on that file.

For the complete SVG-in-DAX pattern and DAX string construction approach, see
`plugins/power-platform/knowledge/power-bi-custom-visuals-toolkit.md` §SVG-in-DAX.

## Proven by Gate 103

`scripts/audit-gates.sh` Gate 103 asserts bidirectionally:
- A clean badge SVG passes (exit 0).
- Each violation class exits non-zero individually.
- A mutant linter that hardcodes exit 0 lets known-bad SVGs through (teeth).

## Purity contract

- **Stdlib-only** — `xml.etree.ElementTree`, `re`, `os`, `sys`. No `subprocess`,
  no `urllib`, no `socket`, no `eval`, no `exec`.
- **No network** — the linter parses XML as inert data; it never fetches any URL.
- **Path safety** — rejects `..` in argv, rejects paths outside the repo root.
- **Exit-coded** — deterministic exit 0/1/2; no partial-pass.
