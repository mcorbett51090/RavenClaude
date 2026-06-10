# Power BI custom-visual toolkit — options, trade-offs, and which to reach for

> **Last reviewed:** 2026-06-03.
> **Refresh trigger:** when a new Deneb major version ships, when Power BI changes AppSource certification requirements for custom visuals, or when Microsoft adds/removes native R/Python visual gateway behavior.
>
> **Discovery credit:** the landscape mapping that prompted this doc was drawn from the [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development) marketplace (Kurt Buhler). Content here is written from primary Microsoft documentation and first-party sources; it does not reproduce Data Goblins material.
>
> **Claim-grounding note:** behaviors tagged `[unverified — training knowledge]` have not been verified against a live Power BI service or official documentation in this session. Verify before quoting into customer work.

---

## Why a toolkit doc exists

Power BI ships a rich set of core visuals. When a core visual cannot express the insight — a custom violin plot, a diverging Likert scale, a custom SVG KPI badge — there are four meaningfully different routes:

1. **Core / AppSource visuals** — pre-built, certified, zero authoring.
2. **Deneb (Vega / Vega-Lite)** — declarative JSON grammar inside a certified custom visual.
3. **SVG via a DAX measure** — construct SVG markup as a DAX string, render via the Image URL tile.
4. **R or Python visuals** — ggplot2, matplotlib, seaborn, plotly-python inside Power BI.

Each route differs in authoring skill required, interactivity support, gateway dependency, and long-term maintainability. Picking the wrong one creates a visual that cannot be handed to the next developer, cannot filter other visuals, or fails silently after a gateway change.

---

## Decision guide — which route?

Work top to bottom. Stop at the first row that covers the requirement.

```
Does a core or AppSource-certified visual do the job?
    Yes → use it. No authoring cost, fully supported, no gateway, full interactivity.
    No  ↓

Does the insight require a Vega / Vega-Lite declarative grammar
(scatter layers, custom marks, faceting, Vega-Lite transforms)?
    Yes → Deneb. Certified, no gateway, Power BI cross-filter / bookmark support.
    No  ↓

Is the output a purely static badge or icon that DAX can encode as SVG markup
and the team is comfortable maintaining SVG strings in DAX?
    Yes → SVG via a DAX measure (Image visual). No custom visual install required.
    No  ↓

Does the team own R or Python skills and accept the gateway / static-image constraints?
    Yes → R visual (ggplot2) or Python visual (matplotlib / seaborn / plotly).
    No  → reconsider scope, or accept a core visual that approximates the insight.
```

---

## Option 1 — Core and AppSource visuals

**What it is:** The built-in visual library (bar, line, card, matrix, map, scatter, etc.) plus the Microsoft AppSource marketplace, which distributes certified and uncertified third-party custom visuals.

**Certification note:** "Certified" AppSource visuals have passed Microsoft's code review for security and portability — they can be rendered in exported PDFs and embedded in other Microsoft services. Non-certified visuals cannot. Source: [Microsoft Learn — certified custom visuals](https://learn.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals-certified) (retrieved 2026-06-03).

**When to use:** whenever a core or certified AppSource visual covers the requirement. No authoring, no maintenance, full Power BI interactivity (cross-filter, bookmarks, drill-through, conditional formatting, tooltips).

**Trade-offs:**

| | |
|---|---|
| Interactivity | Full — visual participates in cross-filter, bookmarks, drill by default |
| Maintainability | None — Microsoft or the publisher maintains it |
| Performance | Best — native rendering |
| Who can maintain it | Anyone |
| Limitation | Fixed grammar; cannot express novel chart types |

---

## Option 2 — Deneb (Vega / Vega-Lite)

**What it is:** Deneb is a **certified** Power BI custom visual authored by Daniel Marsh-Patrick that renders [Vega](https://vega.github.io/vega/) and [Vega-Lite](https://vega.github.io/vega-lite/) declarative JSON specifications directly inside the Power BI report canvas. It ships with the Vega and Vega-Lite libraries packaged inside the visual — no gateway is required and no internet dependency exists at render time.

Primary sources: [https://deneb-viz.github.io/](https://deneb-viz.github.io/) (retrieved 2026-06-03), [https://github.com/deneb-viz/deneb](https://github.com/deneb-viz/deneb) (retrieved 2026-06-03), [AppSource listing](https://appsource.microsoft.com/en-us/product/power-bi-visuals/coacervatelimited1596856650797.deneb).

**Interactivity:** Deneb integrates with Power BI's cross-filtering and cross-highlighting mechanism via its `powerbiInteractivity` encoding. A selection in Deneb can filter other visuals; other visuals can filter data flowing into Deneb. Bookmarks and selection states are preserved. [Source: Deneb documentation — interactivity, retrieved 2026-06-03.]

**When to use:**

- The required chart type (violin, diverging bar, dumbbell, custom heatmap, Sankey) is not available as a core or certified AppSource visual.
- The design team has JSON/JavaScript comfort and can write or adapt a Vega-Lite spec.
- The visual needs to participate in Power BI cross-filtering (SVG-via-DAX and R/Python cannot).
- The report is exported to PDF or embedded — certified custom visuals render; uncertified ones do not.

**Trade-offs:**

| | |
|---|---|
| Interactivity | Full cross-filter / highlight / bookmark integration via `powerbiInteractivity` |
| Maintainability | Medium — Vega-Lite specs are JSON and version-controlled; requires Vega-Lite knowledge |
| Performance | Good — Vega renders in the browser; large datasets may need aggregation pre-Deneb |
| Who can maintain it | Anyone with Vega / Vega-Lite knowledge; specs are readable text |
| Gateway dependency | None — libraries are bundled inside the certified visual |
| Certification | Certified AppSource visual — renders in PDF export and Power BI embedded |

**Gotcha:** Vega-Lite's transform and data pipeline lives inside the spec, not in DAX — if the spec pulls raw rows rather than pre-aggregated measures, it can move a lot of data to the browser. Pre-aggregate in DAX where possible.

---

## Option 3 — SVG via a DAX measure (Image visual)

**What it is:** DAX measures can return a string containing a data URI or an SVG snippet. Power BI's native Image visual (or the `image/SVG` measure trick in a card or table) renders the returned markup. No custom visual is installed; no AppSource dependency.

**When to use:**

- The output is a static badge, icon, status indicator, progress bar, or sparkline-as-SVG.
- The team needs something that works without installing any custom visual.
- The result does not need to cross-filter other visuals.
- The SVG can be fully expressed as a DAX string (no dynamic data binding beyond what DAX can compute).

**Trade-offs:**

| | |
|---|---|
| Interactivity | Static — SVG is rendered as an image; it does not participate in cross-filtering |
| Maintainability | Low — SVG strings in DAX are hard to read, version, and debug |
| Performance | Fast at small scale; DAX string concatenation over large row contexts can be slow |
| Who can maintain it | Requires DAX and SVG knowledge; context is easy to lose |
| Gateway dependency | None |
| Certification | Not applicable — no custom visual |

**Gotcha:** DAX string concatenation has a character limit (`[unverified — training knowledge]`). Very complex SVG will exceed it. Do not use this route for charts with more than a handful of dynamic data points.

---

## Option 4 — R visuals (ggplot2) and Python visuals (matplotlib / seaborn / plotly)

**What they are:** Power BI Desktop and the Power BI service both support R and Python as visual engines — the visual runs a script against the rows in its data roles and renders the output as a static image (PNG). ggplot2, matplotlib, seaborn, plotly-python, and any library installable in the script environment can be used.

**When to use:**

- Statistical graphics that have no equivalent in core or Deneb (kernel density estimates, diagnostic plots, survival curves, residual plots).
- The team owns strong R or Python data-science skills and the visual will not be handed to Power BI-only developers.
- The requirement is one-way: the visual informs a user but does not need to drive cross-filtering.

**Trade-offs:**

| | |
|---|---|
| Interactivity | Static — R/Python visuals render as a PNG image; they do not cross-filter other visuals `[unverified — training knowledge: confirm with current Power BI docs]` |
| Maintainability | Low without R/Python ownership — the script is embedded in the report; version control requires PBIP |
| Performance | Slower than native — a subprocess is spawned per render; large datasets add latency |
| Who can maintain it | Requires R or Python + data-viz library skills |
| Gateway dependency | **Yes for service refresh.** Published R/Python visuals require an **on-premises data gateway** with R/Python installed in the service. Without a gateway the visual is blank in the service. `[unverified — training knowledge: confirm current Power BI service requirements]` |
| Certification | Cannot be certified in the AppSource sense; not portable to PDF export `[unverified]` |

**Gateway note:** this is the most common surprise. A visual that works in Desktop is blank or errors in the Power BI service unless an on-premises data gateway is configured with a matching R/Python runtime. Verify current gateway requirements against Microsoft Learn before committing to R/Python visuals in production. `[unverified — training knowledge]`

---

## Summary table

| Route | Cross-filters? | Gateway needed? | Certified? | Who maintains it | Authoring cost |
|---|---|---|---|---|---|
| Core / AppSource | Yes | No | Yes (certified tier) | Publisher | Zero |
| Deneb (Vega-Lite) | Yes | No | Yes | Vega-Lite author | Medium |
| SVG via DAX | No | No | N/A | DAX + SVG author | Low–Medium |
| R visual | No | Yes (service) | No | R/ggplot2 author | Medium–High |
| Python visual | No | Yes (service) | No | Python author | Medium–High |

---

## Deneb spec linting and security review (delegation to ravenclaude-core)

When authoring or reviewing a Deneb (Vega-Lite / Vega) spec for a Power BI report, the
`power-bi-engineer` agent **must** route the spec through the declarative-visualization
linter (Gate 101) and, for expression-bearing specs, the `viz-spec-reviewer` agent in
`ravenclaude-core`. These are domain-neutral tools — do not build a parallel review in
this plugin.

### Mandatory lint pass (Gate 101)

Before embedding any Deneb spec in a Power BI report:

```bash
python3 <marketplace>/plugins/ravenclaude-core/skills/declarative-visualization/lint.py <spec.json>
```

A non-zero exit blocks delivery. The linter enforces:
- No `data.url` (remote data fetch) — **Deneb specs must use `"data": {"name": "dataset"}`** (Power BI provides the dataset via the `name` binding; a `url` would bypass Power BI's data gateway entirely).
- No loader overrides that open a remote channel.
- No remote `$schema` from an attacker-controlled host.
- No transform.lookup against a remote URL.
- No `<script>` / `on*` / `<foreignObject>` in SVG specs.

For Vega specs (not Vega-Lite) that use `signal`, `expr`, or `calculate` expressions,
also run with `--strict`:

```bash
python3 <marketplace>/plugins/ravenclaude-core/skills/declarative-visualization/lint.py --strict <spec.json>
```

A `--strict` failure triggers a mandatory review (see below).

### SVG-in-DAX: mandatory SVG lint pass (Gate 103)

Any SVG image constructed for use with the Power BI Image visual must also pass:

```bash
python3 <marketplace>/plugins/ravenclaude-core/skills/svg-report-lint/lint.py <image.svg>
```

The SVG linter checks geometry (viewBox, aspect ratio, minimum font size) and security
(`<script>`, `on*` handlers, `<foreignObject>`, remote `href`/`xlink:href`).

### When to dispatch viz-spec-reviewer (ravenclaude-core)

Route to `ravenclaude-core/viz-spec-reviewer` for a full security review when:
- The Deneb spec is a **Vega** (not Vega-Lite) spec and uses `signal`, `expr`, or `calculate`.
- The spec will be embedded in a **shared / multi-tenant** report surface.
- The linter exits 0 with warnings (advisory flags that require human judgment).
- You are adopting a Deneb spec written by a third party.

The reviewer emits a structured verdict (`LGTM`, `NEEDS-CHANGES`, or `DENY`). A `DENY`
means the spec must not ship until all BLOCKERs are resolved.

### Why domain-neutral tooling, not Power Platform-specific

Vega-Lite / Vega / SVG are grammar-neutral — the same security surface exists whether a
spec renders in a Power BI report, a web dashboard, or a Tableau extension. Per the
`ravenclaude-core` house rule (domain plugins extend core via skills and knowledge; they
do not fork domain-neutral review agents), the linter and reviewer live in core and
`power-bi-engineer` delegates to them.

---

## See also

- [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) — visual.json structure for authoring PBIR Enhanced reports programmatically
- [`../best-practices/bi-measures-not-calculated-columns.md`](../best-practices/bi-measures-not-calculated-columns.md) — keep aggregation logic in measures, not calculated columns, before passing data to any visual
- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — the agent that owns visual and semantic model decisions
- [`../../ravenclaude-core/knowledge/design-first-report-workflow.md`](../../ravenclaude-core/knowledge/design-first-report-workflow.md) — the end-to-end workflow: design → spec → lint → review → deliver → verify
- [`../../ravenclaude-core/agents/viz-spec-reviewer.md`](../../ravenclaude-core/agents/viz-spec-reviewer.md) — the agent to dispatch for Vega signal/expression review
- Deneb documentation: [https://deneb-viz.github.io/](https://deneb-viz.github.io/)
- Deneb GitHub: [https://github.com/deneb-viz/deneb](https://github.com/deneb-viz/deneb)

---

_Last reviewed: 2026-06-10 by `claude`_
