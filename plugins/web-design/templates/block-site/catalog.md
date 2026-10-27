# The block catalog

The canonical set of section blocks for small-business and marketing sites. **Five are written out as exemplar
contracts** in `catalog/` (marked ✓) and rendered in `gallery.html`. The others are specified here, so a new contract
starts from a decided shape rather than a blank file.

How to read a row:
- **Use when / avoid when** is what an agent routes on.
- **Slots** are the grid lines the block's children sit on.
- **Bounds** are the props limits that make its worst case finite and testable.
- **Layout** names the primitive it is built from, which is why it has no in-between broken state.

| Block | Use when / avoid when | Level | Tone (default · allowed) | Slots | Layout | Bounds | Media | Truth |
|---|---|---|---|---|---|---|---|---|
| `site-header` | the page chrome: brand, nav, one action / never per page | — | canvas | content | cluster that wraps; the nav collapses where its links stop fitting (measure it) | ≤ 6 nav links, labels ≤ 20 | brand mark (SVG) | — |
| ✓ `hero-full` | opening statement over a strong photo / no business-own photo → `hero-text` | 1 | media (locked) | backdrop, content | copy at the bottom; `min(80svh, 44rem)` with `vh` first | title ≤ 60, lede ≤ 180, ≤ 2 actions | 16/9 full, priority, portrait crop below 48em | no stock photo presented as the place |
| `hero-split` | opening statement beside a product or person photo | 1 | canvas · surface | content | switcher at 44rem | title ≤ 60, lede ≤ 200, ≤ 2 actions | 4/5 half-content, priority | as above |
| `hero-text` | opening statement with no photo, or for inner pages | 1 | canvas · surface · inverse | content | stack; prose measure | title ≤ 70, lede ≤ 220 | — | — |
| `page-header` | an inner page's title and intro | 1 | surface | content | stack | title ≤ 60, intro ≤ 220 | — | — |
| ✓ `features-grid` | 1–6 reasons or offerings / a menu or price list → `price-list` | 2 | canvas · surface | content | count-aware `.cards` | ≤ 6 items; title ≤ 48, body ≤ 160 | optional icon enum | no unsourced awards or ratings |
| ✓ `story-split` | about or history beside a photo / more than 4 short paragraphs | 2 | surface · canvas | content | switcher at 44rem; prose measure | ≤ 4 paragraphs of ≤ 420 | 4/3 half-content | no invented origin story |
| `stats-band` | 2–4 numbers that matter / numbers nobody can source | 2 | canvas · surface · inverse | content | switcher at 36rem (never `auto-grid`) | 2–4 items; value ≤ 8, label ≤ 32 | — | every number has a source |
| `testimonial` | one quote with attribution / quotes without permission | 2 | surface · canvas | content | prose measure inside the slot | quote ≤ 280, attribution ≤ 80 | optional 1/1 avatar, third-content | quoted with permission, with the source and date |
| `price-list` | menu or service prices, exactly as published | 2 | canvas · surface | content | grid with a subgrid row per item; tabular numbers | ≤ 40 items; name ≤ 60, price ≤ 12, note ≤ 120 | — | prices exactly as published, dated |
| `services-list` | 3–8 services with a line each | 2 | canvas · surface | content | count-aware `.cards`, or a two-column subgrid list | ≤ 8 items | optional icon enum | — |
| `team-grid` | people who agreed to be shown | 2 | canvas · surface | content | count-aware `.cards` | ≤ 6 people; name ≤ 48, role ≤ 48, bio ≤ 200 | 1/1 third-content | only people who consented; business-own or commissioned photos |
| `gallery-grid` | 3–12 photos of the place or the work | 2 | canvas · surface | wide | count-aware grid of frames (no masonry: mixed ratios leave ragged column bottoms) | 3–12 images | 4/3 or 1/1 frames, lazy | business-own photos; alt written while looking |
| `faq-list` | 3–8 real questions customers ask | 2 | surface · canvas | content | stack of `details`; prose measure | 3–8 items; question ≤ 100, answer ≤ 400 | — | FAQPage JSON-LD only if Google still shows it for the type |
| ✓ `hours-location` | address, hours, directions for a place customers visit / a service-area business → show the area | 2 | canvas · surface | content | switcher at 40rem; hours as a subgrid `dl` with `align-content: start` | heading ≤ 60, note ≤ 160 | — | hours from the business's structured hours, the same source as the JSON-LD |
| `contact-form` | a real, delivered form / no endpoint provisioned yet → say so in preview copy | 2 | surface · canvas | content | stack; prose measure | ≤ 8 fields; labels ≤ 40 | — | never claims a reply time the business did not give |
| ✓ `cta-banner` | one closing action / directly after a hero, or two in a row | 2 | inverse · surface | content | cluster with space-between | heading ≤ 48, label ≤ 28 | — | the action does what its label says |
| `site-footer` | contact facts, secondary nav, legal / never per page | — | surface | content | cluster rows | ≤ 8 links | — | facts from the manifest's business |

Rules every block follows (they are checked by `block_site_check.py` and `layout-probe.js`, not just written here):

1. **At most three variants**, and each is a designed alternative, never a styling switch.
2. **No styling props:** no colour, size, class, padding or font. Tokens and variants do that.
3. **Every string and list is bounded.** The bounds above are starting points: change them on purpose, then re-run the
   fixtures.
4. **One level-1 block per page, first.** Everything else is level 2.
5. **Media declares its ratio and slot**, which decide its frame, its `sizes` and its minimum source width.
