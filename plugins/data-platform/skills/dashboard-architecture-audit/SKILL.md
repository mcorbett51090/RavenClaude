---
name: dashboard-architecture-audit
description: Systematically walk a dashboard page by page and judge whether its structure makes sense, whether it tells a coherent story, and whether it guides the user toward action — for a new build's final gate and for hardening/upgrading an existing dashboard. Invoked by `dashboard-builder` (primary) and directly for a standalone hardening request.
---

# Skill: dashboard-architecture-audit

> **Invoked by:** `dashboard-builder` — as the mandatory final gate before declaring any dashboard
> build or upgrade "done" (new AND existing dashboards), and directly when a user asks to
> "harden," "review," or "audit" a dashboard with no new-build framing at all.
>
> **What this owns vs. what it doesn't.** Three previously-uncovered axes: does the dashboard's
> **structure** make sense, does it **tell a story**, does it **guide the user toward action**.
> It does **not** re-litigate what's already owned elsewhere — cite those skills/agents for
> findings in their lane rather than duplicating their rubric:
>
> | Already covered by | Not re-litigated here |
> |---|---|
> | [`../../knowledge/dashboard-visual-craft-2026.md`](../../knowledge/dashboard-visual-craft-2026.md) | Color discipline, whitespace, one-dominant-KPI *rendering* mechanics, chart-type selection at the pixel level |
> | [`dashboard-performance-tuning`](../dashboard-performance-tuning/SKILL.md) | Latency budgets, pre-aggregation, caching |
> | [`../../../ravenclaude-core/knowledge/visual-feedback-loop.md`](../../../ravenclaude-core/knowledge/visual-feedback-loop.md) | Pixel-level correctness, console errors, WCAG contrast/a11y-tooling checks |
> | `ravenclaude-core/security-reviewer` + the JWT/RLS/CSP skills | Auth, tenant isolation, embed security |
>
> **Honest scope boundary, stated up front:** this is a **methodology an agent follows using
> existing tools** (Read/Glob for structural specs, `visual-feedback-loop`'s render-and-see loop
> for rendered pages) — it is **not** a new bespoke crawler/automation tool. Nothing here scripts
> "visit every URL on this domain automatically." The agent enumerates pages deliberately (from
> the app's route files, or from a user-supplied list of URLs) and applies the rubric to each.

## Why this exists

A dashboard can be performant, accessible, and secure, and still fail at its actual job: a grid
of technically-correct widgets that doesn't answer any specific question, doesn't guide the eye
anywhere in particular, and leaves the viewer to do all the interpretation themselves. Nothing
in this plugin's existing skill set audited for that — `dashboard-visual-craft-2026.md` covers
*how a widget should look*, not *whether the page as a whole makes sense*. This skill is that
missing layer, and per the build request that created it: it is meant to be **the gate a new
build must pass before it's called done, and the first step of hardening an existing one** —
not a one-off nice-to-have.

## The three dimensions

Score each page against all three. Cite **specific evidence** (a widget name, a screenshot
region, a route) for every finding — a score with no evidence is not a finding, it's an opinion.

### 1. Structure / information architecture

- **Primary-KPI discipline.** Is there one dominant metric the eye lands on first, or does the
  page have no visual entry point (everything the same size/weight)?
- **Grouping.** Are related widgets spatially clustered (all revenue metrics together, all
  engagement metrics together), or scattered by arbitrary grid position?
- **Depth ladder.** Does the page offer summary → detail progression (KPI tile → trend →
  breakdown table), or is everything flat with no differentiation between headline and detail?
- **Widget-count sanity.** Overloaded (>12–15 widgets, no grouping — a cognitive-load red flag)
  or sparse (a single number on an otherwise-empty screen, wasting the page)?
- **Chart-type consistency.** Does the same *kind* of metric always render the same way across
  the dashboard (a revenue trend shouldn't be a bar chart on one page and a line chart on
  another with no reason)?
- **Navigable structure.** Can a user get from an overview to the relevant detail page in a
  predictable way (consistent nav, breadcrumbs, or a logical tab/route structure)?

### 2. Narrative / storytelling

- **Answers a specific question.** Does each page/section answer something implied by its own
  title, or is it "here's some data" with no framing?
- **Reading order.** Does the layout guide the eye in the order the data should actually be
  interpreted (headline → detail, not a random grid)?
- **Comparison context.** Do metrics show a baseline (period-over-period, target-vs-actual,
  cohort) — per data-platform CLAUDE.md §3 #7 ("provenance on every claim") — or are they bare,
  context-free numbers?
- **Explains the "why."** Where a metric moved significantly, is there an annotation, caption,
  or linked event explaining it, or is the viewer left to guess?
- **Cross-page continuity.** Does drilling from a summary into a detail page preserve context
  (same filters/timeframe carried through), or does the story reset at every navigation?

### 3. User guidance / process orientation

- **Actionability.** Does a concerning number come with a next step (a link, a filter, a named
  action), or does it just sit there?
- **Status signaling.** Are alerts/thresholds distinguished by *status-only* color (per
  `dashboard-visual-craft-2026.md`), so a user can scan for problems at a glance — not decorative
  color that competes with it?
- **Decision-reduction.** Does the dashboard do the significance/threshold judgment for the user
  ("3 accounts at risk"), or dump raw numbers and expect the viewer to compute it themselves?
- **Workflow alignment.** Does the page order match the actual process the user runs (triage →
  investigate → resolve, for example), or does it follow database-table order instead?
- **Empty/zero states.** Does an empty or zero-data state explain what's missing and what to do
  about it, rather than rendering a blank or broken-looking widget?

## Procedure

1. **Enumerate pages/views.** For a new build: `Glob` the app's route/page files (or ask
   `dashboard-builder` which views exist). For an existing/live dashboard being hardened: ask
   the user for the URL(s), or `Glob`/`Grep` the repo if it's local.
2. **Per page, "see" it** — reuse [`visual-feedback-loop`](../../../ravenclaude-core/skills/visual-feedback-loop/SKILL.md)'s
   existing render-and-see mechanism: a screenshot via `chrome-devtools-mcp` when installed, or a
   structural layout read as the documented fallback when it isn't. Do not build a second
   screenshot mechanism — this skill consumes that one.
3. **Score all three dimensions per page**, citing specific evidence per finding.
4. **Assess cross-page coherence** once, at the dashboard level, not per page: is there a
   sensible overall arc (overview → segment → account-level, for example), and is navigation
   between pages discoverable? A dashboard can pass every individual page's rubric and still fail
   here if the pages don't cohere into one product.
5. **Route out-of-lane findings.** A contrast issue, a slow widget, a missing `access_policy` —
   name it, cite the owning skill/agent from the table above, and don't re-score it here.
6. **Write the report** using [`../../templates/dashboard-audit-report-template.md`](../../templates/dashboard-audit-report-template.md) —
   priority-tagged (P0–P3, matching this marketplace's `/repo-review` convention: P0 = breaks the
   dashboard's core job, P1 = significant IA/narrative/guidance gap, P2 = worth fixing, P3 =
   polish), each finding naming the page, the dimension, the evidence, and a concrete fix.

## Using this as a build gate vs. a standalone audit

- **Build gate (new dashboard):** `dashboard-builder` runs this as the last step before its
  Output Contract can say the build is complete — see that agent's Output Contract, which now
  requires an `Architecture/story/guidance audit:` field. A build with unresolved P0/P1 findings
  is **not** done, regardless of whether it renders correctly and passes the performance/security
  gates.
- **Standalone hardening (existing dashboard):** invoke this skill directly — "harden this
  dashboard," "review this dashboard's structure," "does this dashboard make sense" all route
  here per `dashboard-builder`'s scenario list. No new build is implied; the deliverable is the
  report plus, per the Last-Mile Completion Protocol, as many of the fixes as are automatable
  given the access this session already has (a layout reflow, a missing comparison baseline, a
  reordered nav) — not just a list handed back.

## Anti-patterns this skill flags

- Scoring a page without citing specific evidence (a vague "structure could be better" is not a
  finding)
- Re-scoring a visual-craft, performance, security, or accessibility issue that already has an
  owning skill — name it and route it instead
- Treating "it renders without errors" as equivalent to "it makes sense" — those are different
  questions answered by different tools
- Declaring a dashboard build done with unresolved P0/P1 findings from this audit
- Auditing pages in isolation and never assessing cross-page coherence
- Inventing an automated crawler this skill doesn't have — enumerate pages deliberately, don't
  claim exhaustive site coverage you didn't actually check

## References

- Report template: [`../../templates/dashboard-audit-report-template.md`](../../templates/dashboard-audit-report-template.md)
- Knowledge: [`../../knowledge/dashboard-visual-craft-2026.md`](../../knowledge/dashboard-visual-craft-2026.md)
- Skill: [`dashboard-performance-tuning`](../dashboard-performance-tuning/SKILL.md)
- Canon: [`../../../ravenclaude-core/knowledge/visual-feedback-loop.md`](../../../ravenclaude-core/knowledge/visual-feedback-loop.md)
- Agent: [`../../agents/dashboard-builder.md`](../../agents/dashboard-builder.md) — the primary consumer
