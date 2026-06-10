---
name: declarative-visualization
description: "Author a Vega-Lite / Deneb / SVG spec for a stated intent on any surface (web vega-embed, react-vega, Evidence, Observable, Power BI Deneb, Tableau extension/SVG, SVG-in-DAX). Six-step method: pick grammar → bind data → encode → wire interactivity → test null/empty → verify via render loop. Ships a surface-agnostic spec-patterns library. Mandatory security audit (no data.url, no remote loader, no SVG script) enforced by lint.py (Gate 101). Complements the visual-feedback-loop (render referee) and pbir-layout-engine (coordinate linter). NOT for coordinate/layout arithmetic (pbir-layout-engine) or render-loop orchestration (visual-feedback-loop)."
---

# Skill: declarative-visualization

## What this is

A **method + runnable linter** for authoring Vega-Lite, Vega, Deneb, and SVG specs
on any surface — web, Power BI, Tableau, or standalone SVG. It is the spec-authoring
layer beneath every visualization agent; usable standalone to build and validate a
chart spec without invoking an agent.

The conceptual canon (when to use which grammar, the surface→delivery map, the full
security model) lives in
[`../../knowledge/declarative-visualization.md`](../../knowledge/declarative-visualization.md).
This SKILL is the operating reference for the method and the runnable linter.

## The six-step method

1. **Pick the grammar.** Vega-Lite first (concise, portable). Escalate to full Vega
   only when a required mark or transform is absent. Use Deneb only for Power BI;
   SVG only for non-chart visuals or SVG-in-DAX.

2. **Bind data per surface.** Always use `data.name` + dummy `values` for local
   testing. Never use `data.url` in committed specs (security rule). Wire the real
   data source in the host app (JS `view.change()`, Deneb field mapping, etc.) after
   the spec passes the linter and the render check.

3. **Encode.** Map fields to channels (`x`, `y`, `color`, `size`, `opacity`,
   `tooltip`). For small-multiples: use `facet`. For overlays: use `layer`. The
   spec-patterns library ([`spec-patterns/`](spec-patterns/)) provides starter
   templates for the most common chart types.

4. **Wire interactivity** (where needed). For web: Vega-Lite `params` / `select`.
   For Deneb/Power BI: the `powerbi` cross-filter expression. For Tableau: the
   Extension API datasource hook.

5. **Test null / empty data.** Replace `data.values` with `[]` and confirm the
   chart degrades cleanly (empty state message, not a blank visual).

6. **Verify via the render loop.** Run
   [`../visual-feedback-loop/driver.py`](../visual-feedback-loop/SKILL.md) for a
   pass/fail verdict. For Power BI PBIR: also run
   [`../pbir-layout-engine/lint.py`](../pbir-layout-engine/SKILL.md) for coordinate
   facts. The render loop is the schema check — a spec that renders without error is
   schema-valid; a spec that does not render is not.

## Mandatory security audit

Before committing any spec or template, run the linter:

```
python3 plugins/ravenclaude-core/skills/declarative-visualization/lint.py <spec.json>
```

Exit 0 = clean. Exit 1 = security violation (reject the spec and fix the offending
key). Exit 2 = I/O or path error.

**The four forbidden patterns (exit 1):**

| Pattern | Why forbidden |
|---|---|
| `data.url` (string value) | Spec fetches from a remote URL at render — SSRF vector |
| `transform.lookup` with a `from.data` that has a `url` key | Same as above, via transform |
| `loader` key anywhere in the spec (custom loader override) | Redirects all relative URL resolution |
| SVG `<script>` element or `on*` attribute | Script injection |

Any PR adding or modifying a file under `spec-patterns/` routes through
`ravenclaude-core/security-reviewer` (invariant — this is load-bearing, not a
suggestion).

## Spec-patterns library

The templates under [`spec-patterns/`](spec-patterns/) are the six most common
surface-agnostic chart types. Each:

- Uses `data: {"name": "source"}` + a `values` dummy for local test.
- Is valid JSON (passes `python3 -m json.tool`).
- Passes `lint.py` with exit 0.
- Includes a `description` field stating its intent.

| Template | File | Chart type |
|---|---|---|
| Diverging bar | `diverging-bar.json` | Positive/negative bars around a zero axis |
| Dumbbell | `dumbbell.json` | Start–end comparison per category |
| Small-multiples facet | `small-multiples-facet.json` | Faceted grid of line/bar charts |
| Heatmap | `heatmap.json` | x×y grid colored by value |
| Sparkline strip | `sparkline-strip.json` | Row-per-series compact line mini-charts |
| Annotated line | `annotated-line.json` | Line + text mark at notable points |

## Proven by Gate 101

[`scripts/audit-gates.sh`](../../../../scripts/audit-gates.sh) Gate 101 + the
fixtures under
[`tests/fixtures/declarative-viz/`](../../../../tests/fixtures/declarative-viz/)
are the bidirectional floor: a mutant template with `data.url` must fail (exit 1),
and the clean templates must pass (exit 0). Both halves are asserted.

## Output contract

When authoring a spec for a user, emit:

1. The spec JSON (in a fenced ` ```json ` block).
2. The `lint.py` verdict (`exit 0` or the violation that was fixed).
3. The render loop result if a browser tool was available.
4. The null/empty state confirmation.

Use the Structured Output Protocol block per
[`../structured-output/SKILL.md`](../structured-output/SKILL.md) when handing off
to another agent.
