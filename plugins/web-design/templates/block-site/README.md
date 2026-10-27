# Block-site starter kit

Build a site from **section blocks**: an agent (or a person) writes a typed manifest, and the blocks own the markup, the
grid and the accessibility structure. Use it when you have no block system yet. It is framework-neutral: blocks can
be plain HTML, Astro, React or anything else that renders the anatomy below.

Why blocks: per-site work becomes data entry, and the layout comes out right on every screen because no block decides
its own geometry. The reasoning, the numbers and the pitfalls are in
[`../../knowledge/block-layout-system-2026.md`](../../knowledge/block-layout-system-2026.md).

| File | What it is | Edit per site? |
|---|---|---|
| `tokens.css` | type and space scales, grid widths, shape, motion, colour roles | **values only**: keep the names |
| `layout.css` | the layout contract: page grid, rhythm, tones, primitives, count-aware grid, media frames, text safety, modes | no |
| `block.schema.json` | the shape every block contract must have | no |
| `site-manifest.schema.json` | the shape of a site manifest | no |
| `catalog.json` | the five exemplar block contracts, one entry per block | copy entries for new blocks |
| `example.manifest.json` | a one-page manifest using the exemplars | — |
| `gallery.html` | every exemplar at its extremes on `tokens.css` + `layout.css`; open it in a browser | add your blocks |

The canonical block list, with each block's contract summary, is [The block catalog](#the-block-catalog) below.

## The procedure

Each step ends at a gate that must pass before the next one starts.

1. **Copy the kit** into your project, for example `site/`, and load the two stylesheets in this order on every page:
   `<link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="layout.css">`.
2. **Set the brand in `tokens.css`.** Change the colour values (never the role names) and, if you need to, the type
   base, ratios and grid widths (regenerate the scales with knowledge §3).
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py tokens site/tokens.css`. It reads the colour roles from
     the file itself and checks every pairing a block can produce (text 4.5:1, focus ring 3:1), in light and dark. It
     also checks that the two copies of the dark theme match.
3. **Choose blocks from [the catalog](#the-block-catalog).** Pick by purpose, never by look. Copy an exemplar contract
   from `catalog.json` for each block you need and fill it in: closed props, every string and list bounded, its slots,
   media ratios, a11y and truth. Keep them in one `catalog.json`, or split them into `catalog/<id>/block.json` beside
   each component once the catalog grows; the checker reads either form.
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py catalog site/catalog.json`.
4. **Build each block to the anatomy** (below). Its CSS goes in `@layer blocks`, reads only tokens, never sets grid
   placement, section padding or colours, and changes layout with `@container slot (…)`, never `@media`.
   - **Gate:** add it to your gallery page and run
     `node <plugin>/scripts/device_matrix.mjs --dir site --pages /gallery.html --full --sweep 320:1600:8` until there
     are no findings.
5. **Write the manifest from verified facts** (`site-manifest.schema.json`). Anything you cannot verify goes in
   `ownerTodos`, never in a rendered field. Write image alt text while looking at each image, and give every asset its
   real `width`/`height` and a focal point.
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py manifest site.manifest.json --catalog site/catalog.json`.
     Read its warnings too: small sources and heavy crops show up there.
6. **Render** the manifest with your framework: one component per block type, in manifest order, `tone` and `space`
   from the manifest or the contract's defaults.
7. **Stress it.** Run `block_site_check.py fixtures site/catalog.json --out stress.manifest.json` and render those pages
   too. They hold every block at its minimum, its maximum, one unbreakable word at full length, and RTL text.
8. **Prove it.** Run the device matrix on the built site and the stress pages
   (`--dir dist --pages /,/stress/hero-full/max/,… --full --sweep 320:1600:8`), save visual baselines with `--shots`,
   look at element screenshots at 390 and 1280px in both themes, then check on a real iPhone and iPad.
   - **Gate:** zero findings, and the screenshots look right.

## The block catalog

The canonical set of section blocks for small-business and marketing sites. **Five are written out as exemplar
contracts** in `catalog.json` (marked ✓) and rendered in `gallery.html`. The others are specified here, so a new
contract starts from a decided shape rather than a blank file. Add a row as you add a block.

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

## Block anatomy

```html
<section data-block="features-grid" data-tone="canvas" data-space="m" aria-labelledby="why">
  <!-- direct children are SLOTS: plain wrappers on a grid line (content by default) -->
  <div>
    <h2 id="why">Why people come back</h2>
  </div>
  <div>
    <!-- components that change with their width live INSIDE a slot, never as one -->
    <div class="cards">
      <article class="card stack"><h3>…</h3><p>…</p></article>
    </div>
  </div>
</section>
```

- `data-block` is the block id from its contract. `data-tone` is one of `canvas`, `surface`, `inverse` or `media`.
  `data-space` is one of `s`, `m`, `l` or `none`.
- A slot is on `content` by default. Use `data-slot="wide"` or `data-slot="full"` for wider lines, and
  `data-slot="backdrop"` for a photo behind a `media` block.
- Never put padding, margin or a max-width on a slot. Put narrower content, such as prose at a measure, inside it.
- The first block on a page renders the only `h1`; every other block renders an `h2`, and `h3` for its items.
- A photo block puts its copy in `.on-photo`, which carries a scrim anchored to the text.

## Proving the kit itself

The kit is tested, not just written:

- `python3 <plugin>/scripts/block_site_check.py --self-test` breaks each contract rule and requires it to be reported.
- `node <plugin>/scripts/device_matrix.mjs --self-test` plants every defect the probe knows, requires each one to be
  reported, and requires `tokens.css` + `layout.css` to be clean at every quick viewport in three themes. It also
  measures the count-aware card grid at three widths.
- `gallery.html` passes the full matrix with an 8px sweep (201 page states, 2026-10-27).
