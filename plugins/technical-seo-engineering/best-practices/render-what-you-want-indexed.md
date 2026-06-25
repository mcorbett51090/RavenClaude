# Render what you want indexed — verify the rendered HTML, not view-source

**Status:** Absolute rule
**Domain:** JavaScript SEO & rendering
**Applies to:** `technical-seo-engineering`

---

## Why this exists

Search engines crawl HTML, then render JavaScript in a **separate, resource-budgeted pass**. Content and links that exist only after client-side hydration may be indexed late, partially, or not at all — and a hydration error can leave the indexer seeing an empty shell. "It looks fine in my browser" proves nothing: your browser runs the JS eagerly; the indexer may not. The thing that decides what gets indexed is the **rendered HTML the engine produces**, which you must inspect directly (URL Inspection's rendered HTML / a rendering crawler) — **not** the `view-source` payload and **not** your live browser.

A related failure is the **soft 404**: a page that returns HTTP 200 but whose rendered body says "not found"/"no results." The engine may index it as a thin/duplicate page or waste budget on it. Return a real **404 or 410**.

## How to apply

**Do:**
- Put the content and internal links you want indexed in the **initial HTML response** — prefer **SSR** or **SSG** (or pre-rendering). Use **dynamic rendering** only as a stopgap.
- Verify the **rendered** HTML (URL Inspection / rendering crawler) contains the title, body, and links — before assuming a page is indexable.
- Return a real **404/410** for not-found states; never a 200 with "no results."
- Keep the CSS/JS needed to render **unblocked** in robots.txt.

**Don't:**
- Trust `view-source` or your eager browser to represent what the indexer sees.
- Ship critical content/links that only appear after a client-side fetch on a CSR-only page.
- Serve a 200 for a missing resource (soft 404).

## Edge cases / when the rule does NOT apply

- **Logged-in / personalized content** isn't meant to be indexed — CSR is fine there.
- **Progressive enhancement** where the SSR baseline already contains the indexable content and JS only enriches it is exactly right.

## See also

- [`../knowledge/technical-seo-engineering-reference-2026.md`](../knowledge/technical-seo-engineering-reference-2026.md) — Googlebot rendering behavior (re-verify).
- [`../skills/diagnose-indexation-drop/SKILL.md`](../skills/diagnose-indexation-drop/SKILL.md) — the render layer of the drop triage.

## Provenance

Codifies the house opinion "render what you want indexed; if it's not in the rendered HTML, assume it doesn't exist for the indexer." The advisory hook flags a likely soft-404 (HTTP 200 returned next to "not found" text in the same file). Grounded in Google Search Central JavaScript-SEO documentation, retrieved 2026-06-25 — re-verify before quoting.

---

_Last reviewed: 2026-06-25 by `claude`_
