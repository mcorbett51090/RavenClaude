# Dashboard architecture/story/guidance audit — {{dashboard name}}

**Date:** {{YYYY-MM-DD}} · **Audited by:** `dashboard-architecture-audit` (invoked via
{{dashboard-builder build gate | standalone hardening request}}
**Pages/views enumerated:** {{N}} — {{list route/page names or URLs; if this is a subset of a
larger site, say so explicitly rather than implying full coverage}}

## Executive summary

{{2-4 sentences: does this dashboard tell a coherent story and guide the user, or is it a grid
of technically-correct-but-disconnected widgets? Name the single biggest structural problem if
there is one.}}

## Priority summary

| Priority | Count | Meaning |
|---|---|---|
| P0 | {{n}} | Breaks the dashboard's core job — the user can't find or act on the key information |
| P1 | {{n}} | Significant structure/narrative/guidance gap |
| P2 | {{n}} | Worth fixing |
| P3 | {{n}} | Polish |

## Cross-page coherence (dashboard-level, not per-page)

- **Overall arc:** {{is there a sensible overview -> segment -> detail progression across pages,
  or does each page stand alone with no relationship to the others?}}
- **Navigation discoverability:** {{can a user find the relevant detail page from the overview
  without already knowing the site?}}
- **Continuity:** {{do filters/timeframe/context carry through when drilling from one page to
  another, or does the story reset at every click?}}

## Per-page findings

### {{page/route name}}

**Structure / information architecture**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| {{P0-P3}} | {{one-sentence finding}} | {{specific widget/region/route cited}} | {{concrete, actionable fix}} |

**Narrative / storytelling**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|
| | | | |

**User guidance / process orientation**

| Priority | Finding | Evidence | Fix |
|---|---|---|---|

*(Repeat the three tables per page.)*

## Out-of-lane findings (named, not re-scored here)

| Finding | Lane | Route to |
|---|---|---|
| {{e.g. "KPI card text fails WCAG AA contrast"}} | {{accessibility}} | {{owning skill/agent}} |

## Fixes applied this session (Last-Mile — automatable ones, not just a list)

| Finding | What was done |
|---|---|
| | |

## Fixes NOT applied (and why)

| Finding | Why deferred |
|---|---|
| {{e.g. "requires a real product decision — which metric should be the dominant KPI on this page"}} | {{owner input needed / out of this session's access / etc.}} |
