---
name: diagnose-indexation-drop
description: "Triage a drop in organic traffic or indexed pages by isolating the layer FIRST — crawl (can the bot fetch it?), render (is the content in the rendered HTML?), index (is it indexed and canonicalized right?), or rank (a ranking/algorithm change) — using Search Console coverage + the server log before proposing any fix. Reach for this when organic traffic or index coverage drops. Used by `technical-seo-lead` + `crawl-indexation-engineer`."
---

# Skill: diagnose-indexation-drop

> **Invoked by:** `technical-seo-lead` (primary) and `crawl-indexation-engineer`.
>
> **When to invoke:** "organic traffic dropped"; "pages fell out of the index"; "Search Console coverage shows fewer indexed URLs."
>
> **Output:** a layer-isolated diagnosis (crawl / render / index / rank) with the evidence behind it and the targeted fix — never a guess.

## Procedure (isolate the layer before fixing)

1. **Scope the drop.** Which URLs/sections, when did it start, how much? A sharp cliff suggests a mechanical change (deploy, robots, redirect); a slow slide suggests rank/algorithm or content decay.
2. **Crawl layer — can the bot fetch it?** Check robots.txt (a new `Disallow`?), HTTP status (new 404s/5xx/redirects?), and the server log for whether the bot is even hitting the URLs. A deploy that changed robots.txt or returned 5xx is the classic mechanical cause.
3. **Render layer — is the content in the rendered HTML?** Fetch the rendered HTML (not view-source). A move to client-side rendering, a hydration error, or a soft 404 (200 status, "not found" body) can hide content from the indexer.
4. **Index layer — is it indexed and canonicalized right?** In Search Console coverage/URL Inspection: is the page excluded? Is Google's *chosen* canonical the one you declared? A wrong `noindex`, a bad canonical, or duplicate-content consolidation deindexes pages.
5. **Rank layer — only after ruling out 1–4.** If the pages are crawled, rendered, and indexed but ranking dropped, it's a ranking/algorithm/competition change — a different problem (and partly a content/`marketing-operations` seam).
6. **Name the layer + evidence, then fix at that layer.** Most "SEO drops" are misdiagnosed at the wrong layer; the evidence (log + Search Console) decides.

## Worked example

> User: "We deployed Friday and indexed pages dropped 40% by Monday."

- Sharp cliff right after a deploy → mechanical. Check robots.txt first → the deploy shipped a staging `Disallow: /` that wasn't removed.
- Evidence: log shows Googlebot fetched robots.txt and stopped crawling; Search Console coverage shows "Blocked by robots.txt" climbing.
- Fix: restore the production robots.txt, request validation, resubmit the sitemap. (Layer = crawl, not rank — no content change needed.)

## Guardrails

- Never jump to "it's a ranking/algorithm change" before ruling out crawl, render, and index — that's the layer people skip to and it's usually wrong. (Traverse [`../../knowledge/technical-seo-engineering-decision-trees.md`](../../knowledge/technical-seo-engineering-decision-trees.md).)
- Never trust a rank tracker as the primary signal — Search Console coverage + the server log are the ground truth for what the bot did.
- Confirm Google's chosen canonical via URL Inspection, not the one you declared — they can differ.
