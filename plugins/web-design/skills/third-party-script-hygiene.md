---
name: third-party-script-hygiene
description: Catalogue and hygiene-audit third-party scripts on a marketing site — performance budget by category (analytics / chat / A/B / fonts / video / social), async-defer patterns, consent-gating (GDPR / CCPA / consent-mode v2), CSP implications, and the periodic re-audit cadence. Every third-party is debt; this skill quantifies it. Reach for this skill before launch, during a Core Web Vitals push, or when adding a new external script. Used by `performance-engineer` (primary) + `web-architect`.
---

# Skill: third-party-script-hygiene

**Purpose:** Catalogue and audit third-party scripts on a marketing site. Quantify the cost (performance, privacy, reliability, security), gate by consent where required, and retire what isn't earning its slot. Used by `performance-engineer` (primary) and `web-architect` (CSP, consent, hosting).

Every third-party script is debt. It costs bytes, blocks the main thread, opens a network dependency the site can't control, exfiltrates user data, complicates CSP, and breaks when the vendor ships a bad release. None of that is acceptance criteria for adding the next one — but most sites add scripts as if they were free. They're not. This skill makes the cost visible.

## When to use

- **Before launch** — every marketing site launch should produce a third-party inventory as a deliverable
- **During a Core Web Vitals push** — third-parties are usually the dominant LCP / INP contributors after image and font optimization
- **When adding a new external script** — the cost analysis happens *before* the `<script>` tag lands in production
- **Periodic re-audit** — at minimum twice a year. Abandoned scripts pile up faster than teams notice.
- **After a vendor incident** — when a third-party causes downtime or a security event, that's the cue to re-audit the rest

## 1. Third-party inventory format

Build the inventory as a table. Every column earns its place:

| Column | Why |
|---|---|
| **Script name** | The product (e.g. "Intercom Messenger") |
| **Vendor** | Legal entity (matters for DPA / privacy) |
| **Purpose** | One sentence — why does this exist on this site |
| **Owner** | Internal team accountable for the value it produces |
| **Consent class** | Strictly necessary / functional / analytics / marketing / personalization |
| **Pages loaded** | All / specific routes (and which ones) |
| **Byte cost** | Compressed transfer size (DevTools Network panel, cold cache) |
| **Main-thread cost** | Total blocking time contribution (Lighthouse → "Reduce the impact of third-party code") |
| **CSP impact** | Required hosts / hashes / unsafe-inline / unsafe-eval requirements |
| **Business value** | Estimated $ value or "decision-supporting" |
| **Replaceable?** | Could a server-side / first-party alternative do the job |
| **Last reviewed** | Date of last hygiene review |

Save this as `docs/third-party-inventory.md` (or equivalent) in the repo. It is the single source of truth for what's loading and why.

## 2. Category budgets

Constraint creates clarity. Default category budgets for a marketing site:

| Category | Default budget | Notes |
|---|---|---|
| **Analytics** | 1 | One tool. Plausible / Fathom / GA4 — pick one. Not all three. |
| **Chat / support** | 1, conditional | Loaded only on pages where it earns its keep; lazy-load on interaction |
| **A/B test / personalization** | 1 | Optimizely / VWO / GrowthBook. Two is paying twice for the same job. |
| **Fonts** | max 2 families | Self-hosted from a CDN edge cache. Variable fonts let one file cover the weight palette. |
| **Video** | 0 default | If used, `<iframe>` for YouTube/Vimeo with `loading="lazy"`, or self-host short clips |
| **Social embeds** | 0 default | Twitter / X / LinkedIn / Instagram embeds are some of the worst offenders — replace with static images linking out |
| **Tag manager** | 0 or 1, with discipline | GTM can hide a dozen scripts behind one tag; if used, the GTM container is itself audited |
| **Ads** | 0 for SaaS marketing | If applicable (publisher), separate budget |
| **Heatmap / session replay** | 0 default | FullStory / Hotjar are heavy + privacy-fraught; only with explicit business case and consent |
| **CRM / marketing automation snippets** | 1 max | HubSpot tracking pixel, Marketo munchkin — one CRM source of truth |

Total third-party byte budget on a marketing page: **≤ 100 KB compressed transfer**. Total third-party main-thread blocking: **≤ 200 ms on a mid-range mobile** (Moto G Power class).

## 3. Loading patterns

The pattern matters as much as the script. From best to worst:

| Pattern | Use for | Mechanism |
|---|---|---|
| **Don't load it** | Strict-not-required scripts | Best optimization is removal |
| **Server-side equivalent** | Analytics (server-side GTM, server-side Plausible proxy) | First-party domain, no client cost |
| **Lazy-on-interaction** | Chat widgets, video embeds | Load when user clicks the button / scrolls to embed |
| **`async` (HTML attr)** | Independent scripts (analytics) | Downloads in parallel, executes ASAP — order not guaranteed |
| **`defer`** | Scripts that need DOM ready, order matters | Downloads in parallel, executes after parse, in order |
| **`type="module"`** | Modern modules | Defers by default |
| **Synchronous `<script>` in body** | Almost never | Blocks rendering at insertion point |
| **Synchronous `<script>` in `<head>`** | Genuinely never | Blocks render before the page paints |

```html
<!-- Good: analytics, async, no dependency on DOM order -->
<script async src="https://plausible.io/js/script.js" data-domain="example.com"></script>

<!-- Good: lazy-on-interaction chat -->
<button id="chat-trigger">Chat with us</button>
<script>
  document.getElementById('chat-trigger').addEventListener('click', () => {
    const s = document.createElement('script');
    s.src = 'https://widget.intercom.io/widget/APP_ID';
    document.head.appendChild(s);
  }, { once: true });
</script>

<!-- Bad: blocking head script -->
<script src="https://example.com/heavyscript.js"></script>
```

### Fonts specifically

- **Self-host via your CDN** (Fontsource for npm-installable Google Fonts, or the foundry's WOFF2 files). Removes the Google Fonts third-party.
- **`font-display: swap`** so text renders immediately with fallback, no FOIT
- **Preload critical fonts** (`<link rel="preload" as="font" type="font/woff2" crossorigin>`) — but only the ones used above the fold
- **Variable fonts** to collapse multiple weight files into one
- **Subset** to only the characters / scripts the site uses

## 4. Consent-gating

EU traffic, California traffic, increasingly Texas / Virginia / Colorado / Connecticut traffic — consent gating is the law, and Google's consent-mode v2 is the implementation target for Google products.

### Consent classes (IAB TCF / GDPR vocabulary)

- **Strictly necessary** — site can't function without it (session, CSRF, language). No consent needed.
- **Functional** — remembers user preferences. Consent typically required outside US.
- **Analytics** — site analytics. Anonymized analytics in some jurisdictions ride under "legitimate interest" (Plausible / Fathom), Google Analytics typically requires explicit consent in EU.
- **Marketing / advertising** — re-targeting, ad pixels. Explicit consent required everywhere meaningful.
- **Personalization** — A/B test, personalization engines. Explicit consent in EU.

### Implementation pattern

1. **Consent banner** loads before any non-strictly-necessary script
2. **Consent state** stored in a cookie / localStorage with version
3. **Scripts read consent state** before activating; otherwise they load in a "default-denied" mode
4. **Consent-mode v2 for Google products** — `gtag('consent', 'default', {...})` before any GA / Ads call
5. **Re-load on consent change** — page reload, or scripts subscribe to the consent event
6. **Audit by jurisdiction** — EU IP → all categories deny-by-default; US IP → privacy-rights model varies by state

```html
<!-- Google consent-mode v2 default -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied'
  });
</script>
<!-- After consent UI captures choice, gtag('consent', 'update', {...}) -->
```

Consent management platform (CMP) options in 2026: Cookiebot, Osano, Iubenda, OneTrust. For lighter-weight sites, a hand-rolled banner backed by a single CMP-format cookie is workable.

## 5. CSP integration

Every third-party adds to the Content Security Policy. The CSP is the security contract:

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'sha256-...' https://plausible.io https://www.googletagmanager.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://plausible.io https://www.google-analytics.com;
  font-src 'self';
  frame-src https://www.youtube.com https://player.vimeo.com;
  report-uri /csp-report;
```

- **Allow-list per third-party** — never `script-src https://*`
- **Hash for unavoidable inline scripts** — `'sha256-<hash>'` is better than `'unsafe-inline'`
- **`unsafe-eval` is a smell** — usually means a script is parsing template strings or using `Function()`; flag the vendor
- **`report-uri` / `report-to`** — collect violations in production; surfaces unexpected scripts that snuck in
- **Audit on every new script addition** — adding a vendor without updating the CSP either breaks the script (better outcome) or means the CSP was already too loose

## 6. CWV impact measurement

Don't take vendors' word for the cost. Measure:

- **WebPageTest filmstrip — with and without the script** — most direct measurement of LCP / CLS / INP impact
- **Lighthouse → Reduce impact of third-party code** — surfaces total blocking time by origin
- **Chrome DevTools Performance tab → bottom-up by URL** — shows main-thread time attributed per script
- **Real-user monitoring (RUM)** — segment p75 LCP / INP by whether the script loaded or not
- **`PerformanceObserver` on long tasks** — log long tasks by attribution URL; build a long-tail view of which third-parties block

A vendor that costs 200ms of main-thread time on a mobile device is a vendor that needs to justify its existence.

## 7. Retirement criteria

A third-party gets retired when:

- **Owner can't articulate the business value** — first sign it's vestigial
- **Usage data shows < N events / month** (chat widget no one chats with, A/B test that hasn't run a test in 6 months)
- **Vendor has had > 1 outage / breach in the past year**
- **Vendor has been acquired** — re-evaluate; acquirer's product roadmap may differ
- **A first-party / server-side alternative is available** — server-side analytics, self-hosted fonts, native lightbox vs vendor widget
- **It's been on the inventory for 12+ months with no review**

The retirement PR includes: removing the `<script>`, removing the CMP entry, removing the CSP entries, removing the vendor from data-processor list, archiving the DPA.

## Hygiene checklist

- [ ] Third-party inventory exists, every column populated
- [ ] Each script has a named internal owner
- [ ] Category budgets defined; current load within budget
- [ ] Total third-party transfer ≤ 100 KB compressed on marketing pages
- [ ] No third-party `<script>` in `<head>` blocking render
- [ ] Chat / heavy widgets lazy-loaded on interaction
- [ ] Fonts self-hosted or via first-party CDN edge cache
- [ ] Consent-mode v2 implemented for Google products (if any)
- [ ] Default-denied for marketing / analytics in EU traffic
- [ ] CSP allow-list current; `report-uri` collecting violations
- [ ] Lighthouse "third-party code" budget verified
- [ ] Periodic re-audit cadence in the calendar (at least every 6 months)
- [ ] Retirement criteria documented; vestigial scripts removed

## Anti-patterns

- **Third-party in `<head>` blocking render** — every marketing site, somehow, still does this. Move to `async` or lazy.
- **No consent gate on EU traffic** — analytics / ad pixels firing pre-consent. Regulatory risk + reputational risk.
- **Abandoned chat widget loading on every page** — costs every visitor; serves none. Retire or lazy-load.
- **Google Tag Manager containing a dozen unaudited tags** — GTM is a Trojan horse for third-parties no one signed off on. Audit the container; treat each tag as its own inventory entry.
- **Two analytics tools "to compare data"** — you'll never reconcile; pick one.
- **Google Fonts loaded directly from `fonts.googleapis.com`** — third-party, blocking, GDPR-fraught. Self-host.
- **YouTube embed in the hero** — 500 KB+ before the user clicks play. Use a lite-embed (just a thumbnail + click-to-load).
- **`unsafe-eval` in the CSP "because the vendor requires it"** — vendor's problem to fix; threaten to replace them.
- **Session replay / heatmap on every page** — heavy + privacy-fraught. Scope to landing pages only, behind consent.
- **A/B test framework loaded synchronously to "avoid flicker"** — the cure is worse than the symptom; use server-side experimentation or a flicker-free client SDK.
- **No periodic re-audit** — scripts accumulate. Without a calendar entry, hygiene rots within a year.

## See also

- Skill: [`./core-web-vitals-tuning.md`](./core-web-vitals-tuning.md)
- Skill: [`./seo-technical-audit.md`](./seo-technical-audit.md)
- Skill: [`./accessibility-review.md`](./accessibility-review.md)
- Template: [`../templates/performance-budget.md`](../templates/performance-budget.md)
- Template: [`../templates/launch-checklist.md`](../templates/launch-checklist.md)
- Agent: [`../agents/performance-engineer.md`](../agents/performance-engineer.md)
- Agent: [`../agents/web-architect.md`](../agents/web-architect.md)
