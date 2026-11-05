---
name: information-architecture
description: Design site information architecture — sitemap, URL taxonomy, navigation patterns (primary / utility / footer / contextual), card-sort discipline, content model that the IA implies, and the URL-to-template mapping. On a portal or signed-in UX review, place each major content block (Keep, Move, or Remove) before the pass is done. Used by `web-architect` (primary) + `ux-designer`.
---

# Skill: information-architecture

**Purpose:** Design site information architecture — sitemap, URL taxonomy, navigation patterns, content model that the IA implies, and the URL-to-template mapping. Used by `web-architect` (primary) and `ux-designer`.

IA is the load-bearing decision of the build. Get it wrong and every other discipline pays compounding interest — content can't find its slot, design has to invent extra navigation patterns, SEO bleeds, and the CMS becomes a workaround factory. Get it right and the rest of the site falls out of the structure almost mechanically.

## When to use

- Greenfield site — before wireframes, before brand, before stack selection finalizes
- Re-architecture of an existing site (URL churn, navigation rebuild, CMS re-platform)
- Adding a new top-level section (`/docs`, `/customers`, `/blog/changelog`)
- Pre-SEO push — the IA is upstream of every keyword strategy
- Multi-locale rollout — locale routing decisions are IA decisions
- UX review of an existing portal or signed-in product page — before the pass is called done, place every major content block (§8)

## The IA artifact set

A complete IA deliverable for a marketing site has **five** linked artifacts. Don't ship a "sitemap" alone; the sitemap without the others is decoration.

1. **Sitemap** — every URL, hierarchically grouped, with template type annotated
2. **URL taxonomy spec** — slug conventions, trailing-slash rule, casing rule, locale routing
3. **Navigation spec** — primary / utility / footer / contextual (in-page + cross-link), each with its inclusion criteria
4. **Content model** — for each template type, the fields and relationships the CMS must expose
5. **Redirect plan** — for any re-architecture, the old-URL → new-URL map with 301 chains audited

## 1. Sitemap shapes

Pick the shape from the content, not the org chart. Three canonical shapes:

### Hub-and-spoke (preferred for marketing sites under ~50 pages)

```
/
├── /product
├── /pricing
├── /customers
├── /resources/
│   ├── /resources/blog
│   ├── /resources/docs
│   └── /resources/changelog
├── /about
└── /contact
```

Shallow, wide, predictable. Every top-level section is reachable from the home in one click. Most modern marketing sites (Linear, Vercel, Resend) live here.

### Deep hierarchical (when content is genuinely categorical)

```
/industries/
├── /industries/healthcare
├── /industries/financial-services
└── /industries/manufacturing
/solutions/
├── /solutions/<solution>/<sub-solution>
```

Use when the content **is** categorical — large product catalogs, enterprise solution matrices, regulated-industry sites where each industry is a distinct sales motion. The cost: every level deeper is a click penalty and a SERP-snippet penalty (breadcrumbs help, but not enough).

### Hybrid (most common for sites > 50 pages)

Hub-and-spoke at the top, narrow hierarchy under one or two sections (`/docs`, `/blog`). This is Stripe, Cal.com, Resend's docs.

**Rule of thumb:** if a section needs more than two levels of hierarchy to navigate, it's probably a candidate to split into its own subdomain (`docs.example.com`) or a subdirectory with a dedicated nav (`/docs` with side-rail).

## 2. URL taxonomy principles

URLs are user-facing **and** machine-facing. They outlive design refreshes by years. Every URL change is a 301 chain you carry forever.

- **Stable** — once published, never change the slug without a 301. Slug churn destroys backlinks, social shares, and SEO equity.
- **Readable** — `/customers/acme-corp` not `/c/?id=42`. Slugs are content, not IDs.
- **Hierarchical** — `/blog/topic-slug` reads as a child of `/blog`. URLs reflect the IA.
- **Lowercase + kebab-case** — enforce at the platform level; redirect mixed-case and underscores.
- **No file extensions** — `/about` not `/about.html`. Platform implementation detail leaks otherwise.
- **No stop-words in slugs** — `/the-best-way-to-x` → `/best-way-to-x`. SEO is marginal here; readability is the real win.
- **One canonical** — pick trailing-slash or no-trailing-slash, then enforce. The cost of inconsistency is duplicate content + split link equity.
- **Locale routing** — `/en/`, `/de/`, `/ja/` as a prefix is the most maintainable pattern. `x-default` handled at root.

## 3. Navigation patterns

Navigation isn't just the top bar. It's **four** distinct surfaces, each with different inclusion criteria.

| Surface | Includes | Don't include |
|---|---|---|
| **Primary** | Top 3–6 destinations by conversion / strategic priority | Everything that doesn't earn its slot |
| **Utility** | Sign in, language, search, dark-mode | Marketing-ranked items |
| **Footer** | Comprehensive sitemap, legal, social, secondary CTAs | Decorative junk drawer (it's still scanned by users + crawlers) |
| **Contextual** | Side-rail in docs, in-page TOC, related links | Anything global |

### Primary nav: when to use which pattern

- **Single-column dropdown** — default for marketing sites with ≤ 6 top items, each with ≤ 8 children. Linear, Cal.com pattern.
- **Mega-menu** — when one nav item has 3+ sub-categories that each have their own children. Stripe, Vercel /products. Cost: a11y is harder (focus management, escape handling); mobile pattern must be designed separately.
- **Side-rail** — docs, settings, content-heavy sections where the user needs to see "where am I in this tree" at all times.
- **Sticky top + breadcrumbs** — when the user navigates deep but needs the top nav present at all times. Most documentation sites.

**Anti-pattern:** more than 7 items in the primary nav. If you have 9, three of them aren't earning the slot — move them to the footer or consolidate.

- **Mobile/app bottom-navigation item cap: ≤5.** Where the archetype's nav pattern is a bottom tab bar (a PWA, an app-shell IA) rather than a top nav, the same "earn your slot" discipline applies at a tighter number — a 6th item is either collapsed into a "More" tab or cut.

## 4. Card-sort methodology

Card sorting de-biases IA from internal vocabulary. Two modes:

- **Open card sort** — give users the content items, let them group + label. Reveals the user's mental model.
- **Closed card sort** — give users your proposed nav labels, let them sort content into them. Validates a proposed IA.

For a marketing site, **8–12 participants** is enough to find the dominant clustering pattern. Tools: Optimal Workshop, Maze, or even a Figma board with sticky notes for a quick async run.

What to look for:
- Items that get sorted into multiple buckets consistently — they need to live in two places (or the buckets are wrong).
- Labels users don't recognize — your internal jargon. Rename before launch.
- Categories with one item — collapse upward.

## 5. Content model implied by the IA

Every URL pattern in the sitemap is a **template type**, and every template type has a content model. Document them together:

```
URL pattern              Template       Content model (CMS fields)
─────────────────────    ───────────    ───────────────────────────────
/                        home           hero, sections[], CTAs[]
/product                 marketing      hero, features[], testimonials[], CTA
/customers/<slug>        case-study     customer{}, story, metrics[], quote, related[]
/blog/<slug>             post           title, author->, published, body (mdx), tags[]
/docs/<slug>             doc            title, body (mdx), prev->, next->, edit_url
/legal/<slug>            legal          title, body, last_updated, jurisdiction
```

If you can't write this table, the IA is incomplete. The handoff to the CMS or to `frontend-implementer` will be guesswork.

## 6. CMS implications (must be designed-in, not retrofitted)

For each template type the IA implies, the CMS must expose:

- **Slug field** (with validation: kebab-case, no duplicates within parent)
- **Parent relationship** (for hierarchical URLs)
- **Redirect log** — when a slug changes, the CMS writes a 301 from old → new automatically
- **Status** — draft / scheduled / published / archived (archived ≠ deleted; archived 410s)
- **Locale field** if multilingual; `hreflang` siblings linked

Pick the CMS **after** the content model is sketched, not before. The content model rules out half the candidates immediately (a flat blog tool can't handle case-study `customer{}` relations cleanly).

## 7. Redirect plan (re-architecture only)

A re-architecture without a redirect plan is a launch-day SEO incident waiting to happen.

For each old URL:
- **301** to the closest new URL (preserves ~90% of link equity)
- **410** if the content is genuinely gone (faster than 404 for crawler de-indexing)
- **Never 302** for a permanent move
- **No redirect chains > 1 hop** — collapse `A → B → C` to `A → C`

Audit with a crawler (Screaming Frog) after the redirect map is in place but **before** DNS cutover. Most re-platform incidents come from redirects added late.

## 8. Content placement on a page that already exists

Sitemap shape says where a *page* sits. This step says whether a *block* belongs on the page you are looking at. On a portal review, run PLACE in [`../../knowledge/portal-and-site-review-checklist-2026-11.md`](../../knowledge/portal-and-site-review-checklist-2026-11.md) before this skill's sitemap, card-sort, or redirect plan. Chrome, accessibility, and form review do not substitute for it.

The blocks: forms, builders, editors, tables, share kits, analytics panels, settings. Shared chrome (rail, account menu, page title) is not a block.

For each block, one verdict:

| Verdict | Meaning |
|---|---|
| **Keep** | The block does this page's job, and this route is where that job is done. |
| **Move** | The block is the real tool. Name the product area and the route it moves to. |
| **Remove / redirect** | The block duplicates a tool that already has a route, or it is a leftover. Name the route that remains. |

Traverse the content-placement tree in [`../../knowledge/web-design-decision-trees.md`](../../knowledge/web-design-decision-trees.md) before choosing. The citable rule is [`../../best-practices/content-belongs-on-the-page-that-owns-it.md`](../../best-practices/content-belongs-on-the-page-that-owns-it.md).

**Anti-pattern — builder or editor on a page whose nav parent is a different product entity.** The page's URL and nav parent name one thing (the site). The block edits another thing (the card). Reported 2026-11-05 `[user-reported]`: the full card editor still lived on `/account/site` after the Site card already had `/account/cards/site`. A summary or a link to the card's route can stay. The editor cannot.

A marketing or legal page with one job records `N/A — single-purpose page`. KKCR in [`../content-audit/SKILL.md`](../content-audit/SKILL.md) scores the URL; it does not place the block. A card-sort of 8 or more people is for a nav restructure. It is not a prerequisite for moving a tool that already has a home.

On the Website product the ship gate for this section is `check-content-placement.mjs`, covering `account/**` and shell/nav files (Website #953). Do not give that gate another name.

## Hygiene checklist

- [ ] Sitemap published as an artifact, reviewed by stakeholders, not just the design team
- [ ] Every URL annotated with its template type
- [ ] URL taxonomy rules documented (slug convention, trailing-slash, locale)
- [ ] Navigation spec covers primary + utility + footer + contextual
- [ ] Card-sort run with 8+ real users (or documented exception)
- [ ] Content model written for every template type
- [ ] CMS choice validated against the content model, not vice versa
- [ ] If re-architecting: redirect plan with every old URL accounted for
- [ ] `sitemap.xml` generated from the IA, not maintained separately
- [ ] Breadcrumbs match the IA exactly (no "phantom" parent pages)
- [ ] On a portal or signed-in review: every major content block has Keep, Move (named route), or Remove / redirect (§8)
- [ ] No builder or editor remains on a page whose nav parent is a different product entity

## Anti-patterns

- **Jamming everything under `/services`** — every section becomes a `/services/<thing>`, which is the IA equivalent of a junk drawer. Real differentiation lives at the top.
- **Slug churn** — renaming `/about` to `/company` to `/team-mission` over three quarters. Every rename is a 301 chain that compounds.
- **Pagination depth** — `/blog?page=47` reached only by clicking "next" 46 times. Use categories, search, or a "load more" pattern that updates the URL.
- **Org-chart sitemap** — IA that mirrors the company's department structure ("Marketing", "Sales Ops"). Users don't think in org-chart terms.
- **Mystery-meat nav** — labels users have to hover to understand. "Discover", "Solutions" (without context), "Resources" (catch-all).
- **Two competing taxonomies** — a sidebar that says one thing, breadcrumbs that say another, URL that says a third.
- **Nav updated, page body not** — a signed-in editor still rendered on the old URL after the nav points at a dedicated route. That is page-content placement, not a sitemap problem. Run [`../../knowledge/content-placement-page-ia-2026-11.md`](../../knowledge/content-placement-page-ia-2026-11.md) on every signed-in portal UX pass before chrome polish.
- **Sitemap.xml drift** — manually-maintained sitemap that lags the actual content. Generate from the CMS / build.
- **Locale routing via cookie / IP only** — user lands at `/`, gets redirected based on IP. Breaks back-button, hides locale from URL, breaks SEO. Use prefix routing.
- **"Coming soon" pages in the IA** — placeholder URLs that ship to production. Either build it or omit it.
- **Hash-based primary nav** — `/#features`, `/#pricing`. Looked clever in 2014. Wrecks SEO, breaks history, breaks deep-linking.
- **Editor stranded on the wrong entity** — a full builder or editor still lives on a page whose navigation parent is a different product. The 2026-11-05 miss `[user-reported]`: the card editor on `/account/site` after `/account/cards/site` existed. A chrome, accessibility, or form pass does not catch it.

## See also

- Template: [`../../templates/site-architecture.md`](../../templates/site-architecture.md)
- Skill: [`../seo-technical-audit/SKILL.md`](../seo-technical-audit/SKILL.md)
- Skill: [`../content-audit/SKILL.md`](../content-audit/SKILL.md) — KKCR scores the page; §8 places the block
- Signed-in block placement (Keep / Move / Remove), distinct from this skill's sitemap: [`../../knowledge/content-placement-page-ia-2026-11.md`](../../knowledge/content-placement-page-ia-2026-11.md)
- Rule: [`../../best-practices/content-belongs-on-the-page-that-owns-it.md`](../../best-practices/content-belongs-on-the-page-that-owns-it.md)
- Agent: [`../../agents/web-architect.md`](../../agents/web-architect.md)
- Agent: [`../../agents/ux-designer.md`](../../agents/ux-designer.md)
