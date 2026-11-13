# Site architecture — [Site name]

> IA + page-type taxonomy + navigation spec. The frame the rest of the build hangs on.

**Site:** [...]
**Tech stack:** [...]
**Hosting:** [...]
**Last updated:** [YYYY-MM-DD]
**Owner:** [...]

---

## URL structure

- **Trailing slash:** with / without (pick one + enforce)
- **Case:** lowercase enforced
- **Locale prefix:** `/en/`, `/de/` etc. — yes / no
- **Canonical hostname:** `www.example.com` or `example.com` (one, the other redirects)

### Sitemap (top-level)

```
/                          Homepage
/about/                    About
/services/                 Services index
/services/<slug>/          Individual service page
/blog/                     Blog index
/blog/<year>/<slug>/       Blog post
/contact/                  Contact
/legal/privacy/            Privacy policy
/legal/terms/              Terms of service
/404                       Custom 404
/500                       Custom 500
```

## Page-type taxonomy

| Page type | URL pattern | Template | Owner |
|---|---|---|---|
| Homepage | `/` | `Home.astro` | [...] |
| Service detail | `/services/[slug]/` | `ServiceDetail.astro` | [...] |
| Blog post | `/blog/[year]/[slug]/` | `BlogPost.astro` | [...] |
| ... | ... | ... | ... |

## Content placement (signed-in / portal pages)

Skip with `N/A — single-purpose page` when the page has one job (a marketing page, a legal page). Otherwise every major block gets one verdict before this IA is signed. A builder or editor on a page whose nav parent is a different product entity is Move or Remove, not Keep. Procedure: `skills/information-architecture` §8.

| Route | Block | Verdict (Keep / Move / Remove) | Destination route, if not Keep |
|---|---|---|---|
| `/…` | [editor / table / form / share kit / analytics / settings] | | |

## Navigation

### Primary navigation

- About
- Services
- Blog
- Contact

### Secondary / utility

- Login / Sign up (if applicable)
- Locale switcher (if multi-language)
- Search (if applicable)

### Footer

- Sitemap links (mirrors primary nav + legal)
- Social links
- Newsletter signup
- Copyright + contact + privacy / terms

### Mobile navigation

- Hamburger → drawer with primary nav
- Sticky CTA on mobile if conversion-driven

## Signed-in page content (portal)

> Run on every signed-in portal UX pass, before chrome polish. One row per major block, from the rendered page. Procedure: [`../knowledge/content-placement-page-ia-2026-11.md`](../knowledge/content-placement-page-ia-2026-11.md). Marketing-only site: `N/A — no signed-in routes`.

Walk signed in. Open every route the rail, account menu, and in-page tabs can reach.

| Route | Block | Verdict (Keep / Move / Remove/redirect) | Destination (route — product area) | Old page keeps |
|---|---|---|---|---|
| /account/site | Card editor | Move | /account/cards/site — Cards | Link only. Not a second editor. |
| ... | ... | ... | ... | ... |

- [ ] No editor or builder remains on a page whose nav already points at a dedicated route for it.
- [ ] Move and Remove/redirect rows name the route. "The nav looks fine" is not a substitute for this table.

The `/account/site` row is the reported shape `[user-described 2026-11-05]`, not a route every product must copy.

## IA validation (card sort — G2 acceptance record)

> G2 requires the nav/taxonomy be validated, not just asserted. Record the method and result here.

- **Method:** open / closed / hybrid card sort · **participants:** [8–12 target]
- **Result / key regroupings:** [...]
- **Waiver (if no human panel available):** `synthetic-persona / stakeholder-proxy sort — validated against the G1 audience personas; re-run with real participants if budget appears` (owner + date)

## Internationalization

- **Locales supported:** [en-US, en-GB, de-DE, ...]
- **Default locale:** [...]
- **Locale routing:** subpath / subdomain / param
- **hreflang declarations:** required on every multilingual page
- **Locale fallback:** [policy]

## Build pipeline

- **Repo:** [monorepo / polyrepo]
- **Branch strategy:** [trunk-based / GitFlow / etc.]
- **Preview deployments:** [Vercel preview / Netlify preview / GH Pages]
- **Build steps:**
  1. Install
  2. Lint / type-check / unit tests
  3. Build static output
  4. Image optimization
  5. Sitemap + robots generation
  6. Deploy to preview / production

## Hosting + CDN

- **Hosting platform:** [...]
- **CDN:** [...]
- **Cache strategy:** [HTML cache TTL; immutable assets via content hash]
- **Custom domain config:** [DNS records to be set]

## Content model

> Every site has a content model, headless CMS or not — per-template fields + relationships. It is a **mandatory G2 artifact** (the join input G4 populates and G5 renders), not a headless-only concern; for a static/file-based build the "entities" are the content collections (Markdown/MDX frontmatter schema).

| Entity | Fields | Relationships |
|---|---|---|
| Page | title, slug, body, seo_title, seo_description, og_image, locale | n/a |
| Article | title, slug, excerpt, body, author, category, tags, published_at | belongsTo Author, hasMany Tags |
| Author | name, bio, photo, social_links | hasMany Articles |
| ... | ... | ... |

## Redirect plan (mandatory on any re-platform / redesign)

> A retired URL without a 301 destroys its link equity. Audit **301 chains** (old → new, no chains-of-chains) and map every retiring URL **before** any page is removed. On a greenfield build with no prior URLs, record `N/A — greenfield, no prior URLs`.

| Old URL | → New URL | Status | Notes (chain check, param handling) |
|---|---|---|---|
| /old-path | /new-path | 301 | |
| ... | ... | ... | |

## Technical SEO foundations

- [ ] `robots.txt` at root
- [ ] `sitemap.xml` referenced from `robots.txt`
- [ ] Canonical URLs declared on every page
- [ ] `<html lang="...">` on every page
- [ ] OG / Twitter Card meta on every page
- [ ] Schema.org JSON-LD (Organization on homepage, BreadcrumbList on subpages, Article on blog posts)
- [ ] 404 page returns 404 (not 200)
- [ ] 301 redirects for old → new URLs documented

## Build artifacts to commit

- [Source code tree]
- [Token JSON files]
- [robots.txt + sitemap (generated, but committed)]
- [Public assets (compressed)]

---

**See also:**
- [Design brief](./design-brief.md)
- [Design system spec](./design-system-spec.md)
- [Performance budget](./performance-budget.md)
- [Launch checklist](./launch-checklist.md)
