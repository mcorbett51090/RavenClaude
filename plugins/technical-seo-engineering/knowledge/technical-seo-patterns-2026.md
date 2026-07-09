# Knowledge — Technical-SEO patterns (2026)

> **Last reviewed:** 2026-07-09 · **Confidence:** High on the durable mechanics (the crawl→render→index→understand→rank ladder, robots-vs-noindex, canonicalization, rendering modes, structured-data eligibility, redirect-mapped migrations); **Medium on the dated signal/tooling map — Google's algorithm signals, SERP features, rich-result eligibility, and tool pricing are volatile and carry retrieval dates below.**
> The reference the `seo-implementation-engineer` reads when building and verifying: crawlability, rendering, indexation controls, structured data, Core Web Vitals, international SEO, and migrations — with a 2026 tooling snapshot.

The team's discipline: **verify each rung with the actual tool (server logs / URL Inspection / Rich Results Test / GSC / CrUX), get robots-vs-noindex and rendering right before blaming content, claim structured-data *eligibility* not a guarantee, and root-cause a ranking drop to the CHANGE.**

---

## Crawlability & crawl budget

- **robots.txt** governs *crawling*, not indexing. `Disallow` stops a fetch; it does **not** remove an already-indexed URL (a disallowed URL can still show in results as a bare link). Use it for crawl traps, not de-indexing.
- **XML sitemaps** should list *only* canonical, indexable, 200-status URLs — one clean list of "these are the pages I want indexed." A sitemap full of redirects/404s/noindex URLs erodes trust in the whole file.
- **Crawl budget** is real at **scale** (100k+ URLs, or a site with frequent changes) — Googlebot allocates a finite crawl rate + demand. It is *rarely* the constraint on a small site; don't over-engineer it there. Log-file analysis (server access logs filtered to verified Googlebot) is the ground truth for *what actually gets crawled* and where budget leaks (faceted/parameter URLs, soft-404s, redirect chains, infinite calendars).
- **Highest-leverage crawl fixes:** close facet/parameter crawl traps, collapse redirect chains to a single hop, fix soft-404s, keep the site shallow so money pages are few clicks from the root.

---

## Rendering: CSR vs SSR vs SSG (and why dynamic rendering is out)

| Mode | What the crawler gets | Use when |
|---|---|---|
| **SSR** (server-side render) | Full HTML on first response | Content must rank *and* is dynamic/personalized; the safest default for SEO-critical pages |
| **SSG** (static generation) | Pre-built full HTML | Content is mostly static (docs, marketing, blog); fastest + most crawlable |
| **CSR** (client-side render) | An near-empty shell + JS the crawler must execute later | App-like UIs where the SEO content isn't the point — risky for content that must rank |
| **Prerender / hybrid** | Pre-rendered HTML for bots, hydrated app for users | A bridge for a legacy SPA that can't move to SSR quickly |

- Google renders JS on a **second pass, on a budget and a delay** — CSR content is *eventually* seen, not reliably or promptly. For anything that must rank, **serve rendered HTML** (SSR/SSG). _(Retrieved 2026-07-09.)_
- **Dynamic rendering** (serving a prerendered version to bots) is **deprecated by Google** — treated as a workaround, not a recommended long-term solution; prefer SSR/SSG. _(Retrieved 2026-07-09 — re-verify before quoting.)_
- **Verify, don't assume:** URL Inspection → "View crawled page" / "Test live URL" shows the *rendered* DOM Google actually sees. If your content isn't in it, it doesn't exist for ranking.

---

## Indexation controls — the precise mechanics (get these right)

- **Canonical (`rel=canonical`)** — a *hint* (not a directive) that consolidates duplicate/variant URLs' signals to one preferred URL. One canonical per page; self-reference on the canonical itself. Google may override a bad canonical.
- **Meta robots `noindex`** — a *directive* that **removes** a page from the index. To de-index, the page must stay **crawlable** so Google can *see* the noindex — **do not** also robots-disallow it (a blocked page can't be crawled to read the tag). This robots-vs-noindex confusion is the single most common indexation own-goal.
- **`nofollow`** on links — no longer a strict crawl directive (a hint since 2019/2020); not a reliable crawl-control lever.
- **Pagination** — `rel=next/prev` is no longer used by Google as an indexing signal; treat paginated series as individually indexable (or use a "view-all" canonical) and ensure crawl paths to deep items. _(Retrieved 2026-07-09.)_
- **Parameter handling** — the old Search Console parameter tool is gone; control parameters with canonicals, internal-link discipline, and robots.txt for true traps.

---

## Structured data / schema.org — eligibility, not a guarantee

- Use **JSON-LD** (Google's preferred format) with **schema.org** vocabulary. It makes a page *eligible* for **rich results** — it does **not** guarantee them; Google decides per query. Say "eligible," never "will get."
- **Common rich-result types:** `Product` (+ `Offer`/`AggregateRating`), `Article`/`NewsArticle`, `BreadcrumbList`, `Organization`, `FAQPage` and `HowTo` (note: Google *reduced* FAQ/HowTo rich-result visibility — re-verify current eligibility), `Event`, `Recipe`, `VideoObject`, `LocalBusiness`. _(Retrieved 2026-07-09 — eligibility rules change; re-verify.)_
- **Rules that don't change:** markup must **match visible content** (marking up content not on the page is a structured-data manual-action risk); mark up the real, user-visible thing.
- **Verify** in the **Rich Results Test** and the GSC **Enhancements** reports (validation + coverage over time), not just a schema linter.
- **Entities & topical authority:** structured data + consistent entity references (sameAs, Organization, author entities) help engines resolve *what/who* a page is about — part of "understanding," feeding topical authority.

---

## Core Web Vitals — a ranking factor, measured on field data

- The three metrics: **LCP** (loading), **INP** (interactivity — **replaced FID in March 2024**), **CLS** (visual stability). _(Retrieved 2026-07-09.)_
- CWV is a **real but modest ranking signal — a tiebreaker among comparable results, not an override for content quality.** A fast thin page does not outrank a slow authoritative one.
- Measure on **field data (CrUX)** — the 75th-percentile of real users — not a single lab **Lighthouse** score. Lab tools diagnose; field data is what Google uses. Optimize the field metric, verify in the GSC **Core Web Vitals** report.

---

## International SEO — hreflang

- **hreflang** tells Google which language/region version to serve. It must be **bidirectional** (every page's hreflang set includes a **return tag** back to it) and **self-referencing**; use `x-default` for the fallback.
- Delivery: HTML `<link>` tags, HTTP headers (for non-HTML), or the XML sitemap (cleanest at scale).
- Common breakages: missing return tags, wrong region/language codes (ISO 639-1 language + optional ISO 3166-1 region), or hreflang pointing at non-canonical/redirecting/noindex URLs.

---

## Site migrations — the highest-risk SEO event

A replatform, redesign, domain change, or HTTP→HTTPS/URL-structure change is where rankings are most often lost. The non-negotiables:

1. **A complete old→new 301 redirect map** — every old URL with equity maps to its closest new equivalent, **single-hop** (no chains), status **301** (permanent). A blanket redirect-to-homepage is equity destruction.
2. **Staging behind noindex + auth** — never let a staging/dev site get crawled or indexed (a duplicate of production competing with it). Remove the noindex/robots-block on go-live, not before.
3. **Preserve** canonicals, hreflang, structured data, and internal-link structure across the move.
4. **Search Console:** verify both properties, submit new sitemaps, use **Change of Address** for a domain move, and watch coverage/rankings closely post-launch.
5. **Post-launch verification:** crawl the new site, confirm redirects resolve single-hop, confirm indexation in GSC, and **root-cause any ranking drop to the change** (a missing redirect, an indexed staging URL, a lost canonical) — don't "wait and see."

---

## 2026 tooling map (dated — volatile, re-verify before quoting)

- **Google-first:** **Google Search Console** (Coverage/Pages, URL Inspection, Enhancements/rich-result reports, Core Web Vitals, Change of Address), **Rich Results Test**, **PageSpeed Insights / CrUX** field data, **Lighthouse** (lab). **Bing Webmaster Tools** (+ IndexNow for instant submission). _(Retrieved 2026-07-09.)_
- **Crawlers / auditors:** **Screaming Frog SEO Spider**, **Sitebulb**, **JetOctopus** / **Botify** / **Lumar** (Deepcrawl) for enterprise + log-file analysis. _(Retrieved 2026-07-09.)_
- **Rank / visibility / research suites:** **Ahrefs**, **Semrush**, **Sistrix**, **Moz** — keyword, backlink, SERP-feature, and visibility tracking. **Feature depth and pricing vary and change** — treat as a 2026-07 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a client commitment. _(Retrieved 2026-07-09.)_
- **Log analysis:** the enterprise crawlers above, or a warehouse/Splunk/GoAccess pipeline over verified-Googlebot access logs.

---

## Provenance

- Durable mechanics (crawl→render→index→understand→rank, robots-vs-noindex, canonicalization semantics, SSR/SSG/CSR rendering trade-offs, JSON-LD eligibility-not-guarantee + match-visible-content, hreflang bidirectionality, redirect-mapped/staging-noindex migrations) are consensus practice across Google Search Central and the technical-SEO literature, reviewed 2026-07-09 — **High confidence**.
- The signal/tooling map — dynamic rendering deprecation, INP replacing FID (March 2024), pagination signal changes, FAQ/HowTo rich-result reductions, CWV weighting, and every tool's feature set/pricing — is a **2026-07 snapshot**; these are volatile, carry the retrieval dates above, and must be re-verified with `ravenclaude-core/deep-researcher` before pinning in a client deliverable.
