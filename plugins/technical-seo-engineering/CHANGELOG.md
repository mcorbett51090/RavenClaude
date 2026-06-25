# Changelog — technical-seo-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-25

Initial release.

### Added

- **3 agents** — `technical-seo-lead` (site-migration redirect strategy, the canonical-vs-noindex-vs-disallow decision, Search Console + log-file measurement, traffic-drop triage, routing), `crawl-indexation-engineer` (robots.txt, XML sitemaps, crawl budget, canonical/pagination/faceted-nav traps, JS rendering — SSR/SSG/dynamic-rendering, soft-404s — and the noindex-vs-disallow distinction), `core-web-vitals-engineer` (LCP/INP/CLS as ranking inputs, field vs lab, and structured data / schema.org rich results).
- **5 skills** — `audit-crawlability`, `plan-site-migration-redirects`, `implement-structured-data`, `diagnose-indexation-drop`, `optimize-core-web-vitals`.
- **Knowledge bank** — `technical-seo-engineering-decision-trees.md` (2 Mermaid trees: crawl-vs-index drop triage, and noindex-vs-disallow-vs-canonical signal selection) and `technical-seo-engineering-reference-2026.md` (dated CWV thresholds, Googlebot rendering behavior, robots/sitemap mechanics, structured-data catalog, and tooling map; re-verify before quoting).
- **9 best-practices** — 7 named rules (noindex-removes-disallow-hides, one-canonical-signal-set, never-block-a-page-you-also-canonicalize, render-what-you-want-indexed, keep-the-sitemap-honest, redirect-map-before-you-migrate, redirects-are-301-and-one-hop) plus 2 companions (measure-core-web-vitals-in-the-field, structured-data-matches-the-page).
- **3 templates** — site-migration-redirect-map, technical-seo-audit-report, structured-data-spec.
- **3 commands** — `/audit-technical-seo`, `/plan-migration`, `/diagnose-traffic-drop`.
- **1 advisory hook** — `flag-seo-smells.sh` (4 checks on `.txt`/`.xml`/`.html`/`.htm`/`.md`: disallow + noindex/canonical contradiction, redirect chain / 302-for-permanent-move, HTTP-200 soft-404, FID-instead-of-INP; `SEO_SMELLS_STRICT=1` to block).

### Verify-at-use

- All numeric thresholds and search-engine behaviors in `technical-seo-engineering-reference-2026.md` (Core Web Vitals thresholds, the FID→INP change, Googlebot two-wave rendering, robots/sitemap limits, the supported structured-data catalog and required properties) — volatile; re-confirm against Google Search Central / web.dev / schema.org before quoting in a client deliverable.
