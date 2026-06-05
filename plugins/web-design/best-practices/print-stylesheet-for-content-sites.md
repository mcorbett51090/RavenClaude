# Ship a Print Stylesheet on Every Content-Heavy Page

**Status:** Pattern
**Domain:** Web Design — Progressive enhancement / print
**Applies to:** `web-design`

---

## Why this exists

A content-heavy page printed without a print stylesheet renders the navigation bar, the sticky header, the chat widget, the cookie banner, the sidebar, and the footer — everything except the article the user wanted to print. The reader gets a multi-page printout where the first page is mostly navigation and the last page is a 50px-tall footer. A print stylesheet is 30–40 lines of CSS that produces a clean, readable printed page. The plugin's house opinion #13 calls it out: "Print stylesheets for content sites." Omitting it on a documentation, blog, or article site is a visible quality gap.

## How to apply

**Minimum print stylesheet:**

```css
@media print {
  /* Hide non-content UI */
  nav, header, footer, aside,
  .cookie-banner, .chat-widget,
  .sidebar, .sticky-header,
  button, [role="navigation"] {
    display: none !important;
  }

  /* Full width, no margins fighting the print margins */
  main, article, .content {
    width: 100%;
    max-width: none;
    margin: 0;
    padding: 0;
  }

  /* Prevent page breaks inside figures and code blocks */
  figure, pre, blockquote, table {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* Expand href for links so the URL is visible in print */
  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: #555;
  }

  /* Except internal/anchor links */
  a[href^="#"]::after,
  a[href^="javascript:"]::after {
    content: "";
  }

  /* Legible font size and black on white */
  body {
    font-size: 12pt;
    color: #000;
    background: #fff;
  }
}
```

**Additional considerations for long-form content:**

```css
@media print {
  h1, h2, h3 {
    page-break-after: avoid;
    break-after: avoid;
  }

  p, li {
    orphans: 3;
    widows: 3;
  }
}
```

**Do:**
- Test the print output: `Ctrl+P` (or `Cmd+P`) in the browser before shipping.
- Use a `@page` rule to set margins if the default browser margins are too aggressive.
- Include the print stylesheet in the base layout so it applies to all content pages automatically.

**Don't:**
- Show navigation, fixed/sticky elements, or interactive widgets in print output.
- Show `href` URLs on anchor links — the fragment tells the reader nothing useful on paper.
- Apply a print stylesheet to single-page apps with no meaningful print surface — focus effort on content pages.

## Edge cases / when the rule does NOT apply

- **Dashboard and application pages**: these are not content pages; a "not intended for print" note is sufficient and a full print stylesheet is unnecessary effort.
- **Pages with sensitive data** that should not be printed: suppress the page entirely with `@media print { body { display: none; } }` and an in-print message.

## See also

- [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md) — implements the print stylesheet
- [`./a11y-respect-motion-and-forced-colors-preferences.md`](./a11y-respect-motion-and-forced-colors-preferences.md) — companion rule: print and reduced-motion are both non-screen media that must not be afterthoughts

## Provenance

Codifies house opinion #13 ("Print and reduced-motion are not afterthoughts — print stylesheets for content sites") from `CLAUDE.md` §3. Print CSS techniques from MDN Web Docs (CSS paged media) and Smashing Magazine. _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
