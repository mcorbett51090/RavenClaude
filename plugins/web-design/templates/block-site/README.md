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
| `block.schema.json` | the shape every `block.json` must have | no |
| `site-manifest.schema.json` | the shape of a site manifest | no |
| `catalog/<id>/block.json` | five exemplar block contracts | copy them for new blocks |
| `catalog.md` | the canonical block list with each block's contract summary | add rows as you add blocks |
| `example.manifest.json` | a one-page manifest using the exemplars | — |
| `gallery.html` | every exemplar at its extremes on `tokens.css` + `layout.css`; open it in a browser | add your blocks |

## The procedure

Each step ends at a gate that must pass before the next one starts.

1. **Copy the kit** into your project, for example `site/`, and load the two stylesheets in this order on every page:
   `<link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="layout.css">`.
2. **Set the brand in `tokens.css`.** Change the colour values (never the role names) and, if you need to, the type
   base, ratios and grid widths (regenerate the scales with knowledge §3).
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py tokens site/tokens.css`. It reads the colour roles from
     the file itself and checks every pairing a block can produce (text 4.5:1, focus ring 3:1), in light and dark. It
     also checks that the two copies of the dark theme match.
3. **Choose blocks from `catalog.md`.** Pick by purpose, never by look. Copy an exemplar `block.json` for each block
   you need and fill in its contract: closed props, every string and list bounded, its slots, media ratios, a11y and
   truth.
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py catalog site/catalog`.
4. **Build each block to the anatomy** (below). Its CSS goes in `@layer blocks`, reads only tokens, never sets grid
   placement, section padding or colours, and changes layout with `@container slot (…)`, never `@media`.
   - **Gate:** add it to your gallery page and run
     `node <plugin>/scripts/device_matrix.mjs --dir site --pages /gallery.html --full --sweep 320:1600:8` until there
     are no findings.
5. **Write the manifest from verified facts** (`site-manifest.schema.json`). Anything you cannot verify goes in
   `ownerTodos`, never in a rendered field. Write image alt text while looking at each image, and give every asset its
   real `width`/`height` and a focal point.
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py manifest site.manifest.json --catalog site/catalog`.
     Read its warnings too: small sources and heavy crops show up there.
6. **Render** the manifest with your framework: one component per block type, in manifest order, `tone` and `space`
   from the manifest or the contract's defaults.
7. **Stress it.** Run `block_site_check.py fixtures site/catalog --out stress.manifest.json` and render those pages
   too. They hold every block at its minimum, its maximum, one unbreakable word at full length, and RTL text.
8. **Prove it.** Run the device matrix on the built site and the stress pages
   (`--dir dist --pages /,/stress/hero-full/max/,… --full --sweep 320:1600:8`), save visual baselines with `--shots`,
   look at element screenshots at 390 and 1280px in both themes, then check on a real iPhone and iPad.
   - **Gate:** zero findings, and the screenshots look right.

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
