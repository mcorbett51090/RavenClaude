# Heading Structure Is a Navigation Aid — Never Skip Levels

**Status:** Absolute rule
**Domain:** Web Design — Accessibility / SEO / content
**Applies to:** `web-design`

---

## Why this exists

Headings are the primary navigation mechanism for screen-reader users (H or the heading-level shortcut jumps to the next heading in NVDA, JAWS, VoiceOver). A heading structure that skips levels — `<h1>` directly to `<h3>` with no `<h2>` — breaks that navigation map. It also tells search engines and AI answer engines that the content hierarchy is disordered. The anti-pattern "heading-level skips (h1 → h3 with no h2)" is in `CLAUDE.md` §4. House opinion #10 states "SEO + a11y converge — headings, alt text, semantic structure, link text serve both."

## How to apply

**Heading structure rules:**

1. **One `<h1>` per page** — the page title. Never use `<h1>` for visual emphasis; use CSS.
2. **Never skip a level** — `<h1>` → `<h2>` → `<h3>` in order; `<h3>` may jump back up to `<h2>` or `<h1>` when a section closes, but may not jump *down* by more than one level when opening a new section.
3. **Headings reflect the page's topic outline** — a reader who reads only the headings should understand the page's structure and the relationship between sections.
4. **Do not use headings for visual styling** — if you want large bold text that isn't a structural heading, use `<p class="lead">` or a styled `<span>`, not a heading element.

**Correct example:**

```html
<h1>Authentication Guide</h1>            <!-- page title -->
  <h2>Getting started</h2>              <!-- major section -->
    <h3>Install the SDK</h3>            <!-- sub-section -->
    <h3>Configure credentials</h3>      <!-- sub-section -->
  <h2>OAuth flows</h2>                  <!-- new major section (skip back up is fine) -->
    <h3>Authorization Code + PKCE</h3>
```

**Incorrect example:**

```html
<h1>Authentication Guide</h1>
  <h3>Getting started</h3>   <!-- WRONG — skips h2 -->
    <h5>Install the SDK</h5> <!-- WRONG — skips h4 -->
```

**Automated detection:**

```bash
# Check for heading skips in built HTML
npx axe --tags wcag2a,wcag2aa path/to/page.html
# Or in CI with pa11y:
npx pa11y --standard WCAG2AA https://staging.example.com/
```

**Do:**
- Audit heading structure with a browser extension (Headings Map, axe DevTools) before launch.
- Use ARIA landmarks (`<main>`, `<nav>`, `<aside>`) to complement but not replace heading structure.
- Verify that the heading structure is coherent in the rendered HTML, not just in the source template (CMS components sometimes inject heading levels).

**Don't:**
- Use `<h2>` to make text look large; use typography tokens.
- Nest component-internal headings at levels that conflict with the page-level heading hierarchy.
- Let a component library's default heading levels conflict with the page context — override them explicitly.

## Edge cases / when the rule does NOT apply

- **Rich-text editor output from a CMS**: the editor may generate arbitrary heading levels. Configure the editor to restrict the available heading choices to match the page's expected hierarchy; validate the output in CI.
- **Widget/iframe embeds**: content inside an `<iframe>` has its own heading hierarchy and does not affect the parent page's heading structure.

## See also

- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) — audits heading structure as part of the WCAG review
- [`./reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md) — the parent rule: semantic HTML (including correct heading levels) is the foundation

## Provenance

Codifies the anti-pattern "Heading-level skips (h1 → h3 with no h2)" from `CLAUDE.md` §4 and house opinion #10. WCAG 1.3.1 (Info and Relationships, Level A) and 2.4.6 (Headings and Labels, Level AA). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
