---
name: choose-seo-strategy-and-priorities
description: Diagnose what to fix first for a described site by walking the SEO strategy decision tree (crawl → render → index → understand → rank), fixing the lowest broken rung first, then return the priority diagnosis, the indexation strategy, the E-E-A-T posture, and the conditions that would reorder the priorities. Reach for this when the user asks "our organic traffic is flat — where do we start?", "what should we fix first for SEO?", "which pages should we index or noindex?", or "how do we rank in a helpful-content world?". Used by `seo-strategy-architect` (primary).
---

# Skill: choose-seo-strategy-and-priorities

> **Invoked by:** `seo-strategy-architect` (primary). Also consulted by `seo-implementation-engineer` when a build reveals the priority was wrong and the strategy needs re-ordering.
>
> **When to invoke:** "Our organic traffic is flat — where do we start?"; "what should we fix first?"; "which pages should we index / canonicalize / noindex?"; "how do we rank this content?"; any "what's the SEO strategy?" question.
>
> **Output:** the priority diagnosis (the binding rung) + the indexation strategy + the E-E-A-T posture + the 1-2 flip conditions that would reorder the priorities.

## Procedure

1. **Restate the situation in the ladder's terms.** Capture: the **site** (stack, rendering mode, size/URL count), the **current organic performance** (GSC impressions/clicks/coverage, the trend), the **target queries & intents** (what must convert), and the **pain** (not indexed / not ranking / traffic dropped / new site).
2. **Walk the ladder, find the lowest broken rung.** Traverse [`../../knowledge/seo-strategy-decision-tree.md`](../../knowledge/seo-strategy-decision-tree.md): **crawl** (robots.txt/sitemaps/log evidence) → **render** (does the crawler see the content) → **index** (right pages in, only right pages) → **understand** (IA, entities, schema) → **rank** (quality signals). A page can't rank if it can't be understood, understood if not indexed, indexed if not rendered, rendered if not crawled — so **fix the lowest broken rung first**.
3. **Prioritize by the binding constraint, not by tactic fashion.** Effort on schema markup while Googlebot is blocked is wasted. Name *which rung is broken* and put that first; sequence the rest behind it.
4. **Set the indexation strategy per page class.** For each template (product, category, faceted filter, pagination, internal search, tag, author), decide **index / canonicalize / noindex / block** — with crawl-budget and duplicate-content reasoning. Most sites index far too much; find the over-indexing.
5. **Set the E-E-A-T + helpful-content posture** where the binding rung is *rank*: people-first content, first-hand experience/expertise signals, author/entity trust, intent coverage — tied to the topical-authority map (hand to [`design-site-architecture-and-content-model`](../design-site-architecture-and-content-model/SKILL.md)), not a keyword-density trick.
6. **State the flip conditions** — the 1-2 facts that, if different, reorder the priorities (e.g., "if the SPA is actually being rendered fine, render drops and content quality becomes the binding rung").
7. **Hand off:** the chosen priorities + indexation strategy go to `seo-implementation-engineer` via [`implement-technical-seo-and-structured-data`](../implement-technical-seo-and-structured-data/SKILL.md).

## Worked example

> User: "We launched a React storefront 4 months ago. Google indexed the homepage but almost none of our 8,000 product pages. Where do we start?"

- Symptom is at the **render/index** rungs, not rank — so **don't** start with schema or link-building.
- **Diagnose render first:** a CSR SPA that ships an empty DOM means Googlebot sees no product content on the second-pass render → the binding rung is **render**. Verify with URL Inspection "view crawled page" on a product URL.
- **Priority order:** (1) fix rendering — SSR/SSG the product pages so content is in the first HTML response; (2) then indexation — canonical per product, clean XML sitemap of the 8,000 canonical product URLs, noindex the faceted-filter combinations; (3) *then* understanding — Product JSON-LD + internal linking; (4) rank/E-E-A-T last.
- **Indexation strategy:** products → index; facet/sort/parameter URLs → block or noindex; internal search results → noindex.
- **Flip condition:** if URL Inspection shows the product content *is* rendered and indexed, render/index aren't the constraint — re-diagnose at understand/rank (thin content, no topical authority).

## Guardrails

- Never prescribe a tactic before walking the ladder — diagnose the binding rung first.
- Fix the **lowest** broken rung first; higher-rung effort is wasted while a lower rung is broken.
- Index **less, not more** — hunt the over-indexed faceted/duplicate/thin URLs before adding pages.
- E-E-A-T is people-first content with real experience signals, not a keyword-density checklist.
- Internal site-search relevance is **not** technical SEO → route to `search-relevance-engineering`; paid → `marketing-operations`; the visual build → `web-design`.
- Volatile claims (Google algorithm signals, SERP features, rich-result eligibility, tool pricing) carry a **retrieval date** and are re-verified before a client commitment. See [`../../knowledge/technical-seo-patterns-2026.md`](../../knowledge/technical-seo-patterns-2026.md).
