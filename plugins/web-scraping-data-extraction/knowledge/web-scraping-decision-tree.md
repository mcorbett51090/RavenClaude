# Knowledge — Web-scraping & data-extraction decision trees

> **Last reviewed:** 2026-07-22 · **Confidence:** High on the durable framings (API-before-scrape,
> the legal/ethical gate, structured-data-before-selectors, be-a-polite-client,
> validate-to-a-schema — broad practitioner consensus). **robots.txt/ToS content, anti-bot
> behavior, jurisdictional legality, and library APIs are volatile + site-specific — re-verify
> each at use.**
> The most-asked questions are "is there an API instead?", "is it OK to scrape this?", "HTTP or
> headless?", "how do I parse this so it doesn't break?", and "how often do I re-crawl?". These are
> the trees the team traverses **before** writing a fetcher.

The team's discipline: **name the source (API before scrape), pass the legal/ethical gate before any
code, fetch as lightly as the target allows, parse structured-data-first, and be a polite client.**
This is **not legal advice** — volatile legal/ToS specifics carry a retrieval date and are verified
at use. Moving data that *already exists* leaves this layer for `data-orchestration` /
`data-streaming-engineering`; PII *policy* goes to `data-governance-privacy`.

---

## Decision Tree 1: is there a better source than scraping?

```mermaid
graph TD
  Start([Need this web data]) --> API{Official API exists<br/>and fits the need?}
  API -->|Yes| USEAPI[Use the API — STOP<br/>reliable, permitted, cheap]
  API -->|No| FEED{RSS/Atom feed, sitemap,<br/>bulk export, or dump?}
  FEED -->|Yes| USEFEED[Use the feed/export — STOP]
  FEED -->|No| LICENSED{Licensed dataset /<br/>data provider available?}
  LICENSED -->|Yes and fits| USEDATA[Buy/license the data — often cheapest total]
  LICENSED -->|No| GATE[Proceed to the LEGAL / ETHICAL GATE<br/>Tree 2 — scraping is the last resort]
```

**Rule:** a permitted structured source beats a scraper on reliability, legality, and total cost.
Scrape only public, permitted data with no better source.

---

## Decision Tree 2: the legal & ethical gate (BEFORE any code)

```mermaid
graph TD
  Start([Legal / ethical gate]) --> ROBOTS[Read robots.txt<br/>directives + crawl-delay for your UA<br/>retrieval-dated]
  ROBOTS --> TOS[Read the Terms of Service<br/>is automated collection permitted?<br/>retrieval-dated]
  TOS --> TOSQ{ToS forbids scraping?}
  TOSQ -->|Yes| STOP1[STOP — legal decision<br/>seek permission / an API / counsel<br/>do NOT engineer around it]
  TOSQ -->|No| AUTH{Behind login / paywall /<br/>click-through ToS?}
  AUTH -->|Yes| STOP2[STOP & reassess<br/>authenticated access usually needs authorization<br/>do NOT treat auth as an obstacle]
  AUTH -->|No, public| PII{Contains personal data?}
  PII -->|Yes| PRIV[Flag PII → data-governance-privacy<br/>lawful basis, minimization, retention]
  PII -->|No| COPY{Wholesale copy of<br/>copyrighted content?}
  PRIV --> COPY
  COPY -->|Yes| STOP3[Not extraction — name the copyright issue]
  COPY -->|No| BOT{Anti-bot / WAF / CAPTCHA present?}
  BOT -->|Yes| STOP4[STOP SIGN — reassess authorization<br/>prefer API / permission<br/>NEVER build evasion for abuse]
  BOT -->|No| PASS[Gate passed → Tree 3 fetch strategy<br/>with a politeness budget]
```

**The gate is a gate.** A ToS prohibition, an auth wall, a wholesale-copyright issue, or an
aggressive anti-bot system stops the work and gets *surfaced* — this team does not design evasion
for prohibited or abusive access. A politeness/reliability measure for an **authorized** target
(honest UA, honoring `Retry-After`, a session for a licensed API) is **not** evasion.

---

## Decision Tree 3: fetch strategy — lightest that works

```mermaid
graph TD
  Start([How to fetch?]) --> JS{Does the data need<br/>JS execution to appear?}
  JS -->|No, in the HTML| HTTP[HTTP + parser<br/>cheapest, fastest, most stable]
  JS -->|Yes, rendered client-side| XHR{Is there a JSON/XHR endpoint<br/>the page calls?}
  XHR -->|Yes almost always| ENDPOINT[HTTP against the JSON endpoint<br/>clean structured data, stable]
  XHR -->|No, truly needs the DOM| HEADLESS[Headless browser — LAST RESORT<br/>expensive, slower, more brittle]
  HTTP --> POLITE[Apply the politeness budget<br/>UA, delay, concurrency, backoff]
  ENDPOINT --> POLITE
  HEADLESS --> POLITE
```

**Order:** HTTP → JSON endpoint → headless. The browser is the expensive last resort; the JSON the
page already calls is usually right there and far more stable than the rendered DOM.

---

## Decision Tree 4: parse strategy — structured-data-first

```mermaid
graph TD
  Start([Extract fields]) --> STRUCT{Structured data present?}
  STRUCT -->|JSON API response| S1[Parse the JSON — best]
  STRUCT -->|JSON-LD script| S2[Parse JSON-LD entity]
  STRUCT -->|__NEXT_DATA__ / app state| S3[Parse embedded state]
  STRUCT -->|microdata / OG meta| S4[Parse itemprop / og:*]
  STRUCT -->|None| SEL[CSS/XPath selectors — last resort]
  SEL --> ANCHOR[Anchor on stable hooks<br/>id, data-*, ARIA, semantic tags<br/>NOT nth-child / hashed classes]
  ANCHOR --> FALL[Add per-field fallbacks]
  S1 --> VAL
  S2 --> VAL
  S3 --> VAL
  S4 --> VAL
  FALL --> VAL[Validate every record to a schema<br/>quarantine + alert on failure<br/>= detected breakage, not silent-wrong]
```

---

## Decision Tree 5: schedule & change-detection

```mermaid
graph TD
  Start([Keep it fresh]) --> RATE{How often does the<br/>data actually change?}
  RATE -->|Prices/stock| FAST[Hourly–daily]
  RATE -->|Catalog/reference| SLOW[Weekly–monthly]
  FAST --> INC
  SLOW --> INC[Incremental crawl<br/>conditional GET ETag/If-Modified-Since<br/>sitemap lastmod, per-URL state]
  INC --> POLITE[Politeness budget<br/>concurrency cap, delay, Retry-After, backoff]
  POLITE --> PIPE[Pipeline: fetch → parse → validate → dedup → store<br/>provenance: source URL + fetch timestamp<br/>upsert on stable natural key]
  PIPE --> MON[Instrument + alert<br/>304-rate, validation-failure rate, 429s]
```

---

## Seams to adjacent plugins

| If the question is… | It belongs to… |
|---|---|
| Move/transform/orchestrate data that **already exists** in a store | `data-orchestration` |
| Real-time streaming ingestion of an existing event source | `data-streaming-engineering` |
| Privacy **policy** for collected personal data (lawful basis, retention) | `data-governance-privacy` |
| Design/consume a first-party **API** (the thing you'd rather use than scrape) | `api-engineering` |
| A generic backend service unrelated to acquisition | `backend-engineering` |
| A genuine **legal** determination | a lawyer — this team surfaces it, retrieval-dated, not legal advice |

This team owns **acquiring** web data — lawfully, robustly, and politely — and turning it into
validated structured records.
