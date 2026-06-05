# Link Text Describes the Destination, Not the Action

**Status:** Absolute rule
**Domain:** Web Design — Accessibility / content
**Applies to:** `web-design`

---

## Why this exists

"Click here", "read more", and "learn more" are the three most useless link texts on the web. A screen-reader user navigating by the links list (Tab or the screen reader's link-list shortcut) hears a sequence of "read more… read more… read more…" with no destination context. A sighted user scanning a page for links encounters the same problem visually. Both WCAG 2.4.4 (Link Purpose in Context, AA) and the SEO discipline require link text that identifies the destination — and "click here" fails both. The anti-pattern is in the `CLAUDE.md` §4 list.

## How to apply

**The test:**

> "If I read only the link text, without any surrounding sentence, do I know where I'll go or what I'll find?"

**Rewrites:**

| Before | After |
|---|---|
| "Click here to learn more" | "Learn how to set up Google SSO" |
| "Read more" | "Read the migration guide for v2" |
| "Download" | "Download the accessibility audit report (PDF)" |
| "This article" | "The Nielsen usability heuristics article" |

**Rules:**
- **Verb + noun** is the pattern: "View pricing", "Download the starter kit", "See the error reference."
- **Distinguish multiple links to different destinations** on the same page — if two links say "Learn more" but go to different pages, both are broken for screen readers.
- **File type and size for downloads**: "Download the Q2 report (PDF, 2.4 MB)" — the user knows what they're getting.
- **Don't repeat the URL** as link text (`https://example.com/pricing`) — it's unreadable aloud.

**Do:**
- Run axe or WAVE to catch duplicate ambiguous link texts programmatically.
- Write link text at PR review time, not as a post-launch a11y fix.
- For icon-only links (social media icons, hamburger menu), add `aria-label` with the destination text.

**Don't:**
- Use "here" as a link word — it places the burden on the surrounding sentence for context, which fails in link-list navigation mode.
- Link a whole paragraph — link only the specific words that identify the destination.
- Use different link texts for the same URL on the same page — pick one and be consistent.

## Edge cases / when the rule does NOT apply

- **"Back" and "Next" navigation in a paginated sequence** with `aria-label` providing the full context ("Previous: Chapter 3", "Next: Chapter 5") — acceptable because the position context is conveyed.
- **`<a>` elements wrapping a full card/tile with a visible heading**: the heading is the effective link text for assistive technology when the card `<a>` uses `aria-labelledby` pointing to the heading.

## See also

- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) — audits link text as part of the WCAG 2.4.4 check
- [`../agents/content-strategist.md`](../agents/content-strategist.md) — writes microcopy including link text

## Provenance

Codifies the anti-pattern "Link text that says 'click here' or 'read more' with no destination context" from `CLAUDE.md` §4. WCAG 2.4.4 Link Purpose (in Context), Level AA (W3C Web Content Accessibility Guidelines 2.2). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
