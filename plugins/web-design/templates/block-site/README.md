# Block-site starter kit

Build a site from **section blocks**: an agent (or a person) writes a typed manifest, and the blocks own the markup, the
grid and the accessibility structure. Use it when you have no block system yet. A reference renderer turns a manifest
into a static site today; the same contracts and CSS port to Astro, React or anything that renders the anatomy below.

Why blocks: per-site work becomes data entry, and the layout comes out right on every screen because no block decides
its own geometry. The reasoning, the numbers and the pitfalls are in
[`../../knowledge/block-layout-system-2026.md`](../../knowledge/block-layout-system-2026.md).

| File | What it is | Edit per site? |
|---|---|---|
| `tokens.css` | type and space scales, font stacks, grid widths, shape, motion, colour roles, the photo scrim | **values only**: keep the names |
| `layout.css` | the layout contract: page grid, rhythm, tones, primitives, count-aware grid, media frames, text safety, modes | no |
| `blocks.css` | each exemplar block's CSS, keyed by `[data-block]`, plus the site header, menu and footer | add your blocks' CSS |
| `block.schema.json` | the shape every block contract must have | no |
| `site-manifest.schema.json` | the shape of a site manifest: facts, chrome, assets, pages | no |
| `catalog.json` | ten exemplar block contracts, one entry per block | copy entries for new blocks |
| `example.manifest.json` | a three-page site (home, visit, contact) that uses all ten blocks and the site chrome | — |

The tools are in [`../../scripts/`](../../scripts/): `block_site_check.py` (the contract, as exit codes),
`block_site_render.py` (manifest → static HTML), `layout-probe.js` and `device_matrix.mjs` (the rendered page,
measured). The canonical block list is [The block catalog](#the-block-catalog) below.

## Try it in two minutes

```shell
K=<plugin>/templates/block-site; S=<plugin>/scripts
python3 $S/block_site_render.py render $K/example.manifest.json --catalog $K/catalog.json --out /tmp/site --placeholders
python3 -m http.server -d /tmp/site 8000      # open http://localhost:8000
node $S/device_matrix.mjs --dir /tmp/site --manifest $K/example.manifest.json   # needs Playwright
```

`--placeholders` draws a plain gradient where a photo is missing; the example ships no photos. Never publish one.

## The procedure

Every step ends at a gate that must pass before the next one starts.

1. **Copy the kit** into your project, for example `site/`: the three stylesheets, the two schemas and `catalog.json`.
   Pages load the stylesheets in this order: `tokens.css`, `layout.css`, `blocks.css` (the renderer does this).
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py catalog site/catalog.json` passes on the copy.
2. **Set the brand in `tokens.css`.** Change the colour values (never the role names), the font stacks and, if you
   need to, the type base, ratios and grid widths (regenerate the scales with knowledge §3). For a brand web font,
   follow the comment above `--font-body`: `font-display: swap`, one preload, and a metric-matched fallback.
   - **Gate:** `block_site_check.py tokens site/tokens.css`. It reads the colour roles from the file itself (hex,
     `rgb()`, `hsl()`, `oklch()`, `oklab()`) and checks every pairing a block can produce, in light and dark: text
     4.5:1, form-control edges and focus rings 3:1, text in a card on a dark band, and light copy over the photo scrim
     on a white pixel. It also checks that the two copies of the dark theme match, that every type step grows less
     than 2.5× (so 200% zoom works), and that a font stack is set.
3. **Choose blocks from [the catalog](#the-block-catalog).** Pick by purpose, never by look. Copy an exemplar contract
   from `catalog.json` for each block you need and fill it in: closed props, every string and list bounded, its slots,
   media boxes, the facts it `requires`, a11y and truth. A media box's `maxWidth` is the widest the frame is ever drawn,
   at any width and any item count: a photo card in `.cards` is at most half the slot (576px), because an odd last
   photo card keeps a column's width, centred, instead of stretching. A string with a `pattern` needs `examples`
   (values that match), so the fixtures can fill it. Keep the contracts in one `catalog.json`, or split them into
   `catalog/<id>/block.json` beside each component once the catalog grows; the checker reads either form.
   - **Gate:** `block_site_check.py catalog site/catalog.json`. It refuses props it cannot prove closed and bounded
     (`$ref`, `anyOf`, type lists), styling props, and a `variant` written into props.
4. **Build each block to the anatomy** (below): a render function in your project's own `blocks.py` (a `RENDER` dict of block id to function, passed with `--blocks`; it may import the renderer's helpers: `from block_site_render import e, a, picture`), and its CSS in your `blocks.css`. Never edit the
   plugin's scripts: an update replaces them. The CSS goes in
   `@layer blocks`, reads only tokens, never sets grid placement, section padding or colours, and changes layout
   with `@container` queries, never `@media`.
   - **Gate:** the stress pages in step 7 render it, and the device matrix passes on them.
5. **Write the manifest from verified facts** (`site-manifest.schema.json`). Anything you cannot verify goes in
   `ownerTodos`, never in a rendered field. Write image alt text while looking at each image, and give every asset its
   real `width`/`height`, a focal point, smaller `sources` of the same crop for `srcset`, and a `portrait` crop for a
   full-bleed photo that crops badly on a phone. Write the phone as printed, in digits (`(251) 555-0100 ext. 12`):
   every `tel:` link on the site must dial it. Set `lang`; `dir` follows the language's script unless you set it.
   Set `origin` (canonical URLs, JSON-LD and `sitemap.xml`), `basePath` if the site is served under a subpath,
   `shareImage` (an asset with alt, 1200px wide, for link previews) and `icon`. Mark an emergency-only line's hours
   `"kind": "emergency"`: they show under their own heading and are never published as opening hours.
   - **Another language.** The renderer writes some words itself (Menu, Get directions, Call, day and month names,
     Closed, Special days, (required), Skip to content). Give them in the site's language in `strings`, and a page in
     a second language its own `strings` and `alternates` (hreflang). One manifest per language, each with its own
     `basePath` and `chrome`, is the cleaner shape for a whole second-language site.
   - **Gate:** `block_site_check.py manifest site/site.manifest.json --catalog site/catalog.json`. Read its warnings
     too: they include any photo too small, at 2x, for the box it is drawn in, and a non-English page without
     strings.
6. **Render** with `block_site_render.py render site/site.manifest.json --catalog site/catalog.json --blocks
   site/blocks.py --out dist` (the flags go in any order), or with your framework: one component per block type, in manifest order, with `tone` and `space` from
   the manifest or the contract's defaults. The stylesheets come from beside the catalog (your branded copy), and the
   run prints which it used: a line saying "the kit's own" means your brand did not reach `dist`.
   - **Gate:** the renderer runs the manifest check first and refuses on any problem. Before it writes a file it reads
     each page with an HTML parser, the way a browser does, and refuses anything that could run code or reach another
     site unasked (an event handler, `srcdoc`, `<base>`, a meta refresh, a backslash or a scheme other than https,
     mailto and tel in any URL). It then checks its own HTML: one h1, no skipped heading level, unique ids, every
     label and link resolves, every image has alt and dimensions, and the JSON-LD parses with hours that match the
     rows shown. A refusal writes nothing.
   - **`--out` is the renderer's folder.** It records the files it wrote (`.block-site-render.json`), and the next
     render removes those that are gone from the manifest, so an old page never keeps publishing old facts. It never
     touches a file it did not write, and it refuses a folder that already holds files and no record.
   - **Credits.** A photo's `credit` is shown in the footer of each page that shows it. A media frame may list the
     provenances it accepts: the hero takes only `business-own` or `commissioned`, never stock or a generated image
     presented as the place.
7. **Stress it.** `block_site_check.py fixtures site/catalog.json --out stress/stress.manifest.json` writes every
   block at its minimum, its maximum, one unbreakable word at full length, and in Arabic right-to-left. The pages
   carry the longest header and address the schema allows and a near-white stress photo. Render them into their own
   folder, never into `dist`, so they are never published: `block_site_render.py render stress/stress.manifest.json
   --catalog site/catalog.json --blocks site/blocks.py --out stress/dist`.
   - **Gate:** step 8 runs on these pages too.
8. **Prove it.** Two runs:
   - the site, everything: `node <plugin>/scripts/device_matrix.mjs --dir dist --manifest site/site.manifest.json
     --full --sweep 320:1600:8` (5 pages took about 6 minutes);
   - the stress pages, one theme: `node <plugin>/scripts/device_matrix.mjs --dir stress/dist --manifest
     stress/stress.manifest.json --themes light` (48 pages in six themes took 31 minutes; one theme is a sixth).
   Each row's first theme also checks every word for ink (`text-hidden`: covered, masked or faded out), each page
   is laid out once in its print stylesheet, and an image, font or media file that answers 4xx is `resource-failed`
   (`--no-ink` and `--no-print` skip the first two for a quicker look, never for the gate).
   A site with a `basePath` is served and tested only under it, as its host serves it. Save visual baselines with `--shots`, look at element
   screenshots at 390 and 1280px in both themes, then check on a real iPhone and iPad.
   - **Gate:** zero findings, and the screenshots look right. A run that cannot load a page's stylesheet stops with
     a reason instead of measuring the browser's defaults.

## The block catalog

The canonical set of section blocks for small-business and marketing sites. **Ten are written out as exemplar
contracts** in `catalog.json` (marked ✓), each with a render function in `block_site_render.py` and CSS in
`blocks.css`. The others are specified here, so a new contract starts from a decided shape rather than a blank file.
Add a row as you add a block.

How to read a row:
- **Use when / avoid when** is what an agent routes on.
- **Slots** are the grid lines the block's children sit on.
- **Bounds** are the props limits that make its worst case finite and testable.
- **Layout** names the primitive it is built from, which is why it has no in-between broken state.

| Block | Use when / avoid when | Level | Tone (default · allowed) | Slots | Layout | Bounds | Media | Truth |
|---|---|---|---|---|---|---|---|---|
| ✓ `hero-full` | opening statement over a strong photo / no business-own photo → `page-header` | 1 | media (locked) | backdrop, content | copy at the bottom; `min(80svh, 44rem)` with `vh` first | title ≤ 60, lede ≤ 180, ≤ 2 actions | 16/9 full, ≤ 1280×704 at 2x, priority; portrait crop on narrow portrait screens | no stock photo presented as the place |
| `hero-split` | opening statement beside a product or person photo | 1 | canvas · surface | content | switcher at 44rem | title ≤ 60, lede ≤ 200, ≤ 2 actions | 4/5 half-content, priority | as above |
| ✓ `page-header` | an inner page's title and intro / the home page when a photo exists → `hero-full` | 1 | canvas · surface | content | stack | title ≤ 70, intro ≤ 220 | — | — |
| ✓ `features-grid` | 1–6 reasons or offerings / a menu or price list → `price-list` | 2 | canvas · surface | content | count-aware `.cards` | ≤ 6 items; title ≤ 48, body ≤ 160 | optional icon enum | no unsourced awards or ratings |
| ✓ `story-split` | about or history beside a photo / more than 4 short paragraphs | 2 | surface · canvas | content | switcher at 44rem; prose measure | ≤ 4 paragraphs of ≤ 420 | 4/3, ≤ 704px wide (stacked) | no invented origin story |
| ✓ `stats-band` | 2–4 numbers that matter / numbers nobody can source | 2 | canvas · surface · inverse | content | switcher at 36rem (never `auto-grid`) | 2–4 items; value ≤ 8, label ≤ 32, source ≤ 120 | — | every number has a source, shown under it |
| ✓ `testimonial` | one quote with attribution / quotes without permission | 2 | surface · canvas | content | figure at the prose measure | quote ≤ 280, name ≤ 80, context ≤ 80, `permission: true` | — | quoted word for word, with permission, and where and when |
| `price-list` | menu or service prices, exactly as published | 2 | canvas · surface | content | grid with a subgrid row per item; tabular numbers | ≤ 40 items; name ≤ 60, price ≤ 12, note ≤ 120 | — | prices exactly as published, dated |
| `services-list` | 3–8 services with a line each | 2 | canvas · surface | content | count-aware `.cards`, or a two-column subgrid list | ≤ 8 items | optional icon enum | — |
| `team-grid` | people who agreed to be shown | 2 | canvas · surface | content | count-aware `.cards` | ≤ 6 people; name ≤ 48, role ≤ 48, bio ≤ 200 | 1/1 `half-content`, `maxWidth` 600: two to a row at most widths, and an odd last photo card keeps that width, centred | only people who consented; business-own or commissioned photos |
| `gallery-grid` | 3–12 photos of the place or the work | 2 | canvas · surface | wide | `.auto-grid` of frames marked `data-ragged` (no masonry: mixed ratios leave ragged column bottoms) | 3–12 images | 4/3 or 1/1 frames, lazy | business-own photos; alt written while looking |
| ✓ `faq-list` | 3–8 real questions customers ask | 2 | surface · canvas | content | stack of `details`; prose measure | 3–8 items; question ≤ 100, answer ≤ 400 | — | FAQPage JSON-LD only if Google still shows it for the type |
| ✓ `hours-location` | address, hours, special days and directions for a place customers visit / a service-area business → show the area | 2 | canvas · surface | content | switcher at 40rem; hours as a subgrid `dl` with `align-content: start` | heading ≤ 60, note ≤ 160; `requires` address and hours | — | hours from the business's structured hours, the same source as the JSON-LD |
| ✓ `contact-form` | a real, delivered form / no endpoint provisioned yet → say how to reach the business | 2 | surface · canvas | content | stack; prose measure | 1–8 fields from a fixed set; labels ≤ 40 | — | posts to an endpoint the business reads; never promises a reply time; needs a security review |
| ✓ `cta-banner` | one closing action / directly after a hero, or two in a row | 2 | inverse · surface | content | cluster with space-between | heading ≤ 48, label ≤ 28 | — | the action does what its label says (`call` is a `tel:` link) |

The **site header and footer** are not blocks. They come from the manifest's `chrome` (a nav of ≤ 6 links of
≤ 20 characters, one action, ≤ 8 footer links) and its `business` facts, and are the same on every page. The header's
nav becomes a menu below the width its links need. The renderer works that width out from the labels, in rem (so it
moves with a reader's font size) and counting wide glyphs such as Japanese at 1em, and the device matrix's `nav-wrap`
check proves it, header row included.

Rules every block follows (checked by `block_site_check.py` and `layout-probe.js`, not just written here):

1. **At most three variants**, and each is a designed alternative, never a styling switch. A manifest picks one on the
   block instance; props never repeat it.
2. **No styling props:** no colour, size, class, layout, padding or font. Tokens and variants do that.
3. **Every string and list is bounded.** The bounds above are starting points: change them on purpose, then re-run
   the fixtures.
4. **One level-1 block per page, first.** Everything else is level 2.
5. **Media declares its ratio, its slot and the largest box it is drawn in.** Together they decide its frame, its
   `sizes`, and the smallest source that stays sharp at 2x.
6. **A block that renders a business fact `requires` it**, so a page cannot ship an empty hours table.
7. **Links keep their promises.** `linkProps` are checked against the pages and anchors, and a `tel:` link must dial
   the business's phone. `variantLinks` holds a variant to its label (`{"call": "tel:"}`), and `endpointProps` (where
   a form posts) must be https:// or a path, never an `#anchor`.
8. **A figure is never split across lines.** Keep it whole (`white-space: nowrap`) and let its row stack first; the
   probe's `word-broken` check reports one that breaks.

## Block anatomy

```html
<section data-block="features-grid" data-tone="canvas" aria-labelledby="b2-features-grid-h">
  <!-- direct children are SLOTS: each sits on a grid line (content by default) -->
  <div>
    <h2 id="b2-features-grid-h">Why people come back</h2>
  </div>
  <div>
    <!-- a component that queries its container lives INSIDE a slot, never as one -->
    <div class="cards">
      <article class="card stack"><h3>…</h3><p class="muted">…</p></article>
    </div>
  </div>
</section>
```

- `data-block` is the block id from its contract, and `blocks.css` keys on it. `data-tone` is one of `canvas`,
  `surface`, `inverse` or `media`. `data-space` is one of `s` or `l`; absent means `m`. `none` exists only for a
  block whose contract declares it (a band designed to abut its neighbour); a manifest cannot choose it.
- A slot is on `content` by default. Use `data-slot="wide"` or `data-slot="full"` for wider lines, and
  `data-slot="backdrop"` for a photo behind a `media` block.
- A slot may itself be a layout primitive that does not query its own width (a `.switcher`, a `.cluster`). A
  component that does (`.cards`, or anything with an `@container` rule) goes inside a slot, because a container query
  never styles its own container.
- Never put inline padding, margin or a max-width on a slot. Put narrower content, such as prose at a measure, inside
  it.
- The first block on a page renders the only `h1`; every other block renders an `h2`, and `h3` for its items.
- A photo block puts its copy in `.on-photo`, which carries a scrim anchored to the text, and an opaque backplate in
  forced colours.
- Anything inside an inverse or photo band reads the same colour roles as on the page, and the band re-points them,
  so a card or a form field there stays legible.

### A render function

`def b_my_block(props, ctx) -> str` returns the section's inner HTML; the renderer writes the `<section>` with its
`data-*` attributes and `aria-labelledby`. Escape every prop: `e()` for text, `a()` for a quoted attribute value.
`picture()`, `img()`, `icon()` and `phone_text()` are the kit's own helpers, importable the same way. `ctx` holds:

| Key | Value |
|---|---|
| `manifest` | the whole manifest: business facts, assets, chrome |
| `contract` | this block's contract from the catalog (its `media` gives the frame for `picture()`) |
| `variant` | the instance's variant, or the contract's first |
| `hid` | the id this block's heading must carry: the section is `aria-labelledby` it |
| `bid` | this block's short id on the page (`b3`), to prefix any id inside it |
| `lang`, `rtl` | the page's language, and whether it reads right to left |
| `today` | the render date (ISO), for anything dated |
| `ui` | the renderer's own words in the page's language (`strings` over English) |

A `RENDER` entry under an exemplar's id replaces the kit's function for that block, for example a contact form with
fields the exemplar does not offer. Change that block's contract first, so the checker knows its props.

## Proving the kit itself

The kit is tested, not just written:

- `python3 <plugin>/scripts/block_site_check.py --self-test` breaks each contract, manifest and token rule and requires
  it to be reported.
- `python3 <plugin>/scripts/block_site_render.py --self-test` renders the example and every stress page and checks
  the HTML. It also requires each HTML check to fire on a broken copy. CI runs both.
- `node <plugin>/scripts/device_matrix.mjs --self-test` needs Playwright, so it is run by hand. It renders the same
  pages and requires:
  - the example clean at every quick viewport in six themes, plus a sweep;
  - every stress page clean at every quick viewport, photo copy included.

  It plants every defect the probe knows and requires each to be reported. It checks look-alikes that must not be
  reported, and it measures the count-aware card grid at three widths.
