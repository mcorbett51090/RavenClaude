---
name: legal-ethical-and-fetch-strategy
description: "Run the legality/ethics gate BEFORE any code (robots.txt, ToS, public-vs-authenticated, rate, PII/copyright), prefer an API/feed/export over scraping, then choose the fetch strategy (HTTP + parser vs headless, JSON-endpoint-first). Traverses the top of the web-scraping decision tree. Reach for this when the user asks 'is it OK to scrape this?', 'should we scrape or is there an API?', 'do we need a headless browser?', or 'how do we do this without getting blocked/sued?'. Legality-first; never evasion for abuse. Used by extraction-architect (primary) and scraper-implementation-engineer."
---

# Skill: legal-ethical-and-fetch-strategy

> **Invoked by:** `extraction-architect` (primary — the gate and the strategy call) and
> `scraper-implementation-engineer` (to confirm the posture before building).
>
> **When to invoke:** "is it OK to scrape this?"; "should we scrape or is there an API?"; "do we
> need a headless browser?"; "how do we do this without getting blocked/sued?"; any "is this
> allowed and how should we fetch it" question.
>
> **Output:** a legal/ethical posture (with concerns named) + a source route (API/feed vs scrape) +
> a fetch strategy (HTTP vs headless) — legality-first, retrieval-dated, **not legal advice**.

## Procedure

1. **Look for a non-scrape source first.** Official **API**, **RSS/Atom feed**, **sitemap**, **bulk
   export/data dump**, or a **licensed dataset**. If one exists and fits the need, recommend it and
   stop — it wins on reliability, legality, and cost. Scraping is the last resort for public,
   permitted data with no better source.
2. **Read `robots.txt`.** Fetch `/robots.txt`, note the directives for your user-agent and the
   crawl-delay (retrieval-dated). It is a stated wish of the site operator; respect it. A disallow
   on the paths you need is a strong signal to seek permission or an API instead.
3. **Read the Terms of Service.** Check whether automated access / data collection is permitted
   (retrieval-dated). A ToS that forbids scraping turns this into a **legal decision**, not a
   technical one — surface it; recommend authorization or counsel. This skill does not route around
   a prohibition.
4. **Establish public vs authenticated.** Public, un-gated content is one posture. Content behind a
   **login, paywall, or click-through ToS** is another — accessing it via automation typically
   requires authorization and may breach the ToS. Do not treat auth as a technical obstacle to
   bypass.
5. **Flag PII and copyright.** If the data includes **personal data**, privacy law applies — route
   policy (lawful basis, retention, minimization) to `data-governance-privacy`. If it's
   **copyrighted content** being copied wholesale, that's not "extraction" — name it.
6. **Treat anti-bot as a stop sign.** If the target runs a bot-detection/WAF/CAPTCHA system, that is
   a **signal to reassess authorization** — is there an API? should we ask permission? — **not** an
   obstacle to defeat. This skill never designs CAPTCHA-solving, credential stuffing, or
   fingerprint-spoofing to bypass a prohibition. (A politeness/reliability measure for an
   *authorized* target — honest UA, honoring `Retry-After`, a session for a licensed API — is fine.)
7. **Choose the fetch strategy — lightest that works.** Default **HTTP + a parser**. Before reaching
   for a **headless browser**, check the network tab for the **JSON/XHR endpoint** the page calls —
   it's usually there, returns clean structured data, and is far more stable and cheaper than the
   rendered DOM. Use headless only when the data genuinely requires JS execution and no endpoint
   exists.

## Worked example

> User: "We want product prices from an e-commerce site. Just scrape it?"

- **Non-scrape source:** check for a **products API**, an affiliate/partner feed, or a Google
  Merchant-style export first *(retrieval-dated 2026-07)*. If the retailer offers a partner API,
  that's the answer.
- **robots.txt / ToS:** read both (retrieval-dated). If the ToS forbids automated price
  collection, surface it as a legal call — recommend a licensed pricing-data provider or direct
  permission.
- **Public vs auth:** prices are public here (no login) — better posture. If they were behind an
  account, stop and reassess.
- **PII:** none in prices — good. (Reviews with usernames would trigger the PII flag.)
- **Anti-bot:** if the site runs an aggressive WAF, that's a stop-and-reassess, not a puzzle —
  prefer the API or a licensed dataset.
- **Fetch strategy:** the price is rendered client-side, but the page calls a `/api/v2/products`
  JSON endpoint — use **HTTP against that endpoint**, not a headless browser scraping the DOM.

## Guardrails

- **API/feed/export before scrape** — if a permitted structured source exists, the scraper is wrong.
- **The legal gate is a gate** — a ToS prohibition or auth wall stops the work; surface it, don't evade.
- **Anti-bot = stop and reassess authorization** — never build evasion for prohibited/abusive access.
- **PII → `data-governance-privacy`; copyright wholesale-copy is not extraction** — name both.
- **HTTP before headless; find the JSON endpoint first** — the browser is the expensive last resort.
- **Retrieval-date robots/ToS/anti-bot facts; this is not legal advice** — recommend counsel for legal calls.
