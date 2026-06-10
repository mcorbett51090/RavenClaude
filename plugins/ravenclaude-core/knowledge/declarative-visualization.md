# Declarative Visualization Canon — Cross-Surface (Vega-Lite / Deneb / SVG)

**Scope:** Authoritative reference for spec-authoring agents on any surface: web
(vega-embed / react-vega / Evidence / Observable), Power BI (Deneb), Tableau
(extension / SVG export), and standalone SVG. The runnable linter + skill live at
[`../skills/declarative-visualization/`](../skills/declarative-visualization/SKILL.md).

> **Claim grounding:** grammar specifics below are marked `[unverified — training
> knowledge; verify at vega.github.io / deneb-viz.github.io]` where not confirmed
> from first principles. Security controls are load-bearing and independently
> verifiable; they are not marked unverified.

---

## 1. When to use which grammar

| Grammar | Best for | Not for |
|---|---|---|
| **Vega-Lite** | Statistical charts, multi-layer compositions, faceted small-multiples, interactive selections. Concise JSON; the most portable cross-surface option. | Custom force-directed graphs, pixel-level glyph control (use Vega). |
| **Vega** (full) | Custom marks, streaming updates, complex transforms, any chart Vega-Lite can't express declaratively. | Quick iterative work (Vega-Lite compiles to Vega; start there). |
| **Deneb (Power BI)** | Embedding Vega or Vega-Lite inside a Power BI report as a certified custom visual. Receives Power BI's cross-filter/highlight signals via the `powerbi` expression. | Non-Power-BI surfaces (use Vega/Vega-Lite directly). |
| **SVG** | Static or lightly animated illustrations, icon glyphs, custom shape overlays, SVG-in-DAX (Power BI Image visual). | Any chart needing dynamic data binding or interactivity (use Vega-Lite). |

**Decision rule:** start with Vega-Lite. Escalate to full Vega only when a required
mark or transform is missing. Use Deneb only when the target surface is Power BI.
Use SVG for non-chart visuals and the SVG-in-DAX pattern (see §5).

---

## 2. Grammar essentials

### 2a. Vega-Lite top-level structure

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "description": "Human-readable intent",
  "data": {"name": "source"},
  "mark": {"type": "bar", "tooltip": true},
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value",    "type": "quantitative"}
  },
  "width":  "container",
  "height": 280
}
```

Key invariants:
- `data.name` (named data source) + `data.values` dummy for local test — never
  `data.url` in committed specs (security rule §4).
- `width: "container"` for responsive embed; a fixed pixel width for Deneb
  (Power BI container drives the size).
- `$schema` must be a **local** relative URL or the official `https://vega.github.io/`
  origin — never a CDN or third-party host (security rule §4).

[unverified — verify the exact Vega-Lite v5 schema URL at vega.github.io]

### 2b. Encoding channels

| Channel | For |
|---|---|
| `x` / `y` | Cartesian axes |
| `color` | Category hue or sequential gradient |
| `size` | Bubble / dot size |
| `opacity` | Emphasis / fade |
| `tooltip` | `[{"field": "X", "title": "Label"}, ...]` or `true` |
| `detail` | Group without encoding (used in line/area for multi-series) |

### 2c. Common mark types

`bar`, `line`, `area`, `point`, `text`, `rect`, `rule`, `tick`, `arc` (pie/donut).
Composite: `layer` (overlaid), `hconcat` / `vconcat`, `facet` (small multiples).

### 2d. Interactivity — selections

```json
{
  "params": [{"name": "highlight", "select": "interval"}],
  "encoding": {
    "opacity": {
      "condition": {"param": "highlight", "value": 1},
      "value": 0.3
    }
  }
}
```

In Deneb, Power BI cross-filter hooks into the `powerbi` expression. In vega-embed
(web), selections are handled in-spec. [unverified — Deneb powerbi expression API;
verify at deneb-viz.github.io]

---

## 3. Surface → delivery map

| Surface | Runtime | How to embed | Data binding |
|---|---|---|---|
| **Web — vega-embed** | Browser, vega-embed JS library | `vegaEmbed('#id', spec, opts)` | Named data source → JS `view.change()` |
| **Web — react-vega** | React component | `<VegaLite spec={spec} data={data} />` | Props |
| **Web — Evidence** | Evidence.dev markdown | ` ```vega-lite ` fence block | Evidence `data` object |
| **Web — Observable** | Observable notebook | `Plot.plot()` or `vl.render(spec)` | Observable inputs / cells |
| **Power BI — Deneb** | Deneb certified custom visual | Paste JSON into Deneb visual's spec editor | Power BI fields mapped to `powerbi` expression |
| **Tableau — extension** | Tableau Dashboard Extension | Vega/Vega-Lite inside an extension iframe | Extension API `datasource.getSummaryDataAsync()` |
| **Tableau — SVG export** | Tableau calculated field + Image | SVG string in a calculated field | Tableau string expressions |
| **SVG standalone** | Browser / any HTML | `<img src="…">` / `<svg>…</svg>` inline | Static; dynamic via JS DOM manipulation |
| **SVG-in-DAX** | Power BI Image visual | `"data:image/svg+xml;utf8," & <DAX expr>` | DAX string concatenation — see §5 |

---

## 4. Security model (load-bearing)

Vega/Vega-Lite specs and SVG are **untrusted-input-shaped**: they can carry
network-access vectors and script-injection vectors. These controls are enforced by
the Gate 101 linter ([`../skills/declarative-visualization/lint.py`](../skills/declarative-visualization/lint.py))
and must be respected in all committed specs/templates.

### 4a. Vega network-access vectors

| Vector | Risk | Rule |
|---|---|---|
| `data.url` | Spec fetches from a remote URL at render time — SSRF / data exfiltration if URL is attacker-controlled | **Forbidden in committed specs.** Use `data.name` + bound values. |
| `transform.lookup` with an `from.data.url` | Same as above, via transform | **Forbidden.** Use `data.name` + join in the host app. |
| `loader` override (`{baseURL, http}`) | Can redirect all relative URL resolution | **Forbidden.** Never set a custom loader in a committed spec. |
| Remote `$schema` (non-vega.github.io host) | Could be re-served as a different schema version; also a network call | **Forbidden.** Use the official `https://vega.github.io/schema/…` origin or omit. |

Deneb's certified-build for Power BI disables the Vega loader at the runtime level,
providing defense-in-depth for Power BI specifically — but the rule still applies
to spec authoring because the same spec may be deployed on other surfaces.
[unverified — Deneb certified-build loader-disable; verify at deneb-viz.github.io /
AppSource cert docs]

### 4b. SVG script-injection vectors

| Vector | Risk | Rule |
|---|---|---|
| `<script>` elements | Arbitrary JS execution in SVG context | **Forbidden in committed SVG.** |
| `on*` event attributes (`onclick`, `onload`, etc.) | Inline JS execution | **Forbidden in committed SVG.** |
| `<foreignObject>` with embedded HTML | Potential XSS escalation | **Forbidden unless reviewed.** |
| `xlink:href` pointing to remote resource | Network call + potential JS (SVG 1.1) | **Forbidden in committed SVG.** |

### 4c. Reviewing user-supplied specs

Before rendering a user-supplied spec (not a committed template), apply the
allowlist: check for `data.url`, `transform.lookup`, custom `loader`, and SVG
`<script>`/`on*`. Reject or strip the offending key and explain the substitution
to the user. The linter ([`lint.py`](../skills/declarative-visualization/lint.py))
is the automated form of this review.

### 4d. The Gate 101 invariant

Every committed template in `spec-patterns/` must pass `lint.py` with exit 0. A
mutant template with a `data.url` must fail (exit 1). Both halves are asserted by
Gate 101 in `scripts/audit-gates.sh`. Any PR adding or modifying a `spec-patterns/`
template routes through `ravenclaude-core/security-reviewer` (declared invariant).

---

## 5. SVG-in-DAX (Power BI — Image visual)

SVG-in-DAX embeds dynamic SVG inside Power BI via the Image visual and DAX string
concatenation. It is a Power-BI-specific pattern; the neutral skill links here
rather than duplicating the PBI-specific detail.

Key constraints [unverified — verify against current Power BI docs]:
- The DAX expression must return a `data:image/svg+xml;utf8,` prefixed string.
- Character-limit for a DAX string column: ~32,767 chars (DAX TEXT limit).
- The Image visual rasterizes the SVG — script execution does not occur even if
  `<script>` is present, but omit it anyway for consistency and defense-in-depth.
- DAX string concat with `&` — build the SVG in pieces and concatenate.

Detailed pattern (fill values from Buhler / reconstruct from first principles if
the original source 404s — mark `[unverified — source 404'd; reconstructed]`).
See `plugins/power-platform/knowledge/` for Power-BI-specific SVG-in-DAX patterns
if present.

---

## 6. Visual-feedback-loop integration

For any spec, the primary verification is the
[`visual-feedback-loop`](./visual-feedback-loop.md) render-screenshot cycle (for
web surfaces where a browser tool is available) or the structural
[`pbir-layout-engine`](../skills/pbir-layout-engine/SKILL.md) check (for Power BI
PBIR layout facts). The Gate 101 linter covers security/network facts; it does NOT
replace Vega schema validation — the render loop is the schema check (a spec that
renders without error is schema-valid; a spec that does not render is not).

Stopping signals for a spec iteration:
1. `lint.py` exits 0 (no network sources, no script).
2. The spec renders without Vega/Vega-Lite parse errors.
3. The rendered chart matches the stated intent (visual check / screenshot).
4. For Power BI PBIR: `pbir-layout-engine` exits 0 (layout arithmetic correct).

---

## 7. Null / empty data handling

Every spec must degrade gracefully on empty data:
- Include a `condition` on `text` marks for the zero-data case, or a `layer` with
  a "No data" text mark triggered by `{"fold": ..., "filter": "length(data('source')) === 0"}`.
- Test with `data.values: []` before publishing.
- For Deneb/Power BI: empty cross-filter state should show an "empty" state, not
  a blank visual (which users interpret as a bug).

---

## 8. Checklist before publishing a spec

- [ ] `lint.py` exits 0 (no `data.url`, no `transform.lookup` with remote, no `loader`, no SVG `<script>`/`on*`)
- [ ] `$schema` is the official Vega/Vega-Lite origin or omitted
- [ ] Null/empty data case renders cleanly
- [ ] Chart matches intent (visual verification)
- [ ] For Power BI: PBIR layout linter exits 0
- [ ] For Deneb: spec tested with `data.name` + dummy `values` before wiring to Power BI fields
