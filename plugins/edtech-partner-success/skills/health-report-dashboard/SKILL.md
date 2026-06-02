---
name: health-report-dashboard
description: Build a self-contained, Power-BI/Tableau-style HTML portfolio report from partner-health data — KPI cards (NRR/GRR/avg-health/red-count/renewal-risk), a health-band donut, a 12-week trend line, a peer-cohort range chart, score-component drill-downs, red-flag surfacing, and a sortable/filterable per-partner table. Used by `learning-analytics-analyst` (primary) + `partner-success-manager`. Ships with a ready-to-open demo (sample data) AND regenerates from real data — replace `bi-report/data.json` (same shape) and re-run the generator. Invoke when someone asks for a partner-health dashboard, a "report I can show leadership", a QBR data view, or "how's my whole book doing in one picture".
---

# Skill: health-report-dashboard

**Purpose:** turn the partner-health numbers the PSM team already tracks into a
**single, self-contained HTML report** that looks like an advanced Power BI /
Tableau page — but needs no BI license, no server, and no internet. It opens by
double-clicking the file. This is the visual companion to the
[`health-score-dashboard`](../../templates/health-score-dashboard.md) *spec* and
the [`partner-health-scoring`](../partner-health-scoring/SKILL.md) skill (which
defines the score itself).

It exists in two halves, so you get **both** a thing to look at now and a real tool:

1. **Demo (ships in the plugin).** `plugins/edtech-partner-success/bi-report/data.json`
   holds realistic **synthetic** data; `report.html` is the rendered demo. Open it
   to see the whole layout immediately.
2. **Generator (the capability).** Replace `data.json` with a real export in the
   same shape and re-run — the report rebuilds from your numbers.

## When to use

- "Show me how my whole book is doing" / "I need a portfolio health view."
- Leadership / EBR wants a one-glance report of every partner's health, trend, and risk.
- QBR prep — drop one partner's drill-down (components + red flags + dates) into the deck.
- You have partner-health numbers in a spreadsheet and want a clean, shareable page.

## What the report shows

| Section | Plain-language question it answers |
|---|---|
| KPI cards | "Are we keeping/growing revenue (NRR/GRR)? What's the average health? How many are red? How many renewals are at risk?" |
| Health-band donut | "Of all my partners, how many are Healthy / Watch / Act-now?" |
| 12-week trend line | "Is the book getting healthier or sliding?" |
| Peer-cohort range | "Is this partner ahead of or behind its peer group?" |
| Per-partner table | "Sort by score, filter to red, search a name." |
| Row drill-down | "What's moving this partner's score, what red flags are live, when do they renew?" |
| Data-quality banner | "Is anyone red only because their data is stale?" (don't act on a sync problem) |

Every metric carries a **"?" explainer** in everyday words, and the whole report
reads at roughly a 5th-grade level — the jargon (NRR, GRR, IQR) is the small print.

## How to (re)build it

```shell
# rebuild every plugin report that has bi-report/data.json
python3 scripts/generate-bi-report.py

# just this plugin
python3 scripts/generate-bi-report.py --plugin edtech-partner-success

# CI / pre-commit: fail if the committed report.html is stale
python3 scripts/generate-bi-report.py --check
```

The generator is **plugin-agnostic**: any plugin that ships a `bi-report/data.json`
gets a `report.html`. The charts are hand-rolled inline SVG and the sort/filter/
drill-down is vanilla JS, so the output stays fully self-contained (no CDN, no
charting library) — consistent with the rest of the marketplace's static surfaces.

## The data shape (what to export from real systems)

`bi-report/data.json` (see the shipped sample for a complete, filled example):

```jsonc
{
  "report":  { "title": "...", "subtitle": "...", "refreshed": "YYYY-MM-DD",
               "synthetic": true, "owner": "..." },     // set synthetic:false for real data
  "bands":   { "green": [70,100], "yellow": [50,69], "red": [0,49] },
  "components": [ { "key": "adoption", "name": "Adoption depth", "weight": 25,
                    "half_life_days": 90, "plain": "everyday explanation" }, ... ],
  "kpis":    [ { "key": "nrr", "label": "Net revenue kept + grown", "short": "NRR",
                 "value": 108, "unit": "%", "delta": 2.0, "good": "up",
                 "plain": "everyday explanation" }, ... ],
  "cohort":  { "label": "K-12 · Enterprise · Year 2+", "median": 68, "p25": 54, "p75": 81, "size": 11 },
  "trend_weeks": ["12 wk ago", ..., "This wk"],
  "portfolio_trend": [62, 63, ..., 68],                  // 12 portfolio-average scores
  "partners": [ {
    "name": "Riverside Unified", "segment": "k12", "psm": "Dana L.",
    "score": 81, "delta": 3, "band": "green",            // band optional — derived if omitted
    "components": { "adoption": 84, "touchpoint": 88, ... },
    "spark": [72, 73, ..., 81],                          // last 12 weeks of the composite
    "flags": ["plain-language red-flag sentence", ...],  // empty = none
    "play": "Maintain", "last_touch": "YYYY-MM-DD",
    "next_qbr": "YYYY-MM-DD", "renewal": "YYYY-MM-DD" } ]
}
```

The component keys/weights/half-lives mirror
[`partner-health-scoring`](../partner-health-scoring/SKILL.md) and the
[`health-score-dashboard`](../../templates/health-score-dashboard.md) spec; the
red-flag sentences mirror that spec's six triggers; the metric vocabulary mirrors
[`psm-metrics-glossary.md`](../../knowledge/psm-metrics-glossary.md).

## FERPA / privacy (load-bearing)

- **Synthetic identifiers only in anything that ships or is shared.** The demo
  `data.json` uses invented districts and PSM initials — never real partner or
  student data. Keep `report.html` out of any repo that isn't access-controlled.
- The report is **partner-level**, never student-level. Do not add student PII
  columns. Student-level analysis routes through `security-reviewer` first
  (plugin constitution §2).
- A real export should set `report.synthetic` to `false` and live next to the
  data it came from, not in a public location.

## Adapting this to other plugins ("apply where applicable")

Any plugin with quantitative, per-entity data can ship a `bi-report/data.json` and
get a report for free. Natural candidates and the data that would feed them:

| Plugin | Per-entity rows | KPIs | Trend / cohort |
|---|---|---|---|
| `finance` | accounts / cost centers | revenue, margin, cash runway, variance | monthly P&L trend |
| `project-management` | projects / sprints | % on-track, open risks, velocity | burndown |
| `salesforce` | reps / segments | win rate, cycle time, quota attainment | pipeline funnel |
| `data-platform` | pipelines / datasets | freshness, row-count delta, SLA hits | latency trend |

For a domain whose shape differs a lot from partner-health (e.g. a P&L waterfall),
either extend the generator's chart helpers or add a domain-specific renderer that
follows the same self-contained, token-inlined pattern.

## Hand-off

- **Score design / weights / decay** → [`partner-health-scoring`](../partner-health-scoring/SKILL.md) (`learning-analytics-analyst`).
- **Turning a drill-down into a QBR slide** → [`qbr-composition`](../qbr-composition/SKILL.md) (`qbr-composer`).
- **Which play a red flag triggers** → the recovery / renewal / expansion play skills (`success-playbook-designer`).
- **Anything student-level** → `ravenclaude-core/security-reviewer` (mandatory).

## References

- Spec: [`templates/health-score-dashboard.md`](../../templates/health-score-dashboard.md)
- Metric definitions: [`knowledge/psm-metrics-glossary.md`](../../knowledge/psm-metrics-glossary.md)
- Generator: `scripts/generate-bi-report.py`
- Demo data + output: `bi-report/data.json` → `report.html`
