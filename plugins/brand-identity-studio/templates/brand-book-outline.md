# Brand Book — <brand / version / date>

> The **dynamic brand-book hub** outline (not a rotting PDF — the color tokens shown ARE the delegated tokens;
> logo files are downloadable). Compiled by `brand-book-assembly`. **Client-ready is gated**: requires the
> curation + authorship log AND every IP/font claim routed to `security-reviewer`. Not legal advice; prices
> `[unverified]`.

## Header

- **Brand:** _____  · **Version:** 0.__  · **Prepared:** 2026-__-__  · **Owner:** _____
- **Client-ready?** ☐ ready  ☐ pending gates → _list:_ _____
- **Tier:** starter | mid | comprehensive

## 0. How to use this hub

Living document; the token source is authoritative. Depth is declared per section (**deep** vs *direction* vs
*out-of-v1*) so nothing is over-sold.

## 1. Strategy & positioning — **deep**

Positioning statement, value prop, audience, archetype, brand story. _(from `brand-strategy-brief.md`.)_

## 2. Logo suite — **deep**

Primary lockup · secondary/stacked · mark alone · wordmark alone · clear-space (mark-unit) · min-size
(px web / mm print) · mono/one-color · reversed/B&W · **do/don't gallery**. _True SVG; identifiable in B&W._
Downloadable files: _____.

## 3. Color system — **deep**

| Role | HEX | RGB | OKLCH | CMYK (if print) | Validated WCAG pair(s) |
|---|---|---|---|---|---|
| Primary | | | | | fg/bg: __:1 (AA ✓/✗) |
| Secondary | | | | | |
| Accent | | | | | |
| Neutral ramp | | | | | |

_All pairs validated by `check-brand-a11y.py`. A primary text pair <4.5:1 fails the handoff._

## 4. Type system — **deep**

| Family | Role (display/text/mono) | Weights loaded | **Web-license class** | Self-hostable? |
|---|---|---|---|---|
| | | | OFL/Apache · Adobe · Monotype · desktop-only | ✅/❌ |

Modular scale + pairing rules. _(from `font-license-tracker.md`; non-self-hostable fonts blocked from export.)_

## 5. Grid & spacing — *direction*

Layout grid, spacing scale.

## 6. Iconography — *direction*

Icon style, grid, stroke (direction, not full production in v1).

## 7. Imagery direction — *direction*

Photography/illustration style, art direction. _(Generation + indemnity via `generative-web-media`.)_

## 8. Voice & messaging — **deep**

Voice attributes, tone-shift rules, do-say/don't-say, glossary, tagline, messaging hierarchy. _(from
`brand-voice-and-messaging`.)_

## 9. Usage do/don'ts — **deep**

The specific misuse gallery (stretch, recolor, re-space, drop-shadow, low-contrast, wrong lockup).

## 10. Governance, AI-content rules & accessibility — **deep**

- **Governance:** who can change what; versioning.
- **AI-content usage:** how the brand may/may not appear in generated media.
- **Accessibility:** the validated contrast pairs, reduced-motion posture, alt-text expectations.

## Token handoff (delegated)

- **Tokens produced by:** `web-design:design-tokens-scaffolding` (DTCG → Style Dictionary → CSS vars/Tailwind).
  _This plugin builds no token code._
- **Applied to the site by:** `web-design:visual-designer`.
- **Favicon/OG asset set:** see `favicon-og-asset-manifest.md`.

## Legal-sign-off gate (must pass before client-ready)

- [ ] Curation + authorship log exists
- [ ] WCAG pairs validated
- [ ] Font-license classes recorded (non-self-hostable blocked)
- [ ] Every IP/registrability/font-license claim routed to `security-reviewer`

**Out of v1 (declared):** motion/animation system, extensive stationery beyond favicon/OG + basic collateral.

---
_Plus the ravenclaude-core Structured Output block. Not legal advice; prices `[unverified]`. Seams:
`web-design` (tokens + site), `generative-web-media` (imagery), `security-reviewer` (IP claims)._
