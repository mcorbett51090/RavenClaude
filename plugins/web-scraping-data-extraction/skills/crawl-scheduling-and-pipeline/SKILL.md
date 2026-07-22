---
name: crawl-scheduling-and-pipeline
description: "Design the crawl schedule, change-detection, and the extraction-to-storage pipeline — a re-crawl cadence matched to data volatility, incremental crawls via conditional GET / ETag / sitemap lastmod, a polite rate-limit/backoff budget, and storage with provenance (source URL + fetch timestamp) and dedup. Traverses the schedule/pipeline branch of the web-scraping decision tree. Reach for this when the user asks 'how often should we re-crawl?', 'how do we detect changes?', 'set up the extraction pipeline', or 'add rate-limiting so we don't get blocked'. Used by scraper-implementation-engineer (primary) and extraction-architect."
---

# Skill: crawl-scheduling-and-pipeline

> **Invoked by:** `scraper-implementation-engineer` (primary — the pipeline + politeness layer) and
> `extraction-architect` (the cadence/change-detection design).
>
> **When to invoke:** "how often should we re-crawl?"; "how do we detect changes?"; "set up the
> extract→validate→store pipeline"; "add rate-limiting/backoff so we're a good citizen and don't get
> blocked"; any "keep the data fresh, politely, in a real pipeline" question.
>
> **Output:** a crawl schedule + change-detection strategy + a politeness budget + an
> extraction-to-storage pipeline with provenance and dedup.

## Procedure

1. **Match cadence to data volatility, not to a default.** How often does the source *actually*
   change? Prices/inventory: hourly-to-daily. Reference/catalog data: weekly-to-monthly. A daily
   re-crawl of monthly-changing data is wasted load on the target and on you. Set the cadence to the
   change rate.
2. **Crawl incrementally — re-fetch only what changed.** Use **conditional GET** (`If-None-Match`
   with the stored ETag, `If-Modified-Since`) so unchanged pages return `304` and cost nothing.
   Use the **sitemap `<lastmod>`** and feeds to find changed URLs without walking the whole site.
   Keep a per-URL state (last-fetch, ETag, content-hash) to detect real changes.
3. **Set a politeness budget and enforce it.** A concurrency cap per host, a per-host delay
   (respect `robots.txt` crawl-delay), and a total request rate that doesn't degrade the target.
   Honest, identifying **user-agent**. Honor **`Retry-After`** and back off exponentially with
   jitter on `429`/`5xx`. Politeness is simultaneously the ethics and the thing that keeps you
   un-blocked.
4. **Make the pipeline a clear line: fetch → parse → validate → dedup → store.** Each stage is
   observable and independently retryable. A transient fetch error retries with backoff; a parse/
   validation failure quarantines the record (see the resilient-extraction skill); only clean,
   validated records reach the store.
5. **Attach provenance to every record.** Store the **source URL** and **fetch timestamp** (and
   optionally the content-hash and crawl-run id) with each record. Without provenance you can't
   debug a bad value, audit where data came from, or do incremental updates.
6. **Dedup on a stable natural key.** Define the key that identifies an entity across crawls (a
   product SKU, a canonical URL). On re-crawl, upsert by key; use the content-hash to skip unchanged
   records cheaply and to record "last-changed."
7. **Instrument the crawl.** Per-run metrics: URLs seen / fetched / 304'd, records extracted,
   validation-failure rate, request errors and 429s, wall-time. Alert on anomalies (failure-rate
   spike = site changed; 429 spike = too aggressive, back off). This closes the loop with the
   architect's politeness posture.

## Worked example

> User: "We track ~5,000 product pages for price/stock. Set up re-crawl + the pipeline so we're
> fresh, polite, and don't re-fetch everything each run."

- **Cadence:** prices change daily-ish → **daily** re-crawl (not hourly; verify the change rate).
- **Incremental:** pull the sitemap `<lastmod>`; conditional-GET each product URL with its stored
  ETag — unchanged pages `304` and cost nothing. Only changed pages get parsed.
- **Politeness:** 2 concurrent requests/host, 1s delay, honest UA, honor `Retry-After`, exp-backoff
  on 429/5xx *(retrieval-dated 2026-07 for the site's crawl-delay)*.
- **Pipeline:** fetch → parse (JSON endpoint, per the extraction skill) → validate `{sku, price,
  currency, in_stock, url, fetched_at}` → upsert by **sku** → store; quarantine validation failures.
- **Provenance:** each record carries `url` + `fetched_at` + `content_hash`; `content_hash` unchanged
  → mark seen, skip rewrite.
- **Monitoring:** alert if 304-rate collapses (mass change or breakage), if validation-failure > 5%,
  or if 429s appear (back off / reduce concurrency).

## Guardrails

- **Cadence = the data's change rate** — re-crawling static data daily wastes load and goodwill.
- **Incremental via conditional GET + sitemap lastmod** — a full re-fetch every run is impolite and slow.
- **Enforce a politeness budget** — concurrency cap, delay, honest UA, honor Retry-After, backoff.
- **Provenance on every record** — source URL + fetch timestamp, or you can't debug or audit it.
- **Dedup/upsert on a stable natural key; content-hash to skip unchanged** — don't duplicate entities.
- **Instrument and alert** — a 429 spike or failure-rate spike is the crawl telling you to adjust.
- **Retrieval-date the site-specific crawl-delay/robots facts** — they change; re-verify at use.
