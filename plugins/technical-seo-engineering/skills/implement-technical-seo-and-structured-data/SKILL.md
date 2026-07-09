---
name: implement-technical-seo-and-structured-data
description: Implement and verify the technical-SEO layer for a site — crawlability (robots.txt, XML sitemaps, log-file analysis), rendering (CSR→SSR/SSG/prerender), indexation controls (canonical, meta-robots noindex, hreflang), JSON-LD schema.org structured data for rich-result eligibility, Core Web Vitals (INP/LCP/CLS on field data), and redirect-mapped site migrations — each checked against GSC / URL Inspection / the Rich Results Test / server logs. Reach for this when the user asks "fix our crawl/index", "our SPA doesn't rank — is it rendering?", "add schema markup", "improve Core Web Vitals", or "run our site migration without losing rankings". Used by `seo-implementation-engineer` (primary).
---

# Skill: implement-technical-seo-and-structured-data

> **Invoked by:** `seo-implementation-engineer` (primary). Also consulted by `seo-strategy-architect` to confirm a strategy is implementable on the site's stack before finalizing it.
>
> **When to invoke:** "Fix our crawl/index"; "our SPA doesn't rank — rendering?"; "add schema markup"; "improve Core Web Vitals / INP"; "run our site migration"; any move from a chosen strategy to shipped, verified technical-SEO changes.
>
> **Output:** implemented crawl/render/index/schema/CWV changes (or a migration run), each **verified** against GSC / URL Inspection / the Rich Results Test / a log-file read — not shipped blind.

## Procedure

1. **Anchor to the strategy + the patterns reference.** Confirm the indexation strategy, rendering constraint, and schema types in scope (from the architect). Read [`../../knowledge/technical-seo-patterns-2026.md`](../../knowledge/technical-seo-patterns-2026.md) for the mechanics. Never implement a tactic the strategy didn't ask for.
2. **Crawlability first — read the logs, don't guess.** Confirm robots.txt allows the key paths; make XML sitemaps list *only* canonical, indexable, 200-status URLs; run a **log-file analysis** (verified-Googlebot access logs) to see what's *actually* crawled and where budget leaks (faceted/parameter URLs, soft-404s, redirect chains). Close the leaks before anything downstream.
3. **Resolve rendering — verify the crawler sees the content.** Choose CSR vs SSR vs SSG/prerender per page class; for anything that must rank, serve rendered HTML (SSR/SSG). **Verify the rendered DOM** in URL Inspection ("view crawled page"). Treat **dynamic rendering as deprecated** — a bridge, not a target.
4. **Set indexation controls precisely.** One canonical per page (self-referencing on the canonical); `noindex` to *remove* a page while keeping it **crawlable** (never robots-disallow a page you're de-indexing — it can't be crawled to see the noindex); bidirectional, self-referencing **hreflang** with `x-default` for international. Get the robots-vs-noindex call explicit.
5. **Author structured data honestly.** Valid **JSON-LD** schema.org for the eligible types, **matching visible content**; validate in the **Rich Results Test** + GSC Enhancements. State **eligibility, not a guarantee**, and retrieval-date the eligibility rules.
6. **Move Core Web Vitals on field data.** Improve **INP** (replaced FID in 2024), **LCP**, **CLS** against **CrUX** field data (75th percentile), not just a lab Lighthouse score; verify in the GSC Core Web Vitals report. Remember CWV is a tiebreaker, not the whole game.
7. **Migrations: to the plan, verified.** For a replatform/domain/URL change, follow [`../../templates/seo-migration-plan.md`](../../templates/seo-migration-plan.md): a complete single-hop **301 redirect map**, **staging behind noindex + auth**, preserved canonicals/hreflang/structured data, submitted sitemaps + GSC Change of Address, and a **post-launch crawl/index verification** — root-cause any drop to the change.

## Worked example

> User: "Our Next.js blog gets FAQ schema warnings in Search Console and our INP is 'poor' on mobile. Fix both."

- **Structured data:** open the GSC Enhancements FAQ report; the warning is likely markup not matching visible on-page FAQs (or FAQ rich-result eligibility having been reduced — re-verify current eligibility, retrieval-dated). Fix: ensure the JSON-LD `FAQPage` questions/answers *exactly* match the visible accordion content; re-validate in the Rich Results Test. State eligibility, not a guaranteed rich result.
- **INP:** pull the CrUX field INP for the affected templates (not a one-off Lighthouse run). Common causes: heavy hydration/long tasks blocking the main thread. Fix: reduce/defer non-critical JS, break up long tasks, ensure interaction handlers are light; re-measure INP on CrUX after real traffic accrues.
- **Verify:** GSC Enhancements shows the FAQ items valid; GSC Core Web Vitals report shows INP moving toward "good" on field data. Note INP replaced FID (2024) and CWV is a tiebreaker, not the whole ranking story.

## Guardrails

- Verify each rung with the **actual tool** (logs / URL Inspection / Rich Results Test / GSC / CrUX) — never ship blind or assume "Google handles the JS fine."
- **robots-disallow ≠ noindex** — blocking hides from crawling; noindex removes from the index. Don't block a page you're de-indexing.
- A JS SPA must serve crawler-visible content (SSR/SSG/prerender), verified in URL Inspection; dynamic rendering is deprecated.
- Schema markup earns **eligibility**, not a guaranteed rich result, and must match visible content (mismatch = manual-action risk).
- Core Web Vitals is **field data (CrUX/INP)**, a tiebreaker — not a lab Lighthouse vanity score.
- Migrations live or die on the **redirect map + staging-noindex** — a missing 301 or an indexed staging site tanks rankings.
- Volatile facts (rich-result eligibility, algorithm signals, GSC/tool features, pricing) carry a **retrieval date** and are re-verified before shipping to a client. See [`../../knowledge/technical-seo-patterns-2026.md`](../../knowledge/technical-seo-patterns-2026.md).
