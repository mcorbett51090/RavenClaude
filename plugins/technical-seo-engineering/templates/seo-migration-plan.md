# SEO migration plan — <old site/domain → new site/domain>

> The plan for the highest-risk SEO event: a replatform, redesign, domain change,
> or URL-structure change. The order matters: **inventory → map redirects →
> preserve signals → stage safely → launch → verify → root-cause any drop.**
> A migration lives or dies on the **redirect map** and **staging-noindex** — do
> not skip to "flip it live and watch." Pairs with the
> [`technical-seo-audit-report.md`](technical-seo-audit-report.md).

**Migration ID:** <YYYY-MM-DD-nn> · **Type:** <replatform / redesign / domain change / HTTP→HTTPS / URL restructure> · **Owner / lead:** <name> · **Planned go-live:** <date> · **Status:** planning / staged / launched / verified

## 1. Scope & baseline (capture BEFORE anything changes)
- **What's changing:** <platform / domain / URL structure / templates>
- **Baseline snapshot:** <GSC impressions/clicks/coverage · top organic URLs by traffic · current rankings for target queries — dated, so you can detect a drop>
- **Full URL inventory:** <crawl of the old site + GSC/analytics top URLs + XML sitemaps + backlink-target URLs — the union, so nothing with equity is missed>

## 2. Redirect map (the make-or-break artifact)
- **Every old URL with equity → its closest new equivalent**, **single-hop**, status **301** (permanent).
- **No blanket redirect-to-homepage** for content pages — that destroys the equity; map to the true equivalent or the nearest relevant page.
- **Collapse chains:** old → new directly, never old → interim → new.

| Old URL | New URL | Redirect type | Note |
|---|---|---|---|
| <old/path> | <new/path> | 301 | <1:1 equivalent> |
| <retired/path> | <nearest relevant> | 301 | <no 1:1 — nearest match, not homepage> |
| <kept/path> | <same> | none | <unchanged> |

- **Coverage check:** <every inventoried URL from §1 appears here or is intentionally 410'd — no orphans>

## 3. Preserve the signals
- **Canonicals:** <one per new page, self-referencing — preserved/updated>
- **hreflang:** <bidirectional, self-referencing, x-default preserved for international>
- **Structured data:** <JSON-LD types carried over + validated on new templates>
- **Internal linking + IA:** <hub-and-spoke structure preserved; no new orphans; nav updated to new URLs>
- **XML sitemaps:** <new sitemaps built (canonical/indexable/200 only); old sitemap kept briefly to speed re-crawl of redirects>

## 4. Stage safely (the second make-or-break)
- **Staging behind noindex + auth:** <staging/dev is NOT crawlable or indexable — a duplicate of production competing with it is a classic self-inflicted drop>
- **Pre-launch QA on staging:** <redirects resolve single-hop · rendering serves crawler-visible content · schema validates · CWV acceptable>
- **Remove the noindex/robots-block ONLY at go-live** — never before, never forgotten after.

## 5. Launch
- **Go-live steps + order:** <DNS/deploy · enable redirects · remove staging noindex · submit new sitemaps>
- **Search Console:** <verify both old + new properties · submit new sitemaps · use Change of Address for a domain move>
- **Bing Webmaster / IndexNow:** <equivalent submission + site-move tool>

## 6. Post-launch verification (do NOT "wait and see")
- [ ] Redirects resolve **single-hop 301** across a sample of the map (and all top-traffic URLs)
- [ ] New URLs **indexing** in GSC (Pages/Coverage trending up; redirects being processed)
- [ ] Staging is **not** indexed (site: check; no duplicate competing)
- [ ] Canonicals / hreflang / structured data **valid** on new templates (URL Inspection + Rich Results Test)
- [ ] Core Web Vitals **not regressed** on CrUX field data
- [ ] Rankings + organic traffic tracked vs the §1 baseline

## 7. Root-cause any drop — to the CHANGE, not the symptom
A post-migration drop traces to a specific change; name which:
- [ ] **Missing / wrong redirect** — a top URL 404s or chains? <check the map coverage>
- [ ] **Indexed staging** — a duplicate competing with production? <site: check>
- [ ] **Lost signal** — a canonical / hreflang / schema / internal link dropped in the move? <diff old vs new>
- [ ] **Rendering regression** — new templates ship an empty DOM to crawlers? <URL Inspection>
- **Root cause (the change):** <the specific change + evidence>
- **Correction:** <add the redirect · noindex+de-index staging · restore the signal · fix rendering — then re-verify>

## Seams (not this team)
- **The full website build / visual design:** web-design (this plan is the SEO requirements the build must honor)
- **Deep front-end performance beyond CWV:** performance-engineering
- **Analytics/event re-instrumentation across the migration:** martech-event-instrumentation
- **Multi-week migration RAID / status:** ravenclaude-core/project-manager

**Closed / verified at:** <timestamp> · **Signed off:** <name>
