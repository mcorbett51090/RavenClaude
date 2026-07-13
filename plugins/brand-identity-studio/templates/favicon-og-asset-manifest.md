# Favicon / OG Asset Manifest — <brand / date>

> The 2026 minimum favicon + social-share asset set. Specced by `brand-book-assembly`; **generated** via
> `generative-web-media` (or the prompt-pack fallback), from the curated mark. `[verify-at-use]` — platform
> requirements shift; re-confirm sizes at use (favicon.io/tutorials/favicon-sizes; evilmartians.com,
> retrieval 2026-07-13).

## Header

- **Brand:** _____  · **Prepared:** 2026-__-__  · **Source mark:** the curated vector (never a Firefly regen)

## The asset set

| Asset | Size / format | Purpose | Notes | Done |
|---|---|---|---|---|
| `favicon.svg` | SVG, dark-mode via `@media (prefers-color-scheme: dark)` | Modern browsers, scales crisp | The primary favicon | ☐ |
| `favicon.ico` | ICO 16/32/48 | Legacy fallback | Multi-size ICO | ☐ |
| `apple-touch-icon.png` | 180×180 PNG | iOS home-screen | No transparency (iOS fills) | ☐ |
| `icon-192.png` | 192×192 PNG | PWA / Android | In web manifest | ☐ |
| `icon-512.png` | 512×512 PNG | PWA splash / install | In web manifest | ☐ |
| OG image | 1200×630 PNG/JPG | Open Graph share card | Text-safe margins | ☐ |
| Twitter/X card | 1200×675 PNG/JPG | `summary_large_image` | Can reuse OG if ratio OK | ☐ |

## Generation

- **Brief:** author `creative-brief-for-generative-media.md` with `request_kind: "favicon-set"` /
  `"og-image"`, `format_hints` (`mono-safe` for favicons), `indemnity_required` as appropriate.
- **Provider:** chosen by `generative-web-media` per asset (imagery may be Firefly-default for indemnity; the
  **mark** derives from the curated vector, not a regen).
- **Fallback:** if `generative-web-media` is absent, emit the prompt-pack and record provenance manually.

## Wiring notes (handed to `web-design:visual-designer`)

- `<link rel="icon" type="image/svg+xml" href="favicon.svg">` + ICO fallback + apple-touch + manifest icons.
- OG/Twitter meta tags per `web-design`'s OGP best-practice.

## Checklist

- [ ] All 7 assets produced from the curated mark
- [ ] Dark-mode favicon variant included
- [ ] OG/Twitter text within safe margins
- [ ] Provenance recorded in the curation-and-authorship log
- [ ] Handed to `web-design:visual-designer` for site wiring

---
_Plus the ravenclaude-core Structured Output block. Sizes `[verify-at-use]`. The mark comes from the curated
vector; imagery generation + indemnity is `generative-web-media`'s call._
