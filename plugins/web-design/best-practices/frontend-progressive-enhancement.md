# Build on a working HTML baseline, then enhance — don't require JS to render

**Status:** Pattern — static-first, HTML-first. The core content and primary actions work without client JS; interactivity is a layer on top, not a prerequisite (house opinions #9, #5).

**Domain:** Architecture / Resilience

**Applies to:** `web-design`

---

## Why this exists

Progressive enhancement is the static-first opinion (#9: SSG > SSR > CSR) applied at the component level: the page is meaningful HTML first, and JavaScript improves it rather than constructing it. This is resilience (the page survives a failed/blocked/slow script, a flaky network, a bot, an AI crawler) and it's performance (less shipped JS is less main-thread work, which is the dominant INP lever). It's also SEO/AEO: crawlers and answer engines extract content from the rendered HTML, and content that only exists after hydration is content they may never see. A form that needs React to submit, a nav that's invisible without JS, a link that's really a `div onClick` — all fail the baseline.

## How to apply

Render real, navigable HTML on the server (or at build); use native form/link/control semantics so the baseline works; then attach JS that enhances the already-working markup.

```html
<!-- Baseline works with zero JS: a real form posts to a real endpoint -->
<form method="post" action="/subscribe">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required autocomplete="email" />
  <button type="submit">Subscribe</button>
</form>
```

```js
// Enhancement layer: intercept ONLY if JS is present; the form already worked without it
const form = document.querySelector("form");
form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  await fetch(form.action, { method: "POST", body: new FormData(form) });
  form.replaceWith(thankYouNode());   // nicer UX, but not required for the action to work
});
```

**Do:**
- Server-render or pre-render the content and primary actions; hydrate only the interactive islands (static-first).
- Use native `<form>`/`<a>`/`<button>` so submit and navigation work before JS loads (semantic-HTML-first, house opinion #5).
- Treat JS as additive: feature-detect, and degrade to the working baseline on failure.

**Don't:**
- Render the whole page from an empty `<div id="root">` + a client bundle when the content is static (the `frontend-implementer` and `web-architect` both flag CSR-for-content).
- Make a link or button out of a `<div onClick>` — it has no baseline behavior (and fails keyboard + a11y).
- Hide primary content behind hydration so crawlers/answer engines can't extract it.

## Edge cases / when the rule does NOT apply

- **App-shell behind auth** where SEO is irrelevant and the whole experience is interactive — CSR is defensible *with a written reason* (house opinion #9), but still keep the auth/error states resilient.
- **Genuinely JS-only capability** (a canvas editor, a real-time collaborative surface) — there's no HTML baseline for the drawing itself, but the page chrome, nav, and fallback message still render without JS.
- **RSC / islands** are the modern middle path — server-render the tree, ship interactivity only where needed.

## See also

- [`./reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md) — native elements are the baseline
- [`./perf-keep-inp-under-200ms.md`](./perf-keep-inp-under-200ms.md) — less JS shipped is less main-thread work
- [`./seo-semantic-structure-and-metadata.md`](./seo-semantic-structure-and-metadata.md) — crawlers/answer engines read the rendered HTML
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Rendering strategy" tree
- [`../knowledge/modern-web-stacks-2026.md`](../knowledge/modern-web-stacks-2026.md) — SSG/ISR/SSR/RSC/CSR/islands trade-offs
- [`../agents/web-architect.md`](../agents/web-architect.md), [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md)

## Provenance

Distilled from house opinions #9 (static-first) and #5 (semantic HTML before ARIA), the `web-architect`/`frontend-implementer` anti-patterns (CSR for a static marketing site; `<div onClick>` as a control), the rendering-model table in `modern-web-stacks-2026.md`, and the AEO extraction note in `answer-engine-optimization-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
