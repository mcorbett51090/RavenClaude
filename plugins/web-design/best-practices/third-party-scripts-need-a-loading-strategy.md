# Every Third-Party Script Needs an Explicit Loading Strategy

**Status:** Absolute rule
**Domain:** Web Design — Performance / third-party hygiene
**Applies to:** `web-design`

---

## Why this exists

A third-party script in `<head>` with no `async` or `defer` attribute blocks the HTML parser until the remote server responds, the script downloads, and it executes. A single analytics or chat script on a slow CDN can add 1–3 seconds to the page's LCP. Third-party scripts are also an attack surface (supply-chain XSS), a GDPR/consent-mode problem, and a common source of CLS when they inject elements above existing content. The plugin's anti-pattern list calls this out explicitly: "Third-party scripts in `<head>` that block render." Every script that isn't first-party needs a deliberate loading decision before it merges.

## How to apply

**Loading strategy decision per script type:**

| Script category | Strategy | Attributes |
|---|---|---|
| Analytics / tracking (non-critical) | `defer` or load after first paint via `type="module"` | `<script defer src="...">` |
| Chat widget | Load after main thread is idle — `requestIdleCallback` or `IntersectionObserver` | Script injected dynamically |
| A/B testing (synchronous variant needed) | Inline minimal sync snippet only; async the rest | `<script>` inline snippet + `<script async>` |
| Web fonts from CDN | `<link rel="preconnect">` + `<link rel="stylesheet">` with `media="print" onload="this.media='all'"` | Prevents render-block |
| Maps / embeds | Load on interaction or `IntersectionObserver` trigger | Facade pattern |
| Tag manager | Defer or async; never synchronous in `<head>` | `<script async>` |

**Third-party script inventory template (one row per script):**

| Script | Purpose | Owner | Consent required? | Loading strategy | CWV impact measured? |
|---|---|---|---|---|---|
| … | … | … | YES/NO | defer/async/lazy/idle | YES: [delta] / NO |

**Do:**
- Measure CWV before and after adding each third-party script (Lighthouse, PageSpeed Insights, or WebPageTest).
- Enforce consent-mode v2 gating: analytics and advertising scripts must not fire until consent is given.
- Add each script to a Content Security Policy `script-src` directive before it ships.

**Don't:**
- Add a third-party script to `<head>` without `async` or `defer`.
- Load a widget "just in case someone clicks it" — use a facade and load on interaction.
- Let the tag manager accumulate scripts indefinitely; audit and retire unused scripts quarterly.

## Edge cases / when the rule does NOT apply

- **Critical A/B experiment variants that require synchronous execution** to avoid a flash of original content: a minimal inline sync snippet is acceptable, but the payload that follows must be async. Document the performance cost and set an expiry date for the experiment.

## See also

- [`../agents/performance-engineer.md`](../agents/performance-engineer.md) — owns the third-party script audit and CWV impact measurement
- [`./perf-keep-inp-under-200ms.md`](./perf-keep-inp-under-200ms.md) — third-party JS is a leading cause of INP degradation

## Provenance

Codifies the anti-pattern "Third-party scripts in `<head>` that block render" from `CLAUDE.md` §4 and house opinion #11 ("Third-party scripts are debt"). Loading-strategy guidance from web.dev/loading-performance and the `third-party-script-hygiene` skill in this plugin. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
