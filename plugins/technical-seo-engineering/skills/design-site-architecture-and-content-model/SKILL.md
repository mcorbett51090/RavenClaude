---
name: design-site-architecture-and-content-model
description: From a site's target queries and page classes, design the crawl-efficient information architecture (flat depth, hub-and-spoke topic clusters), the internal-linking model that flows authority to the money pages, and the topical-authority / entity map that tells search engines what the site should own. Reach for this when the user asks "how should we structure the site and internal links?", "design our topic clusters / content model", or "what's our topical-authority / entity map?". Used by `seo-strategy-architect` (primary) and `seo-implementation-engineer`.
---

# Skill: design-site-architecture-and-content-model

> **Invoked by:** `seo-strategy-architect` (primary, to design) and `seo-implementation-engineer` (to keep the implemented URL/link structure faithful to the designed IA).
>
> **When to invoke:** "How should we structure the site + internal links?"; "design our topic clusters / content model"; "what's our topical-authority / entity map?"; any move from target queries to an enforceable IA + linking model.
>
> **Output:** the site architecture (depth + hub-and-spoke clusters) + the internal-linking model (authority flow) + the topical-authority / entity map, ready for the engineer to implement as URLs and links.

## Procedure

1. **Name the target queries, intents, and page classes.** What must the site rank for, at what intent (informational / commercial / transactional), and which page templates serve each? The content model exists to cover those intents — a page with no target intent is a crawl-budget cost, not an asset.
2. **Design a flat, crawl-efficient depth.** Money pages should sit a few clicks from the root; nothing important should be an orphan or buried under deep pagination. Shallow depth is both a crawl-efficiency win and a user-navigation win.
3. **Build hub-and-spoke topic clusters.** A **pillar** page for each core topic, **cluster** pages for the sub-intents, all interlinked (spokes link up to the pillar and across to siblings). This is how a site demonstrates topical breadth+depth rather than a scatter of one-off pages.
4. **Design the internal-linking model to flow authority.** Link *toward* the money/pillar pages from relevant context; use descriptive anchor text (the entity/topic, not "click here"); fix orphan pages; keep the important pages the most-linked-to internally. Internal links are the lever this team controls (external links are earned, not built here).
5. **Draw the topical-authority / entity map.** The entities the site should *own* (products, concepts, people, the organization itself), how they relate, and the `sameAs`/Organization/author entity references that let engines resolve them. Consolidate thin/overlapping pages into fewer authoritative ones — cover the topic, don't mint a page per keyword.
6. **Map the model to URLs + a canonical strategy.** A clean, stable, readable URL structure per page class; one canonical per page; the faceted/parameter/duplicate variants folded into canonicals or noindex (hand the indexation calls to [`choose-seo-strategy-and-priorities`](../choose-seo-strategy-and-priorities/SKILL.md)).
7. **Hand off to implementation.** The IA + linking + entity model goes to `seo-implementation-engineer` via [`implement-technical-seo-and-structured-data`](../implement-technical-seo-and-structured-data/SKILL.md) — including any `BreadcrumbList`/`Organization` structured data that expresses the structure.

## Worked example

> User: "We sell running shoes and want to own 'trail running' as a topic. How should we structure the site and content?"

- **Target intents:** transactional (buy trail shoes) + informational (how to choose, trail-vs-road, gear guides).
- **Architecture:** flat — `/trail-running/` pillar hub, category pages (`/trail-running/shoes/`, `/trail-running/gear/`) as spokes, product pages under them; guides under `/trail-running/guides/…` all linking up to the pillar.
- **Internal linking:** every guide links to the pillar and to the relevant category/product; category pages link across to sibling categories; the pillar is the most-internally-linked page in the cluster.
- **Topical/entity map:** own the entities "trail running", "trail running shoes", key sub-topics (grip, cushioning, terrain); Organization + author entities on the guides; consolidate three overlapping "best trail shoes" posts into one authoritative pillar-linked guide.
- **URLs/canonicals:** clean `/trail-running/…` paths; color/size product variants canonicalize to the primary product; sort/filter facets noindex.
- **Structured data to implement:** `BreadcrumbList` expressing the hierarchy, `Product` on product pages, `Organization` sitewide.

## Guardrails

- Flat, hub-and-spoke, no orphans — depth and orphaning are self-inflicted crawl/index problems.
- Internal links flow authority *to* the money/pillar pages with descriptive anchors — this is the team's controllable lever.
- Model **topics and entities**, not keyword strings — consolidate thin/overlapping pages, don't mint a page per keyword.
- The IA implies an indexation strategy — cross-reference [`choose-seo-strategy-and-priorities`](../choose-seo-strategy-and-priorities/SKILL.md) for the index/canonical/noindex calls per page class.
- Writing the actual content is `technical-writing-docs`; the full visual build is `web-design` — this skill designs the SEO structure they honor.
- See the patterns reference for canonicalization + structured-data mechanics: [`../../knowledge/technical-seo-patterns-2026.md`](../../knowledge/technical-seo-patterns-2026.md).
