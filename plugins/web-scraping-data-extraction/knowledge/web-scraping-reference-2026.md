# Knowledge — Web-scraping & data-extraction reference (2026)

> **Retrieval date:** 2026-07-22 · **Confidence:** High on durable principles, Medium on specifics.
> **This doc names volatile tooling and legal/anti-bot realities — library APIs, site structures,
> ToS terms, and case law move, and legality is jurisdictional. Verify each entry at use.** The
> *principles* (API-first, structured-data-first, be-polite, validate-to-schema) are durable; the
> *tool and legal specifics* below are not. **This is not legal advice.**

A map of the 2026 landscape and how the pieces fit. Pick by fit; re-verify before wiring.

---

## Fetch layer

| Concern | 2026 state (verify at use) | Durable principle |
|---|---|---|
| **HTTP clients** | Mature HTTP clients with connection pooling, HTTP/2, and retry support exist in every ecosystem (e.g. Python `httpx`/`requests`, Node `undici`/`fetch`). | Default to HTTP + a parser; it's cheapest and most stable. |
| **JSON/XHR endpoints** | Most "JS-rendered" pages call a JSON API you can hit directly; find it in the browser network panel. | Prefer the endpoint the page calls over scraping its rendered DOM. |
| **Headless browsers** | Playwright and Puppeteer are the common headless drivers; expensive (CPU/RAM), slower, more brittle than HTTP. This environment ships Chromium + Playwright preconfigured (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) — do **not** run `playwright install`. | Headless is the last resort — only when data genuinely needs JS and no endpoint exists. |

## Parse layer

| Concern | 2026 state (verify at use) | Durable principle |
|---|---|---|
| **HTML parsers** | Robust parsers per ecosystem (e.g. Python `selectolax`/`lxml`/`BeautifulSoup`, Node `cheerio`). CSS-selector and XPath support is standard. | Anchor selectors on stable hooks (`id`, `data-*`, ARIA), never layout position or hashed classes. |
| **Structured data** | JSON-LD (`application/ld+json`), microdata/RDFa, Open Graph meta, and framework state (`__NEXT_DATA__`, `__NUXT__`) are widely present. schema.org vocab is common. | Structured data before selectors — it survives redesigns that break CSS paths. |
| **Validation** | Schema validation is standard (e.g. Python `pydantic`, JSON Schema, Node `zod`). | Validate every record; quarantine + alert on failure = detected breakage, not silent-wrong. |

## Politeness, scheduling & pipeline

| Concern | 2026 state (verify at use) | Durable principle |
|---|---|---|
| **robots.txt** | Standardized directives + crawl-delay; a stated operator preference to respect. | Read and honor robots.txt; a disallow is a signal to seek an API/permission. |
| **Conditional GET** | ETag / `If-None-Match` and `Last-Modified` / `If-Modified-Since` return `304` on unchanged content. | Crawl incrementally; re-fetch only what changed. |
| **Rate limiting / backoff** | Honor `Retry-After`; exponential backoff with jitter on `429`/`5xx`; per-host concurrency + delay. | Politeness is simultaneously ethics and reliability. |
| **Frameworks** | Full crawl frameworks (e.g. Scrapy, Crawlee) bundle scheduling, throttling, and pipelines; roll-your-own is fine for small scopes. | The pipeline is fetch → parse → validate → dedup → store, each stage observable. |
| **Provenance & storage** | Store source URL + fetch timestamp (+ content-hash, run id); upsert on a stable natural key. | Provenance on every record — or you can't debug, audit, or do incremental updates. |

## Legal & anti-bot reality (verify at use; not legal advice)

| Topic | 2026 state (verify at use) | Durable stance |
|---|---|---|
| **Public vs authenticated** | Legality differs sharply between public un-gated content and content behind login/paywall/click-through ToS. Authenticated access is generally a different (higher) legal bar. Jurisdictional. | Public+permitted only by default; auth wall = stop and seek authorization. |
| **Terms of Service** | A ToS that prohibits automated collection turns scraping into a legal question; enforceability is jurisdictional and evolving. | Surface ToS prohibitions; recommend permission/API/counsel — do not engineer around them. |
| **Personal data** | Privacy law (GDPR/CCPA-style) applies to scraped PII regardless of public availability. | Route PII policy to `data-governance-privacy`; minimize and justify. |
| **Copyright** | Wholesale copying of copyrighted content is not "extraction." | Name the copyright issue; extract facts/permitted data, not whole works. |
| **Anti-bot / WAF / CAPTCHA** | Bot-detection is widespread; its presence signals the operator does not want automated access. | Treat as a **stop-and-reassess** signal. **Never** build CAPTCHA-solving, credential stuffing, mass-account creation, or fingerprint-spoofing for prohibited/abusive access. A politeness measure for an authorized target is not evasion. |

---

## What this reference is *not*

- **Not legal advice** — legality is jurisdictional and fact-specific; surface the question and
  recommend counsel for a genuine legal call.
- **Not a data-orchestration guide** — moving/transforming data that already exists in a store is
  `data-orchestration` / `data-streaming-engineering`. This team *acquires* it.
- **Not a privacy-policy authority** — PII handling policy is `data-governance-privacy`.
- **Not a toolkit for evasion** — this team helps with authorized, lawful, good-citizen acquisition
  only; anti-bot systems are a stop sign, not a target.

> Re-verify every tool, ToS, and anti-bot claim above at use. This landscape — technical and legal —
> moves faster than this doc.
