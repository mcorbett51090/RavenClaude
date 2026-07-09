# Technical-SEO audit report — <site / property>

> The one-page audit captured **before** prescribing fixes. Walks the
> **crawl → render → index → understand → rank** ladder and fixes the lowest
> broken rung first. Pairs with [`seo-migration-plan.md`](seo-migration-plan.md)
> when the fix is a replatform/domain change. Volatile facts (algorithm signals,
> SERP features, rich-result eligibility, tool pricing) carry a **retrieval date**.

**Auditor:** <name> · **Date:** <YYYY-MM-DD> · **Property:** <domain + GSC/Bing property> · **Stack / rendering:** <CMS/framework · CSR/SSR/SSG> · **Site size:** <~URL count> · **Status:** draft / reviewed / delivered

## Context & targets
- **Business goal / target queries & intents:** <what must rank & convert, at what intent>
- **Current organic performance:** <GSC impressions/clicks/coverage · the trend · any drop + when>
- **The pain in plain terms:** <not indexed / not ranking / traffic dropped / new site / migration>

## The ladder — diagnosis (lowest broken rung first)
| Rung | Finding | Evidence (tool) | Severity | Binding? |
|---|---|---|---|---|
| **Crawl** | <robots.txt / sitemaps / crawl-budget leaks> | <log-file read · GSC Crawl stats> | <high/med/low> | <yes/no> |
| **Render** | <CSR empty DOM? SSR/SSG?> | <URL Inspection "view crawled page"> | | |
| **Index** | <right pages in? over-indexing? canonical/noindex errors> | <GSC Pages/Coverage · site: checks> | | |
| **Understand** | <IA depth · orphans · internal linking · entities · schema> | <crawl · Rich Results Test> | | |
| **Rank** | <E-E-A-T / helpful-content / topical depth vs SERP · CWV> | <SERP review · CrUX> | | |

**Binding constraint (fix first):** <the lowest broken rung + why>

## Crawlability
- **robots.txt:** <what's allowed/blocked · any key path wrongly blocked>
- **XML sitemaps:** <clean? canonical/indexable/200 only? stale entries?>
- **Log-file finding:** <what Googlebot actually crawls · budget leaks (facet/param/soft-404/redirect chains)>

## Rendering
- **Mode per page class:** <CSR / SSR / SSG / prerender>
- **Crawler sees content?** <URL Inspection rendered-DOM result — content present or empty shell>
- **Dynamic rendering in use?** <if yes: flag as deprecated, plan SSR/SSG migration>

## Indexation controls
- **Canonicalization:** <one per page? self-referencing? bad canonicals?>
- **Meta-robots / noindex:** <de-index handled correctly — noindex + crawlable, NOT blocked>
- **Indexation strategy per page class:** <index / canonicalize / noindex / block — table below>

| Page class | Index / canonicalize / noindex / block | Reason (crawl budget / duplicate / thin) |
|---|---|---|
| <product> | index | unique money page |
| <faceted filter> | block or noindex | crawl trap / duplicate |
| <internal search> | noindex | no search value |
| <pagination> | <index / canonical to view-all> | |

- **International / hreflang:** <bidirectional? self-referencing? x-default? correct codes? pointing at canonical URLs?>

## Understanding — architecture, entities, structured data
- **IA & internal linking:** <depth · hub-and-spoke clusters · orphans · authority flow to money pages>
- **Topical-authority / entity map:** <what the site should own · thin/overlapping pages to consolidate>
- **Structured data:** <JSON-LD types present · Rich Results Test status · matches visible content? · eligibility (NOT guarantee) · retrieval date>

## Rank — quality & performance signals
- **E-E-A-T / helpful-content posture:** <people-first? experience/author/entity signals? intent coverage vs SERP>
- **Core Web Vitals (field / CrUX):** <INP · LCP · CLS at p75 — good/needs-improvement/poor> _(INP replaced FID in 2024; CWV is a tiebreaker, not the whole game)_

## Prioritized fix plan
| # | Fix | Rung | Owner | Effort | Impact | Verify with |
|---|---|---|---|---|---|---|
| 1 | <lowest-broken-rung fix> | <rung> | <who> | <S/M/L> | <H/M/L> | <GSC / URL Inspection / RRT / logs> |
| 2 | | | | | | |

## Seams (not this team)
- **Internal site-search relevance:** search-relevance-engineering
- **The full website build / visual design:** web-design
- **Paid ads / campaign strategy:** marketing-operations
- **Writing the content:** technical-writing-docs
- **Deep front-end performance beyond CWV:** performance-engineering

## Volatile claims to re-verify before client sign-off
- <algorithm-signal / SERP-feature / rich-result-eligibility / tool-pricing claim + retrieval date> → `ravenclaude-core/deep-researcher`

**Sign-off:** <reviewer> · <date>
