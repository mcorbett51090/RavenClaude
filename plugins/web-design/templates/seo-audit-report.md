# SEO audit report — [Site]

**Site:** [...]
**Audit scope:** Technical SEO + content SEO
**Auditor:** [...]
**Audit date:** [YYYY-MM-DD]
**Search Console / RUM data:** [Date range covered]

---

## Executive summary

- **Index coverage:** [N] pages indexed / [N] excluded / [N] errors
- **Top issues:** [3-4 highest-impact findings]
- **Recommendation:** Clean | Targeted fixes | Comprehensive remediation
- **Time-to-remediate estimate:** [...]

---

## 1. Crawlability

| Check | Status (✅ / ⚠️ / 🔴) | Notes |
|---|---|---|
| `robots.txt` present + valid | | |
| `robots.txt` doesn't accidentally block critical paths | | |
| `sitemap.xml` referenced from `robots.txt` | | |
| Sitemap URLs all return 200 | | |
| No infinite redirect loops | | |
| No 30x chains > 1 hop | | |
| `<meta name="robots" content="noindex">` not on shipped pages | | |

## 2. Indexability

| Check | Status | Notes |
|---|---|---|
| Canonical URLs declared on every page | | |
| Trailing-slash policy enforced | | |
| URL case-sensitivity enforced (lowercase) | | |
| No duplicate content across URLs | | |
| Locale prefix consistent (if multilingual) | | |

## 3. URL structure + IA

| Check | Status | Notes |
|---|---|---|
| URLs are short and readable | | |
| URLs reflect IA hierarchy | | |
| No stop-words / dates in URLs unless intentional | | |

## 4. Structured data (Schema.org)

| Page type | Schema present | Validates | Notes |
|---|---|---|---|
| Homepage | `Organization` / `WebSite` | | |
| Blog post | `Article` / `BlogPosting` | | |
| Product | `Product` | | |
| FAQ | `FAQPage` | | |
| Service detail | `Service` | | |

## 4b. Answer-engine optimization (AEO — `gold-standard-website-pipeline` G8 proxies)

| Check | Pass / Fail / N/A | Notes |
|---|---|---|
| Content **server-rendered / crawlable without JS execution** (the AEO-critical bar) | | |
| **Deliberate** AI-crawler allow/deny in `robots.txt` (`GPTBot` / `ClaudeBot` / `Google-Extended` / `PerplexityBot`) — a stated policy, not silence | | |
| Question-shaped headings with the answer in the first 1–2 sentences where content is genuinely Q&A-shaped | | |
| `llms.txt` — **insurance, NOT a gate** (no major AI vendor commits to reading it as of 2026; don't penalize absence / over-credit presence) | | |

## 5. Social share (OG + Twitter Card)

| Tag | Present on all pages | Notes |
|---|---|---|
| `<meta property="og:title">` | | |
| `<meta property="og:description">` | | |
| `<meta property="og:image">` (1200×630+) | | |
| `<meta property="og:url">` | | |
| `<meta property="og:type">` | | |
| `<meta name="twitter:card">` | | |
| `<meta name="twitter:title">` | | |
| `<meta name="twitter:description">` | | |
| `<meta name="twitter:image">` | | |

## 6. Internationalization

| Check | Status | Notes |
|---|---|---|
| `<html lang="...">` correct on every page | | |
| `hreflang` declared on multilingual pages | | |
| `hreflang` bidirectional | | |
| `x-default` declared | | |
| Language switcher in nav (not IP-redirect only) | | |

## 7. Performance × SEO

| Check | Status | Notes |
|---|---|---|
| LCP ≤ 2.5s (P75, field data) | | |
| CLS ≤ 0.1 (P75) | | |
| INP ≤ 200ms (P75) | | |
| HTTPS everywhere | | |
| Mobile-friendly | | |

## 8. Content quality (SEO-side)

| Check | Status | Notes |
|---|---|---|
| Each page has unique `<title>` | | |
| Each page has unique meta description | | |
| Heading hierarchy correct (h1 → h2 → h3) | | |
| Internal linking uses descriptive anchor text | | |
| Content matches search intent for target keywords | | |
| No thin content (< 300 words on substantive pages) | | |
| No keyword stuffing | | |
| Featured snippet opportunities tagged | | |

## Index-coverage breakdown (from GSC)

| Status | URL count | Examples |
|---|---|---|
| Valid (submitted + indexed) | | |
| Excluded — discovered but not indexed | | |
| Excluded — alternate page (canonical) | | |
| Excluded — noindex | | |
| Errors — 404 | | |
| Errors — server error (5xx) | | |
| Errors — redirect error | | |

---

## Top 5 fixes (ranked by leverage)

1. **[Fix]** — affects [N pages]; severity [P0/P1]; effort [hrs]
2. ...

## Findings detail

| # | Severity | Area | Page / template | Issue | Remediation | Owner | Target date |
|---|---|---|---|---|---|---|---|

---

**Sources cited:**
- Google Search Console for index coverage + performance
- Google Rich Results Test for structured-data validation
- [Other tooling]

**Auditor sign-off:** [name] — [YYYY-MM-DD]
