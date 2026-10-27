---
name: block-composed-site
description: Build or extend a website from a catalog of section blocks, so the agent writes a typed manifest instead of markup and the layout is pixel-perfect on every screen. Ships a starter kit (tokens, layout contract, block CSS, schemas, ten exemplar blocks, a three-page example), a reference renderer, and the tools that prove it (contract checker, stress fixtures, layout probe, device matrix with photo contrast). Covers feature-to-block mapping, resolver rules, gates, drift and upgrades. Used by web-architect and frontend-implementer.
---

# Skill: block-composed-site

**Purpose:** make per-site work *data entry* — choosing blocks, variants and real content in one manifest — while a
versioned catalog and a deterministic composer own the markup, the accessibility structure and the upgrades. Primary
agents: `web-architect` (catalog, features, tiers, distribution), `frontend-implementer` (blocks, shell, gates);
`content-strategist` fills the content; `visual-designer` owns the token roles blocks consume.

Backing knowledge:
- [`../../knowledge/block-layout-system-2026.md`](../../knowledge/block-layout-system-2026.md): the layout contract
  that makes a block site pixel-perfect (grid lines, rhythm, fluid scales, containers, count-aware grids, media slots,
  type precision, modes), how each rule is proven, and the pitfalls hit building it.
- [`../../knowledge/block-based-site-composition-2026.md`](../../knowledge/block-based-site-composition-2026.md):
  prior-art data models, principles, architecture, gates, distribution, AI-agent practices, pitfalls, the generation
  projection as built, and a measured per-site cost.

## When to use

- Many sites for many small businesses share the same kinds of sections (hero, menu, services, gallery, events,
  contact, hours) — the agency/factory case.
- A customer buys features or a tier, and what gets built must match what was sold.
- A section fix has to reach sites that already shipped.

Not for: a one-off bespoke site with layouts no block covers (build it directly via `static-site-implementation`), an
app-grade frontend (`frontend-engineering`), or a CMS integration choice (`information-architecture`).

## Where to start

| You have | Start at |
|---|---|
| Nothing yet | **Mode 0**: the starter kit and renderer in this plugin |
| Your own composer and catalog (for example the owner's private site factory) | **Mode A** |
| A catalog to design or extend | **Mode B**, building on the kit's contracts |

Whichever mode you start in, finish with **Prove it**: the same ladder applies to every block site.

## Mode 0: start with no catalog (the starter kit)

[`templates/block-site/`](../../templates/block-site/README.md) is a working, tested starting point: ten exemplar
blocks, their CSS, a three-page example and a reference renderer
([`scripts/block_site_render.py`](../../scripts/block_site_render.py)). Render the example first; it takes two minutes
and shows the whole path working. Then follow the kit's README, which has eight steps with a gate on each:

1. **Copy the kit** (three stylesheets, two schemas, `catalog.json`).
   - **Gate:** `block_site_check.py catalog` passes on the copy.
2. **Brand it** by changing values in `tokens.css`, never role names.
   - **Gate:** `block_site_check.py tokens tokens.css`. It checks every colour pairing a block can produce in light
     and dark, including text in a card on a dark band and light copy over the photo scrim on a white pixel. It also
     checks the 2.5× type-scale bound and that a font stack is set.
3. **Choose blocks by purpose** from [the kit's block catalog](../../templates/block-site/README.md#the-block-catalog),
   and write a closed, bounded contract for each, starting from the exemplars.
   - **Gate:** `block_site_check.py catalog catalog.json` (it also reads a directory of `<id>/block.json`).
4. **Build each new block to the anatomy:**
   - a `<section data-block data-tone data-space>` whose direct children are slots on a grid line;
   - components that query their width inside slots;
   - a render function, and CSS in `blocks.css` (`@layer blocks`) that reads only tokens and uses `@container`
     queries, never `@media`.
5. **Write the manifest from verified facts:** the business, the chrome (nav, header action, footer links), assets
   with real sizes, `srcset` sources and focal points, and pages.
   - **Gate:** `block_site_check.py manifest`, warnings included.
6. **Render** with `block_site_render.py render`, or with your framework's port of it.
   - **Gate:** the renderer refuses a manifest the checker refuses, then checks its own HTML.
7. **Stress it:** `block_site_check.py fixtures` and render those pages too.
8. **Prove it** (below).

## The layout contract: why a block site comes out pixel-perfect

No block decides its own geometry. [`layout.css`](../../templates/block-site/layout.css) owns it in its last cascade
layer, so a block cannot override it by accident:

- **One page grid with named lines** (`full` / `wide` / `content`). Every block's children sit on a line, so every
  content edge on the page aligns to the pixel.
- **Rhythm from three tokens.** Same-tone neighbours share one gap.
- **Fluid type and space** with a rem term, max ≤ 2.5× min, so zoom still works.
- **Slots are containers, and so is every child of a switcher or sidebar.** Components change on the width they
  have, never on the viewport's.
- **Intrinsic primitives** (stack, cluster, switcher, sidebar, frame) instead of breakpoints. Use a switcher, not an
  `auto-grid`, for a few items.
- **Card grids laid out by item count.** Bounded lists make every count a designed case.
- **Media in aspect-ratio frames** with a focal point, a source big enough for its slot at 2x, and `sizes` from the
  slot.
- **Text safety:** `overflow-wrap: anywhere`, balanced headings, a prose measure.
- **Bands re-point every colour role.** A card, a muted line or a form field inside an inverse or photo band reads
  the same roles as on the page and stays legible.
- **Copy over a photo sits on a scrim anchored to it**, at least `--scrim-weak` under every line, with an opaque
  backplate in forced colours.
- **Modes handled once, for every block:** dark, forced colours, more contrast (in dark too), reduced motion, RTL and
  print.

The reasoning and numbers for each rule are in
[`block-layout-system-2026.md`](../../knowledge/block-layout-system-2026.md).

## Prove it: the verification ladder (every mode)

1. **Contract and manifest:** `block_site_check.py catalog`, `manifest` and `tokens`. Each has `--self-test` rows
   proving its rules fire.
2. **The rendered HTML:** `block_site_render.py` checks every page it writes: one h1 and no skipped level, unique ids,
   labels, links and anchors that resolve, alt and dimensions on every image, escaped props, and JSON-LD hours that
   match the rows on the page.
3. **Extremes:** `block_site_check.py fixtures`. Bounded props mean the worst case is finite: every block at its
   minimum, its maximum, one unbreakable word at full length, and RTL, under the longest header the schema allows
   and over a near-white photo.
4. **Device matrix:**
   `node scripts/device_matrix.mjs --dir dist --manifest site.manifest.json --full --sweep 320:1600:8`.
   - **Where it runs:** [`layout-probe.js`](../../scripts/layout-probe.js) at 28 viewports, ±1px around every `@media`
     width and every 8px for container-query states.
   - **Themes:** five on the quick rows (light, dark, forced colours, more contrast, and more contrast in dark).
     Desktop rows run with real scrollbars.
   - **What it reports:**
     - layout: overflow, off-grid slots and content escaping into the gutter, zero-width grid columns;
     - text: overflow (sideways and downwards), text clipped by an ancestor, overlap, widows, the measure;
     - controls: small targets, input zoom, orphan rows, a wrapping nav;
     - images: distorted, upscaled, oversized or gap-showing images, judged against the file the browser chose;
     - contrast: text on flat backgrounds, and copy over photos scored on composited pixels;
     - focus: hidden or clipped focus rings;
     - scrolling and loading: anchors under fixed bars, content left under a bar, repeatable layout shift, failed
       fonts and oversized fixed chrome.
   - The probe itself is proven by `device_matrix.mjs --self-test`. That needs Playwright, so it is run by hand: CI
     runs the Python checks.
5. **Visual baselines:** `--shots DIR`. Diff them against baselines made on the same OS and fonts.
6. **Look.** Take element screenshots at 390 and 1280px in both themes. Geometry checks cannot judge taste. In the
   kit's own build, a photo that stopped short of its band, and a header three rows tall at 320px, were both seen in a
   screenshot first.
7. **Real devices:** an iPhone and an iPad, because Chromium is not WebKit.

## Mode A — Use your own composer and catalog

If the project has a composer (e.g. the owner's `RavenPower-website-factory`: `node scripts/compose-site.mjs catalog |
scaffold | check | build`, brief `briefs/block-site-agent-brief.md`):

1. **Read the catalog first** — features with tier minimums and status, blocks with use-when summaries. A feature marked
   template-only or planned cannot be composed: report it, do not approximate it with other blocks.
2. **Scaffold from the purchased features and tier.** Every content field starts empty, so the check fails until it is
   filled from real facts.
3. **Fill from verified facts only.** Unknowns go to the owner to-do list, never into a rendered field. Write each image's
   alt text while looking at the image. Record each image's provenance (business-own, licensed-stock, generated).
4. **Check until clean** — the composer prints every problem at once. Fix the manifest, never the composer.
5. **Build, then gate the rendered output** (floor, budget, type check, drift, provenance), then the browser pass from
   the [`interface-craft`](../interface-craft/SKILL.md) skill's Step 3 at 390 and 1440 px in both themes. Run the
   device matrix's **photo-contrast** probe on every page with text over a photo. Token pairs cannot score it, and it
   is where both measured builds failed ([`text-over-photo-contrast-2026.md`](../../knowledge/text-over-photo-contrast-2026.md)).
   When dark mode is opt-in through `localStorage`, set the key before the page loads, or every "dark" capture is
   the light theme.
6. **Iterate only in the manifest** (copy length, variant, block order, image focal point) — at most three rounds.
   Never hand-edit a generated file; the next compose overwrites it and the drift check reports it.

**Generating the content with structured outputs** (factory: `compose-site.mjs projection` → generate →
`unproject` → `check`). Fix the structure first: pages, block order, variants. Then generate against a projection
that offers only what a model may write:
- page and block copy;
- the business's copy;
- each existing asset's alt, focal point and credit;
- a title for each card person;
- asset keys as enums.

Facts (name, phone, address, hours, links, brand) are never offered. A value the skeleton set stands, and an inverse
refuses a changed page plan or variant. Then run the full validation. Contract and limits:
[knowledge §7](../../knowledge/block-based-site-composition-2026.md#7-the-generation-projection-as-built).

**Budget for the visual pass.** Two measured builds cost $5.16 (single tier) and $9.74 (growth tier). The visual pass
was about half of each bill and found every real defect. Cache reads were 72–74%, so fewer, larger steps cut the bill
more than a leaner manifest would ([knowledge §8](../../knowledge/block-based-site-composition-2026.md#8-what-one-site-costs-to-build-measured)).

## Mode B — Design or extend a catalog

### B1. The block contract (one `block.json` per block)

| Field | Why |
|---|---|
| `id`, `version` (semver) | A props change is a data-contract change; the lock records versions so a fleet scan can find old copies |
| `summary` | Written for an agent choosing a block — what it is for, when not to use it — kept short like an agent description |
| `headingLevel`, `placement` (`position`, `maxPerPage`, `notAdjacentTo`) | Exactly one level-1 block per page, first, makes the single-h1 and no-skip rules hold by construction |
| `tone` default (+ `locked` for full-bleed photography) | Surfaces are decided at page level; the resolver can refuse two dark bands back to back |
| `props` — a closed JSON Schema | No unknown keys, bounded strings, enums; **no colour, size or class props** |
| `variants` (≤ ~3, designed) | Deliberate alternatives, not a styling escape hatch |
| `assetProps`, `linkProps` | References can be resolved, copied and checked |
| `schemaOrg`, `a11y`, `perf`, `truth` | Each block states what it emits, guarantees, costs and must never invent |

Components read only semantic tokens, use `@container` queries, render inside a shared section frame (which must
**spread the parent's scope attribute** — see the pitfalls), and take the page's heading id so the section is
`aria-labelledby` its own heading.

### B2. Features and tiers

- One catalog of features: pages and blocks each brings, `mustInclude` groups (and `block:variant` gating), required
  data, minimum tier, status, and the vocabulary shared with the pricing/commerce side (same ids, so a customer's purchase
  maps to blocks without a translation table).
- A tier table with **page allowances mirrored from the pricing source of truth**, labelled as a copy.
- A small base set of blocks any site may use (heroes, headers, CTAs); every other block arrives only through a feature.

### B3. The resolver (deterministic, no LLM; prints every problem)

Refuse: unknown or not-ready features; a feature above the tier; more pages than the allowance; a block no enabled
feature brings in; a gated variant without its feature; a purchased feature not delivered; first block not level-1; max
per page; adjacency; two dark bands back to back; invalid or unknown props; dangling asset, link or font references;
palette text pairs below WCAG AA (on the hexes — composited contrast stays a browser job); placeholder text
(`TODO`, `TBD`, lorem ipsum, template braces) in any rendered field. Emit a lock with the catalog version, each block's
version and content hash, the manifest hash and a hash of every kit-owned file.

### B4. Gates (prove each can fail)

- Self-test: for every resolver rule, a must-fail row that breaks only that rule in a copy of a passing fixture and
  asserts the rule is named; catalog must-fail rows (id/dir mismatch, unknown block reference, missing component,
  unsupported schema keyword).
- Coverage: every block is used by an example **that CI builds**, or its component has never been compiled.
- CI composes and builds the examples, then runs rendered-output gates on `dist/` and a drift round-trip
  (hand-edit → detected → re-compose → clean).
- Writer and provenance gate tested against each other when they live in different languages.

### B5. Distribution and upgrades

Pick deliberately (table in the knowledge file). Where site repos are separate and a private package would need auth in
every site's CI, the factory's model works: the site's authored surface is the manifest plus its images; everything else
is regenerated from the kit at a recorded commit, so `build --site <dir>` is a lossless upgrade and the lock's kit-owned
hashes detect hand edits first. Breaking props changes are major versions with a data migration; roll out in rings; a
merge is not a deployment.

## Pitfalls (each one was hit in the factory build or the starter kit)

- **A slot with padding, margin or a max-width** moves that block off the grid line. The probe's `off-grid` check
  reports it. Narrower content goes inside the slot.
- **A component used as its own slot**, such as a `.cards` grid placed directly under the section, never matches its
  own container queries. It stays one column with zero-width implicit tracks, which the probe reports as `grid-span`.
- **A photo backdrop with grid placement** is boxed inside the content line. Use `grid-column: auto`.
- **A forced-colours border** shrinks a band's content box by 1px on every side. Use an outline.
- **`> :is(img, picture > img)`** never matches the `img` inside a `<picture>`: after `>`, the img's parent must be
  both the backdrop and a picture. The hero photo kept its own aspect ratio and stopped two-thirds of the way down the
  band on a phone. Write `> picture > img` as its own selector; the probe's `image-gap` check catches it.
- **`sizes="100vw"` on a cover-cropped band** lies on a narrow, tall screen: the band's height sets the drawn width,
  so the browser picks a file half the size it needs. Give `sizes` the drawn width:
  `max(100vw, min(80vh, 704px) * <ratio>)`.
- **A dark band that re-points only the text colour** leaves a card inside it white text on a white card (1.11:1).
  Re-point every role.
- **`@media (prefers-contrast: more) { :root { … } }`** loses to the dark theme's `(0,2,0)` selectors, so more
  contrast did nothing in dark mode. Repeat the dark selectors after the dark blocks.
- **A reader's reduced-motion setting gives every property a 0.01ms transition**, from a layered `!important` nothing
  can override. A script that changes a style and reads it back in the same tick reads the old value; wait two frames.

- **The frame component drops the scope attribute** → block root styles never match (the hero photo painted behind its
  band). Spread `...rest` onto the frame's root element.
- **The page renderer forces a default tone** → every block's own default surface is overridden. Pass `tone` through
  unset.
- **Dark bands vanish in dark mode** → point them at re-pointed tokens (panel steps up, chrome steps down), not the raw
  night material.
- **Lock keys named after files** → `src/styles/tokens.css` tripped a "key named like a secret" provenance rule. Store
  per-file hashes as `sha256sum`-style strings, not as object keys.
- **Case-insensitive placeholder detection** refuses real copy ("Todos Santos"). Match `TODO`/`TBD`/`XXX` as uppercase
  words.
- **Inherited alt text** describing dishes that are not in the frame. Re-write alt by looking at each photo.
- **A scaffold that adds a second CTA** before an existing one trips the adjacency rule — upgrade the existing block's
  variant instead.
- **A hero scrim sized in percent of the hero** stops below the eyebrow on a phone (measured at 1.25:1 on the kit's own
  example). Anchor a band to the copy (`::before`, `inset-inline: -50vw`, at least 74% under every line) and measure it.
- **Three feature cards strand one on its row** at 669–874px. Choose the column count from the item count.
- **A gate exemption proven only by a self-test** matched a path no real build produces. Prove exemptions on a built
  `dist/`.
- **Printed URLs derived from list position** moved when the list changed. Derive from the name, allow an explicit
  slug, and refuse collisions.
- **A fact written twice** (display hours beside hand-written JSON-LD) drifts. Store it structured once, and derive
  every rendering from it.
