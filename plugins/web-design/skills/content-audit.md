---
name: content-audit
description: Audit existing site content — full inventory (URL × type × intent × last-updated × owner), scoring against business / user-need / SEO criteria, remediation queue (keep / consolidate / rewrite / retire), and the migration plan when re-platforming. Reach for this skill at the start of a re-platform, before an SEO push, or when content quality has stopped predicting conversion. Used by `content-strategist` (primary) + `web-architect`.
---

# Skill: content-audit

**Purpose:** Audit existing site content — full inventory, scoring, remediation queue, and migration plan when re-platforming. Used by `content-strategist` (primary) and `web-architect` (URL / IA / redirect side).

A content audit is the only honest answer to "what do we actually have?" Most teams overestimate their content asset by 3–10x because they're counting URLs, not value. The audit produces the inventory + the verdict for each page. Without the verdict, an "audit" is a spreadsheet that gathers dust.

## When to use

- **Re-platform** — moving CMS, redesigning, restructuring the IA. The audit is what makes the redirect plan possible.
- **Pre-SEO push** — before investing in new content, find the existing content that's underperforming for fixable reasons.
- **Content quality has stopped predicting conversion** — analytics shows top-of-funnel growth but flat conversions; the content asset is decaying.
- **Annual or biannual review** — a healthy content function audits at least yearly.
- **After a Google update** — when ranking drops are content-quality-driven.

## 1. Full inventory (the spreadsheet)

The audit lives or dies on a complete, honest inventory. Columns that are non-negotiable:

| Column | Why |
|---|---|
| URL | The primary key |
| Page title | Surfaces stale / duplicate titles |
| Page type / template | Blog post vs landing vs doc vs legal — different scoring rules |
| Word count | Rough proxy for depth |
| Last published / updated | Freshness signal |
| Author / owner | Who is accountable for this page existing |
| Primary intent | Awareness / consideration / conversion / retention / support |
| Target keyword (if SEO content) | Reveals keyword cannibalization |
| Organic traffic (last 90 days) | Real performance |
| Conversions / events (last 90 days) | Business value |
| Backlinks (referring domains) | Equity at risk if we kill this |
| Score (1–5 per dimension) | The verdict |
| Recommendation | Keep / Consolidate / Rewrite / Retire |

### How to build the inventory

- **Crawl tools** — Screaming Frog (desktop, free up to 500 URLs), Sitebulb (richer reporting), or your CMS's export if it's clean. Crawl-based is more honest than CMS-based because it catches orphan pages.
- **CMS export** — for owner / author / publication-date data
- **Analytics overlay** — Google Analytics 4 / Plausible / Fathom export by URL, joined on the URL column
- **Search Console overlay** — impressions, clicks, average position by URL
- **Backlinks overlay** — Ahrefs / Semrush export by URL (the most valuable join — kills the "retire it, no one's reading it" reflex when there are 200 referring domains pointing at it)

The join key is the URL. Normalize it (trailing-slash, lowercase, strip UTM) before joining.

## 2. Scoring dimensions

For each URL, score 1–5 on five dimensions:

| Dimension | What it measures | 1 (low) | 5 (high) |
|---|---|---|---|
| **Business value** | Does this page serve a current business goal? | Vestigial / obsolete | Directly drives conversion or retention |
| **User task served** | Does it answer a real user question or task? | Internal-monologue content | Solves a specific user job |
| **SEO performance** | Traffic + ranking + backlink profile | No traffic, no rankings, no links | Strong organic, defensible position |
| **Freshness** | Is the content current? | > 24 months old + decaying topic | Updated within 6 months or evergreen-and-still-correct |
| **Quality** | Is it well-written, well-structured, original? | Thin / outdated / off-brand | High-quality, on-voice, useful |

A total score below ~10 is a retire / consolidate candidate. Above ~18 is a keep / boost candidate. The middle is where the work is.

## 3. The KKCR matrix (the verdict)

Each URL gets one verdict. No "we'll decide later" — the audit ends with a queue, not a maybe-list.

| Verdict | Definition | Action |
|---|---|---|
| **Keep** | High score, doing its job | Refresh-cadence noted; no immediate work |
| **Consolidate** | Two or more pages competing for same intent / keyword | Merge into one canonical; 301 the others |
| **Rewrite** | Right topic, wrong execution (outdated, off-voice, thin) | Author re-writes; URL preserved |
| **Retire** | No business value, no user task, no SEO equity | 410 if truly gone, 301 to closest parent if equity exists |

**Cannibalization** (two pages ranking for the same keyword, splitting traffic) is the most common consolidation trigger. Spot it in Search Console by sorting by keyword and finding URLs that share top-10 positions.

## 4. Redirect plan when consolidating / retiring

Every URL that goes away needs a destination:

- **301** to the closest relevant URL — preserves ~90% of link equity
- **410** for pages with genuinely no replacement and no backlinks — faster de-indexing than 404
- **Never 302** for a permanent move
- **No redirect chains > 1 hop** — if `A → B` exists and you now retire `B → C`, update `A → C` directly
- **Audit the rolled-up redirect log** — over years, redirect chains compound; treat the redirect file as code

Log the audit's redirect decisions in a versioned file (`redirects.csv` or the equivalent in your CMS / hosting). The next audit reads from it.

## 5. Authoring guidelines that come out of the audit

A good audit produces **prescriptive** guidelines for new content, not just retrospective scoring:

- **Voice + tone** — extracted from the highest-scoring pages, codified in a style guide
- **Reading level** — measured (Flesch-Kincaid or Hemingway score); set a target (e.g. grade 9 for marketing, grade 11 for technical)
- **Length norms by template type** — blog post: 800–1500 words is typical 2026 sweet spot; landing page: long enough to address all objections, short enough to not bury the CTA; doc page: as long as needed to fully answer the question
- **Heading / structure norms** — h1 once per page, h2 sections every ~300 words, h3 for sub-points
- **Image / media norms** — minimum visual interest per N words; alt text is required (§3 #5)
- **Internal-linking norms** — every new post links to N related pages; every page is reachable from the IA, not orphaned

## 6. Governance — the audit's lifecycle product

A one-time audit is a project. Audits that work are governance:

- **Named owner per content area** — every `/section/*` has a person who's accountable
- **Refresh cadence** — evergreen pages reviewed annually, time-sensitive ones quarterly, dated content (year-in-page-title) audited and re-dated
- **New-content gate** — proposed new pages get scored on the same dimensions before they ship; new content with a projected score below ~10 doesn't ship
- **Quarterly mini-audits** — full audit yearly, scoped audits (just the blog, just the docs) quarterly

## 7. Re-platform migration overlay

When the audit feeds a re-platform:

1. **Content model first** — what fields does the new CMS need? (See [`./information-architecture.md`](./information-architecture.md))
2. **Map old fields → new fields** — for each template type
3. **Export → transform → import** — typically via the new CMS's import format (Contentful, Sanity, Strapi all have JSON / CSV importers)
4. **Slug preservation rule** — preserve as many slugs as possible; if a slug must change, log the redirect
5. **Staging-environment audit** — re-run a crawl on staging; verify every URL from the keep / consolidate / rewrite buckets lands somewhere sensible
6. **Cutover plan** — DNS swap window, redirect file in place before launch, Search Console submission post-launch

## Hygiene checklist

- [ ] Inventory built from a crawler (not just CMS export) — catches orphan pages
- [ ] Analytics + Search Console + backlink data joined on URL
- [ ] Every URL has a score across all five dimensions
- [ ] Every URL has a verdict (no "TBD")
- [ ] Cannibalization audit done (keyword × URL pivot)
- [ ] Redirect plan in place for every Consolidate / Retire
- [ ] Redirect chains audited (no > 1-hop chains)
- [ ] Authoring guidelines extracted from the top-scoring pages
- [ ] Owner assigned per content area
- [ ] Refresh cadence documented
- [ ] If re-platforming: content model mapped + staging crawl complete
- [ ] Quarterly mini-audit scheduled in the team's calendar

## Anti-patterns

- **Audit-then-shelf** — the spreadsheet exists; the remediation never happens. The audit's value is the queue, not the inventory.
- **No remediation queue** — verdicts assigned but no tickets / owners / dates. Same outcome as audit-then-shelf.
- **Audit without traffic data** — scoring pages by gut-feel rather than what's actually performing. Junk audit.
- **Audit without backlink data** — retiring high-equity pages because they "have no traffic" (the link equity is the traffic — it flows to the rest of the site).
- **Retiring pages without 301s** — link equity destroyed, 404s spike, ranking drops sitewide.
- **Renaming slugs during the audit "to clean them up"** — every rename is a 301. Slug churn is a separate decision from content quality.
- **Voice-and-tone "guidelines" that are five adjectives** — "friendly, professional, witty, authoritative, approachable." Useless. Real guidelines have do / don't examples from real pages.
- **No owners** — when everyone owns the blog, no one owns the blog. Refresh cadence will drift.
- **Re-platform without the audit** — migrating low-value content into the new CMS is paying for the next audit twice.
- **Auditing only the blog** — landing pages, product pages, docs, legal — all of them get the same scoring treatment. The blog is just where the audit hurts least.

## See also

- Template: [`../templates/content-style-guide.md`](../templates/content-style-guide.md)
- Template: [`../templates/seo-audit-report.md`](../templates/seo-audit-report.md)
- Skill: [`./information-architecture.md`](./information-architecture.md)
- Skill: [`./seo-technical-audit.md`](./seo-technical-audit.md)
- Agent: [`../agents/content-strategist.md`](../agents/content-strategist.md)
- Agent: [`../agents/web-architect.md`](../agents/web-architect.md)
