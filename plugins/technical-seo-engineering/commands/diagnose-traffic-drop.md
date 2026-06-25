---
description: "Triage an organic-traffic or indexation drop by isolating the layer first — crawl, render, index, or rank — using Search Console coverage + the server log before proposing any fix."
argument-hint: "[what dropped + when it started + which URLs/sections + access to Search Console/logs?]"
---

You are running `/technical-seo-engineering:diagnose-traffic-drop`. Use `technical-seo-lead` + the `diagnose-indexation-drop` skill (pulling in `crawl-indexation-engineer` if it lands at the crawl/render/index layer).

## Steps
1. Scope the drop: which URLs/sections, when it started, how much. Sharp cliff = mechanical (deploy/robots/redirect); slow slide = rank/content.
2. **Crawl layer:** robots.txt change, HTTP status (new 404s/5xx/redirects), and whether the bot is hitting the URLs in the server log.
3. **Render layer:** fetch the RENDERED HTML (not view-source) — CSR move / hydration error / soft 404 hiding content?
4. **Index layer:** Search Console coverage + URL Inspection — excluded? wrong chosen canonical? a stray `noindex`?
5. **Rank layer:** only after ruling out 1–4 — a ranking/algorithm/competition change (partly a `marketing-operations` content seam).
6. Name the layer + the evidence, then fix at that layer. Emit the diagnosis + the targeted fix + the Structured Output block. Traverse the crawl-vs-index tree in `knowledge/technical-seo-engineering-decision-trees.md`.
