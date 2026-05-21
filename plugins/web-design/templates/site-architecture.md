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

## Content model (if headless CMS)

| Entity | Fields | Relationships |
|---|---|---|
| Page | title, slug, body, seo_title, seo_description, og_image, locale | n/a |
| Article | title, slug, excerpt, body, author, category, tags, published_at | belongsTo Author, hasMany Tags |
| Author | name, bio, photo, social_links | hasMany Articles |
| ... | ... | ... |

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
