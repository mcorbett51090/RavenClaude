---
title: Charting Library Selection — 2026
audience: dashboard-engineer, frontend-eng, psm-tooling-lead
status: stable
last_reviewed: 2026-06-04
refresh_triggers:
  - "Tremor v4 promoted out of beta (Vercel-owned)"
  - "Recharts major version change"
  - "ECharts WebGL renderer change"
  - "INP threshold changes in Core Web Vitals"
sources_verified_at: 2026-06-04
---

# Charting Library Selection — 2026

> 2026 React/JS chart landscape. Decision rule first, then maintained-status table, then the SVG-vs-Canvas threshold that drives the actual choice for dense operational dashboards.

---

## Decision rule (apply in order, stop at first match)

1. **Brand-critical custom viz?** → **Visx** (D3 primitives, ~15KB, max control, lowest bundle).
2. **>100K data points or scientific/3D?** → **ECharts with WebGL** or **Plotly** (Plotly's catalog is broader; ECharts-WebGL is leaner).
3. **5K–100K points or real-time stream?** → **Apache ECharts** (Canvas, ~300KB).
4. **<5K points, React + Tailwind, dashboards?** → **Tremor v4** (beta, Vercel-owned) or **Recharts** (Tremor uses Recharts under the hood).
5. **Non-React simple chart, smallest footprint?** → **Chart.js**.
6. **Aesthetic-first, lots of chart varieties?** → **Nivo**.

---

## Library status (2026)

| Library | Render | 2026 maintenance | Bundle (gz) | Best fit | Source |
|---|---|---|---|---|---|
| **Recharts** | SVG | 48.9M weekly npm DLs — highest of any React chart lib. Default React pick. | ~95KB | <5K points, dashboards | [LogRocket — Best React chart libs 2026](https://blog.logrocket.com/best-react-chart-libraries-2026/) |
| **Tremor v4 beta** | SVG (Recharts under the hood) | **Vercel-acquired Jan 22 2025.** Fully MIT (Blocks now free). v4 in beta as of mid-2026. | ~150KB w/ Recharts | Tailwind React dashboards, KPI cards, fast scaffolding | [Vercel — acquires Tremor](https://vercel.com/blog/vercel-acquires-tremor) |
| **Apache ECharts** | Canvas (+ WebGL option) | Apache project, very active. Handles 100K+ pts. | ~300KB | Dense operational dashboards, time-series at scale, real-time | [OpenObserve — ECharts over Plotly](https://openobserve.ai/blog/why-apache-echarts-won-over-plotly-in-our-tech-stack/) |
| **Visx** | SVG (D3 primitives) | Airbnb-maintained, steady. Modular, low-level. | ~15KB core | Custom brand-specific viz, max control, lean | [Querio — 8 top React chart libs 2026](https://querio.ai/articles/top-react-chart-libraries-data-visualization) |
| **Nivo** | SVG + Canvas + HTML | Community-maintained, broad catalog. | ~200KB | Aesthetic dashboards, varied chart types, exploratory | [npm-compare](https://npm-compare.com/@nivo/line,@vx/shape,chart.js,recharts) |
| **Plotly.js** | SVG / Canvas / WebGL | Actively maintained. Rich science/3D catalog. | ~3MB full / smaller bundles | Scientific, ML, 3D, large feature catalog | [Stackshare — Plotly vs ECharts](https://stackshare.io/stackups/echarts-vs-plotly-js) |
| **Chart.js** | Canvas | Community-maintained, very active. Simple API. | ~70KB | Simple charts, small footprint, non-React-first | [Medium — D3/ECharts/Recharts/Plotly](https://medium.com/@pallavi8khedle/when-to-use-d3-echarts-recharts-or-plotly-based-on-real-visualizations-i-ve-built-08ba1d433d2b) |

[verify-at-use — 2026-06-04 — npm download numbers and Tremor v4 beta status]

---

## SVG vs Canvas threshold (the choice that actually matters)

Across 2026 practitioner write-ups the threshold lines up consistently:

- **SVG (Recharts, Tremor, Visx, Nivo SVG-mode)** — breaks down ~**5K nodes per chart**. Above this, re-render cost kills INP.
- **Canvas (ECharts, Chart.js, Nivo Canvas-mode)** — handles **100K+ points** comfortably.
- **WebGL (ECharts-GL, Plotly WebGL)** — required for **>1M points** or 3D.

**For real-time / streaming dashboards, Canvas is the default** regardless of point count — SVG re-render churn blows INP even at <5K points when updates are sub-second.

---

## INP-aware sizing (2026 Core Web Vitals)

INP <200ms is the **2026 budget that matters most** for analytics UIs. Bundle-size ranking by INP impact:

```
Visx (~15KB) << Recharts (~95KB) << Tremor (~150KB) << ECharts (~300KB) << Plotly (~3MB)
```

**Lever rules:**
- Code-split aggressive on heavier libs (ECharts, Plotly).
- Lazy-load chart components below the fold.
- Memoize formatters and tooltip render functions — unmemoized formatters are the silent INP killer.
- Pre-aggregate at the semantic layer (Cube) — fewer points = lower re-render cost regardless of library.

---

## The Tremor caveat (status check)

- **Vercel acquired Tremor January 22, 2025.** Cofounders Severin Landolt + Christopher Kindl joined Vercel's Design Engineering team to work on the Vercel Dashboard + v0 generative UI.
- **All components MIT-licensed** as of acquisition — Blocks was previously a paid tier; now free.
- **v4 still in beta** as of mid-2026. The beta cadence has slowed, but the Vercel acquisition is a stability signal not a finished migration.
- **Recommendation:** new projects on v4-beta are reasonable; production projects on v3.x should plan v4 migration cautiously, not rush it.

---

## Vendor-claim discipline

When a library's docs/blog claim "renders 1M points smoothly" or "10× faster than X":

- Verify against the **specific chart type** you'll use (line + tooltip + zoom = much heavier than static bar).
- Check **INP on a representative slice of your data**, not the vendor's demo dataset.
- Check **bundle cost after tree-shaking** — vendor numbers often quote full bundle.

The 2026 trap: a chart library that benchmarks well in isolation can still blow your INP budget if your tooltip render is unmemoized or your formatter constructs a new `Intl.NumberFormat` per call.

---

## See also

- [`dashboard-productization-multi-tenant-2026.md`](./dashboard-productization-multi-tenant-2026.md) — when the question is render-layer-because-we're-productizing.
- [`snowflake-operational-dashboard-patterns.md`](./snowflake-operational-dashboard-patterns.md) — Snowflake-side mechanics that feed the render layer.
- [`../../ravenclaude-core/best-practices/operational-console-design.md`](../../ravenclaude-core/best-practices/operational-console-design.md) — domain-neutral console design (performance budgets, accessibility).
