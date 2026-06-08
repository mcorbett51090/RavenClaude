# Changelog — content-and-growth-marketing

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.1.0 — 2026-06-08

Initial release. The content-and-growth (editorial / SEO / lifecycle) layer above the marketing-site,
experimentation, and data-platform cluster.

- **3 agents** — `content-strategist` (audience + jobs, topic clusters / pillar pages, editorial calendar,
  content briefs, distribution + repurposing), `seo-program-lead` (keyword + search-intent research, technical
  SEO, on-page + internal linking, SERP features, AEO/GEO), `lifecycle-marketing-engineer` (segmentation, triggered
  nurture flows, deliverability, marketing automation, the demand-gen funnel). Each carries the full
  scenario-authoring frontmatter.
- **3 skills** — `content-strategy-and-briefs`, `seo-program`, `lifecycle-and-email`.
- **Knowledge bank** — `content-and-growth-marketing-decision-trees.md`: Mermaid trees (should-we-publish-this,
  intent-to-surface for classic vs. AEO/GEO, flow-vs-broadcast) + a dated 2026 capability/landscape map
  (CMS / SEO suites / ESP / AEO surfaces) (`[verify-at-build]`).
- **8 best-practices**, **3 commands** (`plan-content`, `audit-seo`, `build-lifecycle-flow`),
  **2 templates** (content brief, lifecycle-flow spec), **1 advisory hook**
  (`check-content-and-growth-marketing-anti-patterns.sh`; `MARKETING_STRICT=1` to make it blocking), and a
  **scenarios bank** (2 field notes).
- Seams: marketing-site build & brand → `web-design`; A/B experiment apparatus → `experimentation-growth-engineering`;
  product/marketing analytics warehouse → `data-platform`; consent/PII → `data-governance-privacy`.
  Requires `ravenclaude-core@>=0.7.0`.
