---
name: report-visualization-design
description: "Design a Power BI report/visualization in the Kurt-Buhler / Bas-Dohmen mold — a checklist-driven method: decide the question first, structure the page with the 3-30-300 information-seeking hierarchy, choose the visual by question-type, design headline KPIs with actual/target/gap + pre-attentive color, lay everything on an 8-pt grid, and tune density / color tokens / accessibility. Emits a layout that maps cleanly onto PBIR (visualType enum + pbir-layout-engine geometry). Used by `power-bi-engineer` (primary)."
---

# Report Visualization Design Skill

**Purpose:** Give `power-bi-engineer` a concrete, reproducible method for designing a Power BI report that *communicates* — not just renders. The method distills the published design canon of **Kurt Buhler** (Data Goblins / SQLBI — the 3-30-300 rule, the "anatomy of an effective KPI visual", pre-attentive color) and the **design-first** school associated with **Bas Dohmen** (How to Power BI — decide-first, prototype-then-build, less-is-more). Every step is a checklist item, not an aesthetic opinion, so a design from this skill is **directly realizable as PBIR** (it names real `visualType`s and emits grid-aligned geometry).

> **Sourcing & honesty.** The load-bearing techniques are **cited inline** with retrieval date 2026-06-08. Where a technique is the broader Power BI design canon rather than a specific named source — or where attribution to a specific person can't be confirmed from a primary source — it is marked `[unverified attribution]`. The **value is the reproducible technique**, not the name-drop. Re-verify the volatile bits (`visualType` strings, schema rules) at use via the PBIR reference below.

## When to Use

- **Designing a new report/page from a blank canvas** — you have a data model and a business question, and need a layout that lands.
- **A report "makeover"** — an existing report is cluttered, slow to read, or "Power BI slop" (every-field-on-the-page) and needs restructuring.
- **Reviewing someone else's report for communication quality** — design is a review dimension, the same way performance and DAX-correctness are.
- **Before authoring PBIR** — run this skill to decide *what goes where*, then hand the result to [`pbir-layout-engine`](../../../ravenclaude-core/skills/pbir-layout-engine/SKILL.md) to lint the geometry and [`pbir-enhanced-reference.md`](../../knowledge/pbir-enhanced-reference.md) to author the JSON.

## How this maps onto our PBIR canon (do not duplicate — point at these)

This skill is the **design layer**. The **realization layer** already exists in the marketplace; this skill produces inputs for it, it does not re-implement it:

| Layer | Owned by | This skill's relationship |
|---|---|---|
| **Which `visualType` strings are real + their query roles** | [`knowledge/pbir-enhanced-reference.md`](../../knowledge/pbir-enhanced-reference.md) § 1 (the `visualType` enum) | This skill's chart-selection step picks **only** from that enum (`kpi`, `cardVisual`, `clusteredBarChart`, `lineChart`, `pivotTable`, …). Never invent a visual name. |
| **Page geometry — no-overlap / within-canvas / equal-gap / column-alignment + PBIR schema checks** | [`pbir-layout-engine`](../../../ravenclaude-core/skills/pbir-layout-engine/SKILL.md) (`lint.py`) | This skill emits x/y/w/h on an 8-pt grid; run `lint.py` on the page to *prove* the grid holds. The helper below produces lint-clean coordinates. |
| **Authoring the visual/page/report JSON (filterConfig, objects vs visualContainerObjects, literal suffixes)** | [`knowledge/pbir-enhanced-reference.md`](../../knowledge/pbir-enhanced-reference.md) | After this skill decides the design, author the JSON there. |
| **Why a deployed report renders blank** | [`knowledge/pbir-enhanced-report-loading.md`](../../knowledge/pbir-enhanced-report-loading.md) | Debug runbook — out of scope here. |

The handoff: **design here → realize in PBIR there.** A design that names a non-enum visual or off-grid geometry is a defect this skill is meant to prevent.

## The method — six steps, each a checklist

### Step 1 — Decide the question first (decide-first, not data-first)

The single biggest design failure is building around *what's in the model* instead of *what must be decided*. Bas Dohmen's framing: *"Reports fail for one reason: they're built around what's available in the data, not around what needs to be decided"* ([datatraining.io/powerbidesigntransformation](https://datatraining.io/powerbidesigntransformation), retrieved 2026-06-08).

- [ ] Write the **one decision or question this page answers**, as a sentence (e.g. *"Are we meeting the orders target, and which regions/products are driving the gap?"*). If you can't, the page isn't ready to design.
- [ ] List the **3-second takeaway** (the headline answer) separately from the **drill questions** (what the user asks next). These map to the layout tiers in Step 2.
- [ ] **One page = one question.** A second decision is a second page, reached by navigation — not a crowded single page.

### Step 2 — Structure the page with the 3-30-300 hierarchy (Buhler)

Kurt Buhler's **3-30-300 rule** paraphrases Shneiderman's visual information-seeking mantra ("overview first, zoom and filter, then details-on-demand") into report-design tiers ([sqlbi.com — Introducing the 3-30-300 rule](https://www.sqlbi.com/articles/introducing-the-3-30-300-rule-for-better-reports/), retrieved 2026-06-08):

| Tier | User gets… in | Content | Placement (Western reading flow) |
|---|---|---|---|
| **3 seconds** | an **overview** of the most important questions/areas | headline KPIs + 1 trend; simple visuals (`kpi`, `cardVisual`, `lineChart`) | **top-left**, moving right |
| **30 seconds** | the ability to **filter & zoom** to periods/categories | performance-by-dimension bars + slicers; conditional formatting on under-performers | middle-left / center |
| **300 seconds** | **details-on-demand** to inform an action | curated matrix / supplemental table; drillthrough; dynamic links | bottom-right |

- [ ] Place the **3-second** content top-left. Keep it focused on the primary question; resist filling it.
- [ ] Group **30-second** filter/zoom visuals in the center. **Limit to 3-5 key breakdowns** — "too many visuals in the filter section creates cognitive overload" (ibid.).
- [ ] Put **300-second** detail in the bottom-right; prefer a `pivotTable` / `tableEx` and **drillthrough** over dumping a wide table onto the main view.
- [ ] **The rule also applies across pages:** an executive summary is the 3-second view; a category page is the 30-second view; a drillthrough/detail page is the 300-second view. Use cross-report/within-report drillthrough to keep context when zooming (ibid.).

### Step 3 — Choose the visual by the question-type, not by taste

Match the chart to the analytical question. These seven shapes cover ~95% of business reporting ([tabulareditor.com — Data visualization best practices](https://tabulareditor.com/blog/data-visualization-best-practices-for-power-bi-reports), retrieved 2026-06-08). Pick the `visualType` from the [PBIR enum](../../knowledge/pbir-enhanced-reference.md) § 1:

| The question is about… | Use | PBIR `visualType` |
|---|---|---|
| **A single headline number + status** | KPI card | `kpi`, `cardVisual`, `card`, `multiRowCard` |
| **Comparing categories** | bar / column | `clusteredBarChart`, `clusteredColumnChart` |
| **Trend over time** | line / area | `lineChart`, `areaChart` |
| **Composition (2-3 parts max)** | donut (sparingly) | `donutChart`, `pieChart` |
| **Change between two points** | waterfall | `waterfallChart` |
| **Relationship between two metrics** | scatter (X & Y must be measures) | `scatterChart` |
| **Detailed/precise values** | table / matrix | `tableEx`, `pivotTable` |
| **Geographic comparison** | map | (per enum — verify at use) |

- [ ] For each visual on the page, state the **question it answers**. A visual that doesn't answer a listed question is a candidate to cut.
- [ ] **Donut/pie only for 2-3 slices.** More slices → bar chart.
- [ ] **Mixed dimension + measure in a table → `pivotTable`, never `tableEx`** (it silently blanks in Fabric — see the `tableEx` vs `pivotTable` callout in [pbir-enhanced-reference.md](../../knowledge/pbir-enhanced-reference.md) § 1).
- [ ] To let users **switch the metric/dimension shown**, prefer **field parameters** or **calculation groups** over duplicate visuals ([sqlbi 3-30-300](https://www.sqlbi.com/articles/introducing-the-3-30-300-rule-for-better-reports/), retrieved 2026-06-08).

### Step 4 — Design the headline KPI (Buhler's "anatomy of an effective KPI visual")

A KPI card earns its place only if it answers *"is this good or bad, and is it getting better or worse?"* without the reader doing arithmetic ([data-goblins.com — KPIs and cards in Power BI](https://data-goblins.com/power-bi/kpi-templates), retrieved 2026-06-08). It must carry three layers:

- [ ] **The Number** — aggregated, with appropriate **units and decimal precision** ("only the level of detail necessary"). No default font; match org branding (ibid.).
- [ ] **The Meaning** — a **baseline/target** (budget, forecast, prior period) and **the gap** to it. The gap is the most load-bearing element — it answers "good or bad?" pre-attentively (data-goblins, retrieved 2026-06-08).
- [ ] **The Context** — a trend (sparkline / `kpi.TrendLine`) or small breakdown, **only if genuinely useful**. "Overwhelming users with information is one of the easiest ways to make your report ineffective" (ibid.).
- [ ] **Color only to steer attention** — neutral when on-target, **deep red when off-target** (leverages the implicit negative association). Don't color for decoration (ibid.).
- [ ] **No more than 3-4 KPI callouts** across the top — excess dilutes impact (ibid.).
- [ ] Use **DAX format strings** for up/down arrows and signed gaps so status reads instantly ([sqlbi 3-30-300](https://www.sqlbi.com/articles/introducing-the-3-30-300-rule-for-better-reports/), retrieved 2026-06-08). Watch the format-scale trap (`0.0\%` vs `0.0%`) — see [pbir-dax-pitfalls.md](../../knowledge/pbir-dax-pitfalls.md).
- [ ] **SVG micro-viz** (custom sparkline measures) carry maintenance cost — if you use them, **hide/mark the helper measures private** so self-service users don't misuse them (data-goblins, retrieved 2026-06-08).

### Step 5 — Lay it on an 8-point grid (Dohmen-school precision + our linter)

Disciplined spacing is what separates a "makeover" from a mess. The widely-used Power BI design default is a **1664×936 canvas on an 8-point grid**, key metrics in the top-left zone `[unverified attribution]` (canon summarized at [lukasreese.com — dashboard design best practices](https://lukasreese.com/2025/08/20/power-bi-dashboard-design-best-practices-guide/), retrieved 2026-06-08 — page returned HTTP 403 on direct fetch this session, so the numeric tokens are `[unverified — secondary summary]`; treat 1664×936 as a sensible default, not gospel).

- [ ] Choose a **canvas size** (default 1664×936 / 16:9) and an **8-px grid module** — every x, y, width, height is a multiple of 8.
- [ ] **Equal gaps** between visuals; **align columns**. These are exactly the checks `pbir-layout-engine`'s `check-3` (equal-gap) and `check-4` (column-alignment) enforce.
- [ ] Use the [`grid.py`](grid.py) helper below to turn a tier-template + visual count into lint-clean x/y/w/h. Then **run the linter** to prove it: `python3 plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py <page.json>`.

### Step 6 — Tune density, color tokens & accessibility (less-is-more)

The "less is more" / data-ink discipline: *think about what you can remove to make the chart simpler, not what you can add to make it nicer* ([tabulareditor.com](https://tabulareditor.com/blog/data-visualization-best-practices-for-power-bi-reports), retrieved 2026-06-08).

- [ ] **Color budget: ≤ 6 colors** on a page; more is visual noise `[unverified attribution]` / canon (lukasreese summary + tabulareditor, retrieved 2026-06-08). Reserve a **bright accent** for the actionable insight; use subtler/lighter tones for everything else.
- [ ] **Typography:** one type family, a small size scale (e.g. title / KPI-number / label). Avoid eccentric or over-decorated styles (tabulareditor, retrieved 2026-06-08).
- [ ] **Density:** the brain "doesn't handle large amounts of information presented simultaneously very well" — prefer white space and a second page over a crammed one (ibid.).
- [ ] **Contrast / accessibility:** white chart backgrounds on a light-grey page give the contrast step; ensure the message survives **any interaction** (filtered states must still read correctly so users trust the numbers) (ibid.). Don't encode meaning in color alone — pair red/green with an arrow or sign for color-blind users `[unverified attribution]` / WCAG canon.
- [ ] **Data-ink:** drop heavy borders, gridlines, and dark table fonts; let the data carry the page (ibid.).
- [ ] **Quality starts in the semantic model** — consistent measure names, formats, and `displayFolder`s prevent business logic scattering across visuals (ibid.; enforced by [`enforce-measure-metadata.md`](../../best-practices/enforce-measure-metadata.md) + the `validate-tmdl-measure-metadata.sh` hook).

## Optional helper — `grid.py` (8-pt layout solver → PBIR-ready geometry)

[`grid.py`](grid.py) is a **stdlib-only, fail-safe** coordinate solver. Given a canvas, a margin, a gap, and a chosen **3-30-300 template**, it emits each region's `x/y/width/height` snapped to the 8-pt grid — coordinates that pass `pbir-layout-engine`'s within-canvas / no-overlap / equal-gap / column-alignment checks, ready to drop into a PBIR `page.json`'s `position` blocks.

```text
python3 plugins/power-platform/skills/report-visualization-design/grid.py --template 3-30-300 --format json
python3 .../grid.py --template kpi-strip --kpis 4 --canvas 1664x936 --format json
```

Templates: `3-30-300` (overview top-left / filter band / detail bottom-right), `kpi-strip` (N equal KPI cards across the top), `golden-overview` (single hero visual + supporting column). It only does arithmetic (no network, no file writes); an invalid request prints a diagnostic to stderr and exits non-zero. Verify the output against the linter before authoring JSON.

## Output Contract

When this skill drives a design deliverable, the report ends with the cross-plugin Structured Output JSON block per [`../../../ravenclaude-core/skills/structured-output/SKILL.md`](../../../ravenclaude-core/skills/structured-output/SKILL.md), plus the Power Platform `## Output Contract` lines (Status / Files changed / Gates passed / Open questions / Licensing impact / Grounding checks performed) from the [plugin constitution](../../CLAUDE.md) § 6. For a design, **Gates passed** should cite the `pbir-layout-engine` lint result on the emitted geometry.
