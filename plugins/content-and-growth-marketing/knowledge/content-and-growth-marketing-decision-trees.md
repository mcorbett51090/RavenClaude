# Content & Growth Marketing — Decision Trees

_Decision trees + a dated capability/landscape map. Capability rows are `[verify-at-build]` — re-check against the vendor/platform before quoting (search volumes, algorithm behavior, ESP features, and AEO surfaces move fast). Last reviewed: 2026-06-08._

Traverse before publishing a piece, targeting a query, or building a lifecycle flow.

## Decision Tree: Should we publish this piece (and is it worth it)?

Content is justified by an audience job + a differentiated angle — not by a slot on the calendar.

```mermaid
graph TD
  A[Candidate content idea] --> B{Does it serve a real audience job-to-be-done?}
  B -- No, it's a trending topic with no relevance --> C[Skip - vanity traffic that won't convert; protect the cluster]
  B -- Yes --> D{Does it fit a topic cluster / pillar, or is it an orphan?}
  D -- Orphan --> E[Reshape to fit a pillar, or start a new cluster only if 2+ pieces will follow]
  D -- Fits a cluster --> F{Do we have a differentiated POV - data, experience, contrarian take?}
  F -- No, it restates the SERP --> G[Don't publish me-too - find an angle or repurpose existing depth]
  F -- Yes --> H{Can we name the reader's next action - the CTA / funnel hook?}
  H -- No --> I[Add a CTA and a lifecycle hook, or it's a cost center with no downstream]
  H -- Yes --> J[Brief it: audience, intent, angle, outline, internal links, CTA, distribution]
```

_Compounding over volume: a skipped low-value post costs less than a published one that dilutes the cluster and the brand._

## Decision Tree: How do we target this query — and on which surface?

Match the page to the intent; then decide classic-rank vs. answer-engine (AEO/GEO) — increasingly both.

```mermaid
graph TD
  A[A query we want to win] --> B{What is the search intent?}
  B -- Informational --> C[Map to a pillar/cluster article or guide]
  B -- Commercial investigation --> D[Map to a comparison / solution page]
  B -- Transactional --> E[Map to a product / landing page - NOT a blog post]
  C --> F{Is the page crawlable + indexed?}
  D --> F
  E --> F
  F -- No --> G[Fix crawl/index first - optimizing an unindexed page is motion, not progress]
  F -- Yes --> H{Is this query intercepted by AI Overviews / LLM answers?}
  H -- Yes --> I[AEO/GEO: answer-shaped content, Q&A structure, structured data, citable sources, entity coverage]
  H -- No / also classic --> J[On-page + internal linking + SERP-feature targeting; consolidate any cannibals into one pillar]
```

_Search now includes answer engines. AEO/GEO is a first-class surface measured distinctly from blue-link rank — not a footnote._

## Decision Tree: Lifecycle flow or broadcast — and is it deliverable?

Triggered, segmented flows out-convert blasts; deliverability is the foundation under both.

```mermaid
graph TD
  A[A message we want to send] --> B{Is it triggered by a behavior / funnel stage?}
  B -- No, it's to the whole list --> C{Is it genuinely a broadcast - newsletter, announcement?}
  C -- No --> D[Make it a triggered flow - define entry/exit criteria and segment it]
  C -- Yes --> E[Segment by engagement anyway; suppress the unengaged to protect reputation]
  B -- Yes --> F{Is the segment defined and the exit/suppression set?}
  F -- No --> G[Add segmentation + exit + suppression, or people get stuck or double-messaged]
  F -- Yes --> H{Is deliverability sound - SPF/DKIM/DMARC, list hygiene, engaged list?}
  H -- No --> I[Fix authentication + sunset the unengaged BEFORE sending - spam converts at zero]
  H -- Yes --> J[Ship the flow; measure clicks/conversion + inbox placement, never opens alone]
```

_Self-service-of-the-funnel means the right message fires on behavior — not a batch-and-blast. Deliverability and segmentation come before clever copy._

## Decision Tree: How do we distribute and repurpose this asset?

Distribution is half the work — a piece nobody sees is a sunk cost. Plan reach before shipping, then atomize.

```mermaid
graph TD
  A[A published / about-to-publish asset] --> B{Is there a distribution plan in the brief?}
  B -- No --> C[Stop - publish-and-forget wastes the expensive half; add reach before shipping]
  B -- Yes --> D{Does it fit a cluster with a pillar to link up to?}
  D -- No --> E[Reshape to a cluster or it has no internal-link reach; orphans don't compound]
  D -- Yes --> F{Is it durable / evergreen or time-bound?}
  F -- Evergreen --> G[Atomize: social thread + email sequence + short video + slide; schedule re-shares]
  F -- Time-bound --> H[One-pass distribution: announcement send + social; don't over-invest in repurposing]
  G --> I{Which channel carries the job-holder?}
  H --> I
  I -- Owned email --> J[Segment by engagement; send to the relevant segment, suppress unengaged]
  I -- Organic search --> K[Internal links from cluster + pillar; route any build to web-design]
  I -- Social / community --> L[Atomize to the format the channel rewards; one asset -> ten]
```

_One asset becomes ten. The distribution plan is part of the brief, not bolted on after — a piece with no reach plan isn't ready to ship._

## Decision Tree: This page/query isn't winning — what's the root cause?

Optimizing on-page on a page that isn't crawled, indexed, or intent-matched is motion, not progress. Triage in order.

```mermaid
graph TD
  A[A page/query underperforming] --> B{Is the page crawlable + indexed?}
  B -- No --> C[Fix crawl/index first - robots, canonicals, render strategy; route build to web-design]
  B -- Yes --> D{Does the page match the query's intent?}
  D -- No --> E[Re-map: transactional query to a product page, informational to a guide - not vice versa]
  D -- Yes --> F{Are multiple thin pages competing for the query?}
  F -- Yes --> G[Cannibalization: consolidate the thin pages into one pillar; redirect the rest]
  F -- No --> H{Is the query intercepted by AI Overviews / LLM answers?}
  H -- Yes --> I[AEO/GEO gap: answer-shaped content, Q&A structure, structured data, citable sources]
  H -- No --> J{Is there a differentiated POV vs. the SERP?}
  J -- No --> K[Me-too: it restates page one - find an angle or don't compete here]
  J -- Yes --> L[On-page + internal linking + SERP-feature targeting; measure rank AND answer-engine presence]
```

_Triage in order — crawl/index, then intent, then cannibalization, then surface (classic vs. AEO/GEO), then POV. Tuning on-page before this order is settled is motion, not progress._

---

## Capability / landscape map (2026, `[verify-at-build]`)

| Layer | Options | Notes |
|---|---|---|
| CMS / publishing | Headless (Contentful, Sanity, Strapi), WordPress, Webflow, framework-native (Next/Astro content) | Render strategy (SSR/SSG) affects crawlability — route the build to `web-design` `[verify-at-build]` |
| Keyword + SEO research | Ahrefs, Semrush, Moz, Google Search Console, Google Keyword Planner | Volumes/difficulty are estimates — cite the tool + date, never quote a number you didn't pull `[verify-at-build]` |
| Technical SEO | GSC, Screaming Frog, Sitebulb, PageSpeed Insights / CrUX (Core Web Vitals), schema.org structured data | Crawl/index + CWV before on-page polish `[verify-at-build]` |
| SERP features | Featured snippets, People-Also-Ask, knowledge panels, sitelinks | Answer-shaped content + structured data win these `[verify-at-build]` |
| AEO / GEO surfaces | Google AI Overviews, ChatGPT/Perplexity/Copilot answers, Bing generative | Optimize for citability + entity coverage; measure presence distinctly from rank — volatile, re-verify `[verify-at-build]` |
| ESP / marketing automation | Klaviyo, Braze, Customer.io, HubSpot, Marketo, Mailchimp, Iterable | Flow logic + segmentation + suppression matter more than the brand `[verify-at-build]` |
| Deliverability | SPF / DKIM / DMARC auth, Google Postmaster, list hygiene + sunset policy, seed-list testing | Authentication + engaged list are the foundation `[verify-at-build]` |
| Funnel / outcome metrics | DORA-of-marketing? No — use funnel-stage conversion, organic-to-pipeline, revenue per recipient, engaged-list health | Pair every throughput metric with an outcome; opens are a privacy-inflated proxy `[verify-at-build]` |

_Framework references: topic-cluster / pillar-page model (HubSpot), search-intent taxonomy (informational / commercial / transactional / navigational), the lifecycle stages (acquisition → activation → nurture → conversion → retention → reactivation), and the AEO/GEO distinction (optimizing for answer engines vs. classic ranking). Re-verify any tool/algorithm/surface specific before quoting it to a consumer — this landscape moves quarterly._
