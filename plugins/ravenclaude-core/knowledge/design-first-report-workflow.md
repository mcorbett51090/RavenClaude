# Design-First Report Workflow

**Scope:** The end-to-end workflow for producing pixel-perfect reports using the
declarative-visualization canon. Covers spec authoring → linting → security review →
delivery surface integration. Applicable to any agent that builds charts or report
images: `power-bi-engineer`, `frontend-coder`, `viz-spec-reviewer`, and the Team Lead.

Related:
- Linter: [`../skills/declarative-visualization/lint.py`](../skills/declarative-visualization/SKILL.md) (Gate 101)
- SVG linter: [`../skills/svg-report-lint/lint.py`](../skills/svg-report-lint/SKILL.md) (Gate 103)
- Reviewer: [`../agents/viz-spec-reviewer.md`](../agents/viz-spec-reviewer.md)
- Grammar reference: [`declarative-visualization.md`](declarative-visualization.md)
- Visual feedback loop: [`visual-feedback-loop.md`](visual-feedback-loop.md)

---

## The Workflow

```
design → spec → lint (Gate 101 / 103) → review → deliver → verify
```

Each stage has a hard gate. A stage cannot advance past its gate with an unresolved
BLOCKER.

---

## Stage 1 — Design First

**Before writing a single line of JSON or SVG, answer these four questions:**

1. **What question does this chart answer?** One sentence. If you can't state it, the
   chart isn't ready to spec.
2. **What is the delivery surface?** Web (vega-embed), Power BI (Deneb), standalone
   SVG (SVG-in-DAX), Tableau extension? The surface determines the grammar and the
   security constraints.
3. **What data shape does the host provide?** Named dataset? Inline values? Power BI
   cross-filter context? The data binding determines whether `data.name` or
   `data.values` is the correct form.
4. **What are the accessibility requirements?** Color-blind-safe palette? Redundant
   encoding (shape + color)? Minimum font sizes?

**Output:** a one-paragraph design brief. No code yet.

---

## Stage 2 — Spec from a Verified Template

Use the spec-patterns library in
[`../skills/declarative-visualization/spec-patterns/`](../skills/declarative-visualization/spec-patterns/)
as the starting point. All templates:
- Use `data.name` (never `data.url`) so they pass the security linter by default.
- Declare `$schema` pointing to the canonical Vega-Lite CDN URL.
- Include the minimum required encoding channels for their mark type.

If no template fits, author from scratch following the grammar essentials in
[`declarative-visualization.md`](declarative-visualization.md) §2.

---

## Stage 3 — Lint (Gate 101 / Gate 103)

**JSON spec:**
```bash
python3 plugins/ravenclaude-core/skills/declarative-visualization/lint.py <spec.json>
# exit 0 = clean; exit 1 = violation; exit 2 = I/O error
```

**SVG image:**
```bash
python3 plugins/ravenclaude-core/skills/svg-report-lint/lint.py <image.svg>
# exit 0 = clean; exit 1 = violation; exit 2 = I/O error
```

**Hard rule:** A spec or SVG that exits 1 from the linter **must not advance to Stage 4.**
Fix the violation first. The linter is the purity contract — never use `--strict=false`
or bypass flags to make a spec pass.

For Vega specs with signals/expressions, also run with `--strict`:
```bash
python3 plugins/ravenclaude-core/skills/declarative-visualization/lint.py --strict <spec.json>
```
A `--strict` failure means the spec carries expression-class constructs that require a
manual security review (Stage 4 is mandatory, not optional).

---

## Stage 4 — Security Review (viz-spec-reviewer)

**When Stage 4 is mandatory:**
- Any Vega spec that uses `signal`, `expr`, or `calculate` transforms.
- Any SVG embedded in a DAX string or a web page.
- Any spec that will be deployed to a shared / multi-tenant surface.
- Any linter warning (exit 0 with warnings) that involves the security-surface checks.

**When Stage 4 is advisory:**
- A Vega-Lite spec with no signals, no expressions, using only `data.name` or
  `data.values`, passing all linter checks cleanly — a review is good practice but
  not blocking.

**Dispatch the `viz-spec-reviewer` agent:**
> "Review this [Vega-Lite/Vega/SVG] spec — [describe the delivery surface and any
> linter flags]."

The reviewer's output is a structured verdict (`LGTM`, `NEEDS-CHANGES`, or `DENY`).
A `DENY` blocks delivery until all BLOCKERs are resolved.

---

## Stage 5 — Delivery Surface Integration

| Surface | Integration path | Key constraint |
|---|---|---|
| **Vega-Lite / web** | `vega-embed` or `react-vega` | `data.name` for all dynamic data; no remote loaders |
| **Power BI (Deneb)** | Paste spec into Deneb visual → bind fields | Use `"data": {"name": "dataset"}` — Deneb provides the host dataset; never `data.url` |
| **SVG-in-DAX** | Embed SVG as a base64-encoded `IMAGE()` DAX measure | Pass the SVG through `svg-report-lint` first; the SVG executes in the browser |
| **Tableau extension** | Vega-Lite spec via the Tableau Vega-Lite extension | Same data-binding rules as web surface |

The SVG-in-DAX pattern is documented in detail in
[`declarative-visualization.md`](declarative-visualization.md) §5.

---

## Stage 6 — Visual Verification

After delivery, verify the rendered output matches the design brief from Stage 1.
The full loop is documented in [`visual-feedback-loop.md`](visual-feedback-loop.md).

**Minimum checks (no browser tool required):**
1. Read the layout structure (confirm chart dimensions, axis labels, legend placement).
2. Confirm the data binding produced the expected shape (spot-check a known value).
3. Confirm font sizes are ≥8px on all text elements.

**Full loop (with `chrome-devtools-mcp` installed):**
1. Screenshot the rendered chart.
2. Check browser console for Vega/Vega-Lite errors.
3. Run the visual-feedback-loop referee:
   ```bash
   python3 plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py \
     --layout-report <layout.json> \
     --console-log <console.json> \
     --lighthouse-report <lighthouse.json>
   ```
   Iterate until `passed: true`.

---

## Security Properties of This Workflow

This workflow is designed so that **a spec can only reach a delivery surface if it
has passed Gate 101 (or Gate 103 for SVGs) and, for expression-bearing specs, the
`viz-spec-reviewer` mandatory review.** The gates are the contract; the stages are
the path.

The two linters share a purity contract:
- stdlib-only Python (no network, no subprocess, no eval/exec)
- argv-only paths; reject `..` and out-of-root paths
- non-zero exit on I/O errors (fail closed)
- exit 0 = clean, exit 1 = violation, exit 2 = I/O error

Do not weaken this contract by adding `try/except` that swallows violations, adding
network fetches to "verify" a remote schema, or adding any exec/eval path.
