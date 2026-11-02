---
name: find-plot-recipe
description: "Look up a library-agnostic plot recipe and runnable implementations across 15 charting libraries (matplotlib, seaborn, plotly, bokeh, altair, ggplot2, Makie, D3, ECharts, ...) from anyplot.ai's public read-only API during the EDA visualization step. Opt-in third-party reference — public HTTP API by default, remote MCP strictly opt-in. Verify AI-generated code before trusting it."
---

# Skill: find-plot-recipe

## What this is

A lookup helper for the **visualization step of EDA**: given a plot intent ("grouped
bar with error bars", "ridgeline", "calendar heatmap") and a target library, fetch a
starting implementation from **[anyplot.ai](https://anyplot.ai)** — "the open plot
catalogue". Each plot begins as a library-agnostic markdown spec; AI then generates and
reviews an implementation in each of ~15 libraries across Python, R, Julia and
JavaScript, with a per-implementation quality score and a colourblind-safe default
palette ("imprint").

Use it to shorten "which chart, and how do I write it in *this* library" — then bring
the result back into the `eda-workflow` discipline: read the plot adversarially, plot
distributions not just summaries, and never let a pretty default hide a bimodality.

## ⚠️ Read before you rely on it (honest dependency posture)

anyplot is a **third-party resource**, not a RavenClaude artifact:

- **Solo-operator, small project.** One maintainer (Markus Neusinger), hosted on Cloud
  Run + Cloudflare, ~25 GitHub stars as of 2026-10. Treat availability as best-effort —
  **have a non-anyplot fallback** (the library's own gallery/docs) for anything load-bearing.
- **Content is MIT-licensed** (source: [github.com/MarkusNeusinger/anyplot](https://github.com/MarkusNeusinger/anyplot)),
  so you may reuse the snippets — keep the attribution the licence requires.
- **The code is AI-generated and AI-reviewed.** The quality score is a signal, not a
  guarantee. **Run it, read it, and confirm it does what you asked** before it lands in a
  notebook or a report. This is exactly the "read plots adversarially" rule from
  [`../eda-workflow/SKILL.md`](../eda-workflow/SKILL.md), applied to the code that drew the plot.
- This skill does **not** install anything, ship a hook, or make a network call on your
  behalf. You run the fetch when you choose to. `[verified 2026-10-19: API facts from anyplot.ai/llms.txt; project facts from the public repo README]`

## Default path — the public read-only HTTP API

No auth, no key, read-only. Base URL `https://api.anyplot.ai` (OpenAPI at
`https://api.anyplot.ai/openapi.json`; an `llms.txt` / `llms-full.txt` index exists at
the site root).

| Need | Endpoint |
|---|---|
| List every spec + metadata | `GET /specs` |
| One spec with all implementations | `GET /specs/{spec_id}` |
| Runnable source for one library | `GET /specs/{spec_id}/{library}/code` |
| Filter rendered implementations | `GET /plots/filter?plot=&lib=&lang=&...` |
| List supported libraries | `GET /libraries` |

```bash
# Discover: which libraries are covered?
curl -s https://api.anyplot.ai/libraries

# Find a spec, then pull the seaborn implementation for it
curl -s "https://api.anyplot.ai/plots/filter?lib=seaborn&plot=ridgeline"
curl -s https://api.anyplot.ai/specs/<spec_id>/seaborn/code
```

Prefer this path: it is the lowest-trust surface (read-only, you control each call) and
needs nothing installed.

## Opt-in path — the MCP server (only if you want in-agent lookups)

anyplot also exposes a **read-only Streamable-HTTP MCP server** at
`https://api.anyplot.ai/mcp/` (no auth). Adding it is a **deliberate, opt-in** choice —
it wires a remote third-party server into your agent session, so the dependency-posture
note above applies in full. This skill deliberately does **not** ship an `mcpServers`
entry in any plugin manifest, so no consumer gets it silently.

```bash
# You choose to add it; nothing adds it for you.
claude mcp add --transport http anyplot https://api.anyplot.ai/mcp/
```

Tools exposed (per anyplot's docs): `list_specs`, `search_specs_by_tags`,
`get_spec_detail`, `get_implementation`, `list_libraries`, `get_tag_values`. All
read-only.

To remove it again: `claude mcp remove anyplot`.

## When to use / not use

- **Use** when you know *what* to plot and want a correct first implementation in a
  specific library, or when comparing how a chart looks across libraries.
- **Don't use** it to decide *whether* a chart is the right one — that is the
  `eda-workflow` judgement (match the plot to the question; plot distributions, not just
  summary statistics).
- For **authoring and linting a Vega-Lite / Vega / SVG spec** (not looking one up),
  reach for `ravenclaude-core`'s
  [`declarative-visualization`](../../../ravenclaude-core/skills/declarative-visualization/SKILL.md)
  skill instead — that is spec *authoring* with a security linter, a different job.

## Output contract

When you use a fetched recipe, record in the EDA notes: the `spec_id` and library used,
the anyplot quality score, the one-line "I verified it renders and does X" check, and
the MIT attribution. That keeps the provenance auditable and the
`reproducible-research` spine intact.
