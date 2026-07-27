# web-scraping-data-extraction

A **web-scraping & data-extraction engineering team** for RavenClaude — the team that owns
*acquiring* data from the web (sites, APIs, feeds, documents) and turning it into clean, structured,
validated records. Legality and good-citizenship come first; robustness and cost-fit come next.

## Who this is for

- Data/backend engineers building an ingestion pipeline whose *source* is the web.
- Anyone deciding whether to scrape at all (vs an API/feed/export), and how to do it lawfully and
  robustly.
- Teams whose scrapers keep breaking, getting blocked, or producing silently-wrong data.

## Legality first

This team helps with **authorized, lawful, good-citizen** data acquisition. It leads with the
robots.txt / ToS / rate / public-vs-authenticated / PII posture **before** any code, prefers an
official API or licensed dataset over scraping, and treats anti-bot systems as a **signal to stop
and reassess authorization — never an obstacle to evade for abuse**. It does not build
CAPTCHA-solving, credential stuffing, or fingerprint-spoofing to bypass a prohibition. Volatile
legal/ToS specifics are retrieval-dated and verified at use; this is **not legal advice**.

## Agents

| Agent | Owns | Reach for it when |
|-------|------|-------------------|
| **extraction-architect** | The decisions — API-vs-scrape, the legal/ethical posture, fetch strategy (HTTP vs headless), change-detection & scheduling, and whether a target should be scraped at all | "Should we scrape this or is there an API?" · "Is scraping this allowed?" · "HTTP or headless browser?" · "How often should we re-crawl?" |
| **scraper-implementation-engineer** | The build — resilient fetchers/parsers, the extraction-to-schema pipeline (validation, dedup, storage, provenance), polite rate-limiting/backoff, breakage monitoring | "Build a robust extractor for this page" · "This scraper keeps breaking — make it resilient" · "Set up the extraction pipeline with validation" · "Add polite rate-limiting/backoff" |

## Skills

- **legal-ethical-and-fetch-strategy** — run the legality/ethics gate and choose the fetch strategy
  (API/feed first; HTTP before headless; find the JSON endpoint).
- **resilient-extraction-and-parsing** — extract defensively (structured data over selectors),
  validate to a schema, and make breakage detectable.
- **crawl-scheduling-and-pipeline** — change-detection, incremental re-crawl scheduling, and the
  extraction-to-storage pipeline with provenance.

## Knowledge bank

- [`knowledge/web-scraping-decision-tree.md`](knowledge/web-scraping-decision-tree.md) — a Mermaid
  decision tree from "is there an API?" through the legal gate, fetch strategy, parse strategy, and
  scheduling.
- [`knowledge/web-scraping-reference-2026.md`](knowledge/web-scraping-reference-2026.md) — a dated
  reference of the 2026 tooling/legal landscape (parsers, headless browsers, robots/ToS, anti-bot
  reality) with retrieval-date + verify-at-use discipline.

## Boundaries

This team owns **acquiring** web data. Moving/transforming data that already exists →
`data-orchestration` / `data-streaming-engineering`. Generic services → `backend-engineering`.
Privacy *policy* for collected PII → `data-governance-privacy`. Legal questions → a lawyer; this
team surfaces them, retrieval-dated, and does not give legal advice.

## Requires

`ravenclaude-core@>=0.7.0`. No external runtime dependencies mandated. Legal/ToS/tooling specifics
are volatile — the reference doc is retrieval-dated; verify at use.

## Install

```
/plugin marketplace update ravenclaude
/plugin install web-scraping-data-extraction@ravenclaude
```
