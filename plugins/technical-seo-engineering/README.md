# technical-seo-engineering

> The **organic-search-engineering layer** for Claude Code — the team that answers *"can search engines crawl, render, index, and understand this site, and will it rank?"* and builds the crawlability, rendering, indexation, structured data, and migrations that make the answer yes. Two agents: the **seo-strategy-architect** (decides strategy, priorities, IA, and the content model) and the **seo-implementation-engineer** (implements and verifies the technical layer).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Our organic traffic is flat — where do we start?" | A binding-rung diagnosis walking crawl → render → index → understand → rank, fixing the lowest broken rung first, with the facts that would reorder it |
| "How should we structure the site and internal links?" | A flat, hub-and-spoke IA + internal-linking model + a topical-authority / entity map — the content model the engineer builds to |
| "Which pages should we index, canonicalize, or noindex?" | An indexation strategy per page class with crawl-budget + duplicate-content reasoning |
| "Our React SPA doesn't rank — is it rendering?" | A rendering decision & implementation (CSR → SSR/SSG/prerender), verified in URL Inspection so the crawler sees the content |
| "Add schema markup so we get rich results." | Valid JSON-LD schema.org for the eligible types, validated in the Rich Results Test — eligibility stated, not a guarantee, and retrieval-dated |
| "We're replatforming — don't tank our SEO." | A migration run to plan: 301 redirect map, staging behind noindex, preserved canonicals/hreflang, GSC handled, post-launch verified |

**Two rules it never breaks:** *fix the lowest broken rung first* (a page can't rank if it can't be understood, indexed, rendered, or crawled), and *verify each rung with the actual tool — logs, URL Inspection, the Rich Results Test, CrUX — don't assume Google "handles it."*

## What's inside

- **2 agents** — `seo-strategy-architect` (decides the priority diagnosis, IA + internal-linking model, content/entity model, indexation strategy, and E-E-A-T posture) and `seo-implementation-engineer` (implements + verifies crawlability, rendering, indexation controls, JSON-LD structured data, Core Web Vitals, and site migrations).
- **3 skills** — `choose-seo-strategy-and-priorities`, `design-site-architecture-and-content-model`, `implement-technical-seo-and-structured-data`.
- **2 knowledge files** — a Mermaid crawl→render→index→understand→rank strategy decision tree (+ five-rung trade-off table + "what should we index" sub-choice) and a 2026 technical-SEO-patterns reference (crawl budget & logs, rendering, indexation mechanics, structured data, Core Web Vitals/INP, hreflang, migrations, tooling map).
- **2 templates** — a technical-SEO audit report and an SEO migration plan.

## Where it sits in the search stack

```
web-design                  →  build the website / visual design      ("make the site exist & look right")
technical-writing-docs      →  write the content                      ("the words on the page")
technical-seo-engineering (HERE)  →  CRAWL / RENDER / INDEX / UNDERSTAND / RANK in Google/Bing  ("can search engines use it & will it rank")
search-relevance-engineering →  relevance INSIDE the site's search box ("ranking within our own search")
marketing-operations        →  paid ads / campaign strategy           ("buying reach — organic's paid sibling")
```

This plugin is the **organic-search-engineering layer**: it makes the site `web-design` builds and `technical-writing-docs` fills discoverable and rank-worthy in Google/Bing, and stays clear of *internal* site-search relevance (`search-relevance-engineering`), the visual build (`web-design`), and paid campaigns (`marketing-operations`).

## Tooling stance

Concept-first (the crawl→render→index→understand→rank ladder, robots-vs-noindex, canonicalization, rendering modes, structured-data eligibility, block-vs-warn indexation, topical authority, Core Web Vitals as a tiebreaker), fluent across **Google Search Console**, **Bing Webmaster Tools / IndexNow**, the **Rich Results Test**, **PageSpeed Insights / CrUX**, **Lighthouse**, crawlers/log-analyzers (**Screaming Frog, Sitebulb, JetOctopus / Botify / Lumar**), and the visibility suites (**Ahrefs, Semrush, Sistrix, Moz**). Google algorithm signals, SERP features, rich-result eligibility, and tool pricing carry retrieval dates — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install technical-seo-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
