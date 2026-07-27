---
name: resilient-extraction-and-parsing
description: "Extract web data defensively — prefer structured data (JSON-LD / microdata / __NEXT_DATA__ / JSON API) over brittle CSS/XPath selectors, anchor selectors on stable attributes with fallbacks, and validate every record to a schema so breakage is DETECTED not silently wrong. Traverses the parse branch of the web-scraping decision tree. Reach for this when the user asks 'build a robust extractor', 'this scraper keeps breaking', 'how do I parse this reliably?', or 'why is my scraped data wrong?'. Used by scraper-implementation-engineer (primary) and extraction-architect."
---

# Skill: resilient-extraction-and-parsing

> **Invoked by:** `scraper-implementation-engineer` (primary — the parser + validation) and
> `extraction-architect` (to judge a target's parse-fragility).
>
> **When to invoke:** "build a robust extractor for this"; "this scraper keeps breaking"; "how do I
> parse this reliably?"; "why is my scraped data silently wrong?"; any "make extraction robust"
> question.
>
> **Output:** a defensive extraction — structured-data-first parsing, selectors anchored with
> fallbacks, and per-record schema validation so breakage surfaces as a detected error.

## Procedure

1. **Reach for structured data before the DOM.** In priority order: (a) the **JSON/XHR API** the
   page calls; (b) **JSON-LD** (`<script type="application/ld+json">`) — often has the clean entity;
   (c) embedded app state (`__NEXT_DATA__`, `__NUXT__`, a `window.__STATE__`); (d) **microdata /
   RDFa / Open Graph** meta. These have a documented-ish shape and survive redesigns that shatter
   CSS selectors.
2. **Fall to selectors only when nothing structured exists — and anchor them.** Prefer stable hooks:
   `id`, `data-*` attributes, ARIA roles, semantic elements. **Avoid** layout-position selectors
   (`div > div:nth-child(3)`) and auto-generated class names (hashed CSS-module names) — they break
   on the next deploy.
3. **Add fallbacks per field.** For each field, try the best source, then a fallback (e.g. JSON-LD
   `price` → `[itemprop=price]` → a labeled selector). A field with one fragile path is a
   single point of failure.
4. **Define the target schema first, and validate every record.** Declare the shape (field names,
   types, required/optional, ranges/formats). Validate each extracted record against it. A record
   that fails validation is **quarantined and alerted**, never written silently — this is the
   difference between "detected breakage" and "a month of wrong data."
5. **Normalize at extraction.** Parse prices/dates/units into canonical types (a `Decimal` price
   with currency, an ISO timestamp), trim whitespace, resolve relative URLs, decode entities.
   Normalize once, at the boundary, so downstream is clean.
6. **Handle the absent and the malformed explicitly.** Missing element ≠ empty string ≠ zero. Decide
   per field whether missing is valid (optional) or a validation failure, and never let a parser
   exception silently drop a whole record without a log.
7. **Make breakage observable.** Track per-run: records extracted, validation-failure rate, and
   empty/near-empty results. A spike means the site changed — that's the signal to fix the selector,
   caught in hours instead of discovered as missing data weeks later.

## Worked example

> User: "My CSS-selector scraper for article metadata keeps breaking every time the site redesigns."

- **Root cause:** selectors anchored on layout/hashed classes — they shatter on redesign.
- **Structured-data-first:** the articles expose **JSON-LD** `NewsArticle` with `headline`,
  `datePublished`, `author` — extract from that instead of the DOM
  *(retrieval-dated 2026-07; JSON-LD presence verified per-site at use)*.
- **Fallback:** for pages missing JSON-LD, fall to Open Graph meta (`og:title`, `article:published_time`),
  then a `[itemprop]` selector — three tiers, not one fragile path.
- **Schema:** `{ headline: str(required), published_at: iso-datetime(required), author: str(optional) }`;
  validate each record; quarantine + alert on failure.
- **Normalize:** parse `datePublished` to a UTC ISO timestamp; trim the headline; resolve author to
  a canonical string.
- **Observability:** alert if validation-failure-rate > 5% or a run returns near-zero records — the
  redesign is now caught the day it ships, not a month later.

## Guardrails

- **Structured data before selectors** — JSON endpoint / JSON-LD / embedded state / microdata first.
- **Anchor on stable attributes** — never layout position or hashed class names.
- **Fallbacks per field** — one fragile path is a single point of failure.
- **Validate to a schema; quarantine failures** — a failed field is detected breakage, not a silent value.
- **Normalize at the boundary** — canonical types once, so downstream is clean.
- **Missing ≠ empty ≠ zero** — decide per field; never drop a record silently on a parser exception.
- **Alert on validation-failure spikes and empty runs** — detect the site change, don't discover it.
