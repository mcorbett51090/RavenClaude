# Content and Growth Marketing

The **content-and-growth-marketing** plugin — the editorial-strategy, organic-search, and lifecycle-marketing craft: the content-and-growth layer *above* the marketing site, the experiment apparatus, and the analytics warehouse that decides what gets published, how it gets found (classic search *and* answer engines), and how people move through the demand-gen funnel — distinct from the site build, the test engine, and the warehouse themselves.

## Agents

- **`content-strategist`** — The content plan: audience and jobs-to-be-done, topic clusters and pillar pages, the editorial calendar and a sustainable cadence, content briefs a writer can execute, and distribution + repurposing so one asset becomes ten. Builds a strategy that compounds, not a calendar of one-off posts.
- **`seo-program-lead`** — SEO as a program across technical, on-page, content, and answer-engine layers: keyword and search-intent research, crawlability/indexation/site-architecture/Core Web Vitals/structured data, on-page and internal-linking topology, SERP features, and AEO/GEO (answer/generative-engine optimization for AI Overviews and LLM answers).
- **`lifecycle-marketing-engineer`** — Email and lifecycle marketing as a system: segmentation, triggered nurture flows (welcome / onboarding / abandonment / win-back), deliverability (SPF/DKIM/DMARC, list hygiene, sender reputation), marketing automation, and the demand-gen funnel — measured on conversion and engaged-list health, never vanity opens.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install content-and-growth-marketing@ravenclaude
```

## Seams

- **The marketing-site build, page templates, brand/visual system, render strategy, Core Web Vitals engineering** → `web-design`; this team specifies the content + SEO requirements, they build the pages.
- **The A/B / multivariate test engine and the statistics** → `experimentation-growth-engineering`; we propose what to test (headlines, CTAs, subject lines, flows), they own the experiment.
- **The marketing/analytics warehouse, attribution modeling, the organic-traffic + funnel pipelines** → `data-platform`; we name the metrics that matter, they build the pipeline.
- **Long-form documentation quality and information architecture** → `technical-writing-docs`; we own marketing/editorial content and its distribution.
- **Consent, PII handling, list-data retention, and the privacy posture of capture/tracking** → `security-engineering` + `data-governance-privacy`; we encode their policy into capture and lifecycle.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `web-design`, `experimentation-growth-engineering`, and `data-platform`.
