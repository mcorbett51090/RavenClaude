# The block layout system: pixel-perfect on every screen (2026)

> **Dated 2026-10-27.** Built and measured in this plugin, not in a private repo:
> - the starter kit `templates/block-site/` (tokens.css, layout.css, blocks.css, the block and manifest schemas, ten exemplar blocks, a three-page example);
> - `scripts/block_site_check.py` (contract checker and stress fixtures) and `scripts/block_site_render.py` (the reference renderer and its HTML checks);
> - `scripts/layout-probe.js` and `scripts/device_matrix.mjs` (rendered-page checks over the device table, photo contrast included).
>
> Every **[observed]** number came from running those against the kit in headless Chromium on 2026-10-27. Browser versions come from MDN's browser-compat-data, read the same day. WCAG facts come from W3C *Understanding SC 1.4.3* and from Maxwell Barvian, *Addressing Accessibility Concerns With Using Fluid Type* (Smashing Magazine, 2023-11-07), both re-read the same day.
>
> Labels: **[doc]** a primary source states it · **[observed]** measured here · **[inferred]** concluded from those · **[unverified]** not confirmed.
>
> This file backs [`block-composed-site`](../skills/block-composed-site/SKILL.md). Device rules (viewport tag, `svh`, safe areas, targets, input zoom) live in [`adaptive-layout`](../skills/adaptive-layout/SKILL.md) and are not repeated here. Text over photos has its own file: [`text-over-photo-contrast-2026.md`](text-over-photo-contrast-2026.md).

---

## 0. The short version

A block site looks pixel-perfect when **no block decides its own geometry**. Each one has a single job:

| Job | Owned by | Rule |
|---|---|---|
| Where content edges are | the page grid (`layout.css`) | every block's children sit on `content`, `wide` or `full`, so every edge on the page lines up to the pixel |
| How far apart sections are | three rhythm tokens | a block chooses `s`, `m` or `l`, never a padding |
| How big type and space are | fluid scales (`tokens.css`) | `clamp()` with a rem term, max ≤ 2.5× min |
| How a component reflows | its slot's width (container query) | never the viewport's |
| How many columns a card grid has | its item count | bounded lists make every case listable |
| How media sits | an aspect-ratio frame with a focal point | never stretched, `sizes` from the slot |
| What text does at its longest | text-safety rules | long words break, headings balance, prose keeps a measure |
| Colour, dark mode, forced colours, RTL, print | tones and modes in the contract layer | once, for every block |

Then it is **measured**, never assumed:
1. The contract checker.
2. The rendered HTML, checked by the renderer.
3. Stress fixtures generated from the props bounds, rendered.
4. The device matrix: 28 viewports, ±1px around every breakpoint, an 8px sweep, and five themes on the six quick rows. Desktop rows run with
   real scrollbars, and copy over photos is scored on composited pixels.
5. Visual baselines.
6. A look at element screenshots.
7. A real iPhone and iPad.

## 1. The page grid: one set of lines for every block

```css
[data-block] {
  display: grid;
  grid-template-columns:
    [full-start] minmax(var(--_gutter), 1fr)
    [wide-start] minmax(0, var(--_wide-side))
    [content-start] min(100% - 2 * var(--_gutter), var(--content-max))
    [content-end] minmax(0, var(--_wide-side))
    [wide-end] minmax(var(--_gutter), 1fr) [full-end];
}
[data-block] > * { grid-column: content; min-inline-size: 0; container: slot / inline-size; }
```

- **Why the wide tracks fill first.** The grid sizing algorithm grows a non-flexible track to its limit before it expands `fr` tracks. So as the viewport widens, `wide` content grows to its maximum before the outer margins do **[inferred from the algorithm; observed in the kit's first, hand-written gallery page]**.
- **Gutters.** One fluid token: `clamp(1rem, 0.4286rem + 2.8571vw, 3rem)`, which is 16px at 320 and 48px from 1440. It is widened to `max(gutter, env(safe-area-inset-left), env(safe-area-inset-right))`. That is symmetric on purpose, so a notch on one side keeps both margins equal. The insets are zero unless the page asks for the whole screen, so the renderer's viewport tag carries `viewport-fit=cover`, and the header and footer add the top and bottom insets to their own padding: the bands run under the notch and the home indicator, and the content stays out from under them.
- **The slot is a plain wrapper.** A block's direct children are slots, and anything narrower than its line goes inside one: prose capped at a measure, a centred form, a card grid.
  - **[observed]** The device matrix's `off-grid` check caught this in the kit's first, hand-written gallery page. A `.prose` placed directly on the content line made the slot narrower than the line from 874px up, on three blocks.
- **A photo backdrop needs `grid-column: auto`.**
  - An absolutely positioned grid child uses its grid placement as its containing block. With the `content` placement every other child gets, the photo sat inside the content line, and the scrim showed as a grey band in the margins.
  - Auto lines give it the block's padding box **[observed, then fixed in layout.css]**. The probe now requires a `backdrop` or `full` slot to cover its block edge to edge.

## 2. Rhythm and tones

- **Rhythm.** `--section-s`, `--section-m` and `--section-l` are the only vertical padding a block has. They run 32→57px, 48→95px and 64→133px across 320–1440px.
- **Same-tone neighbours share a gap.** `[data-tone=canvas] + [data-tone=canvas]` drops its top padding, so two light blocks in a row are one rhythm step apart, not two.
- **Tones are surfaces chosen per page:** `canvas`, `surface`, `inverse` and `media`. A block never picks a colour. `inverse` re-points `--ink-muted`, `--accent`, `--on-accent` and `--focus` so that everything inside it is legible.
- **No two dark bands in a row.** `inverse` or `media` next to another `inverse` or `media` reads as one band. `block_site_check.py manifest` refuses it.
- **In dark mode a dark band must still read as a band.** `--inverse` steps up to `#23242c` on a `#111216` canvas.

## 3. Fluid type and space

Utopia's linear interpolation, written out so anyone can regenerate the tokens:

```
slope     = (maxPx − minPx) / (maxVw − minVw)          # here minVw 320, maxVw 1440
intercept = minPx − slope × minVw
token     = clamp(minPx/16 rem, intercept/16 rem + slope×100 vw, maxPx/16 rem)
```

```python
# python3 - <<'PY'   (prints the kit's type steps; change base and ratios to taste)
MINVW, MAXVW = 320, 1440
def clamp(lo, hi):
    s = (hi - lo) / (MAXVW - MINVW); i = lo - s * MINVW
    return f"clamp({lo/16:.4f}rem, {i/16:.4f}rem + {s*100:.4f}vw, {hi/16:.4f}rem)"
for step in range(-2, 6):
    name = f"n{-step}" if step < 0 else step          # --step-n2 … --step-5, as in tokens.css
    print(f"--step-{name}: {clamp(16 * 1.2**step, 19 * 1.25**step)};")
# PY
```

- **The rem term is not optional.** A `vw`-only size does not grow with browser zoom.
- **Keep max ≤ 2.5 × min.** Barvian, quoting his conclusion: *"If the maximum font size is less than or equal to 2.5 times the minimum font size, then the text will always pass WCAG SC 1.4.4, at least on all modern browsers"* **[doc]**. The kit's steps run ×1.09 to ×1.46. `test_web_design_checks.py` fails a step over 2.5.
- **Space uses the same interpolation, as multiples of the body step.** Space steps are 0.25×, 0.5×, 0.75×, 1×, 1.5×, 2×, 3×, 4× and 6× (4→4.8px up to 96→114px), so space and type scale together.
- **Line length is a separate decision.** `--measure: 66ch` caps prose. The grid stays wide, and only prose narrows inside its slot.

## 4. Containers and intrinsic primitives

- **Every slot is `container: slot / inline-size`, and so is every child of a switcher or sidebar.** A component's unnamed `@container` query answers to the nearest box that holds it, so the same card grid behaves the same in a full page, half a switcher, a sidebar or an iPhone Duo split window. **[observed]** When `.cards` queried the named slot, three cards in half a switcher laid out as three 167px columns; the probe's adversarial review found it.
- **A container query never styles the container itself.**
  - **[observed]** `.cards` placed directly as a slot was its own container. Its rules on itself never matched, so it stayed one column at 1152px. Its children still matched the 64rem `span` rules, which created zero-width implicit columns and ragged right edges (1123px against 1152px).
  - The fix is a wrapper slot. The probe's `grid-span` check reports zero-width columns between real ones.
- **Primitives, so there are few breakpoints and no in-between states:**

| Primitive | Use for | Why not a breakpoint |
|---|---|---|
| `stack` | vertical flow with one gap | spacing is one variable |
| `cluster` | buttons, tags, meta that wrap | each item sizes to its content |
| `switcher` | 2–4 equal things: all in a row, or all stacked | there is no state where one is squeezed or stranded |
| `with-sidebar` | a fixed side and a fluid main | wraps when main would drop below `--main-min` |
| `auto-grid` | an open-ended list (a 7–12 photo gallery) | fills columns at `--min-col`, but **strands the last item** at in-between widths; mark it `data-ragged` to say that is accepted |
| `frame` | media at a fixed aspect ratio | the box exists before the image loads |

- **[observed]** Three stats in an `auto-grid` laid out 2+1 at 464–669px. A `switcher` has no such state. For a small fixed count, use a switcher or the count-aware grid.
- **A grid stretched by its row shares the extra height between its auto rows.** The hours list sat beside a taller column, and its rows drifted 65px apart. `align-content: start` keeps them together **[observed]**. No probe catches this; the screenshot did.

## 5. Count-aware card grids

Props are closed and bounded, so a card list has a known maximum (six in the kit). Every count can then be laid out on purpose rather than left to `auto-fit`:

| Slot width | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| < 40rem | 1 | 1+1 | 1+1+1 | 1×4 | 1×5 | 1×6 |
| 40–64rem | 1 | 2 | 2+1 (last spans) | 2+2 | 2+2+1 (last spans) | 2+2+2 |
| ≥ 64rem | 1 (centred, 4 of 6 tracks) | 2 | 3 | 2+2 | 3+2 (on 6 tracks) | 3+3 |

- `:has(> :last-child:nth-child(N))` selects a grid by its count.
- Selector support: `:has()` is in Chrome 105, Firefox 121 and Safari 15.4 (Baseline since December 2023) **[doc]**.
- `device_matrix.mjs --self-test` measures all 18 cells **[observed]**.
- **A card alone on a row is a defect.** The probe's `orphan-row` check reports it.

## 6. Media slots

- **Frame first.** `aspect-ratio` on the frame, then the image at `inline-size/block-size: 100%; object-fit: cover; object-position: var(--focal)`.
  - A focal point (`"30% 40%"`) is part of the asset, not of the block.
  - Always set `width` and `height` on the `<img>`, the source pixels, so the space is reserved before it loads.
- **Source size from the drawn box, at 2x.** Each media entry in a contract gives its slot and the largest box it is
  drawn in (`maxWidth`, and `maxHeight` for a band whose height is not set by its ratio). The checker warns when a
  source, enlarged to cover that box at 2x, would be upscaled; the probe measures the same thing on the page.

| Media | Largest box (CSS px) | Minimum source for that crop | `sizes` the renderer writes |
|---|---|---|---|
| full-bleed band (`hero-full`) | 1280 wide (2560 at 2x, a QHD screen at 1x), 704 tall | 2560 × 1408 | `max(100vw, min(80vh, 704px) * <ratio>)` |
| content line | 72rem = 1152 | 2304 wide | `min(72rem, 100vw)` |
| half of a switcher (`story-split`) | **704**: it stacks to the switch point, not to half the line | 1408 wide | `(min-width: 50rem) min(36rem, 50vw), min(704px, 100vw)` |
| third of content | 384, or the switch point when it stacks | 768 wide | `(min-width: 50rem) min(24rem, 33vw), min(<maxWidth>px, 100vw)` |

  - **A cover-cropped band is drawn wider than the viewport on a narrow, tall screen**, because its height sets the
    scale. **[observed]** With `sizes="100vw"` at 481×900, the browser picked the 1280w file for a band drawn
    1252×704, enlarged 1.96×. `sizes` must state the drawn width.
  - Cap density at 2x, as apple.com does (`adaptive-layout`). Above it the eye cannot tell, and the bytes triple.
  - A **portrait crop** (`portrait` on the asset) is served at `(max-width: 30em) and (orientation: portrait)`. It is
    for composition: with the 2x cap, a 2560×1440 band is still sharp on a 390×844 phone (1350 of 1440 source pixels
    tall). An earlier version of the probe said it needed 2025, because it used the phone's full 3x and a
    `naturalWidth` that the browser had already divided by the srcset density. Both are fixed: the probe decodes the
    chosen file to read its real pixels, and caps at 2x.
- **One `fetchpriority="high"`:** the first block's media only (`"priority": true` in its contract). Everything below the fold is `loading="lazy"`.
- **Alt text.** A backdrop under copy that says what matters is decorative (`alt=""`). Any other image needs alt text written while looking at it. The checker refuses empty alt on a content image.

## 7. Typography precision

| Rule | CSS | Support (MDN BCD, 2026-10-27) |
|---|---|---|
| Headings never end on one short word | `text-wrap: balance` on h1–h4, blockquote, figcaption | Chrome 114, Firefox 121, Safari 17.5. Chromium balances ≤ 6 lines, Firefox ≤ 10 **[doc]** |
| Paragraphs avoid orphans | `text-wrap: pretty` on p, li, dd | Chrome 117, Safari 26, **not Firefox** (falls back to plain wrap) **[doc]** |
| A long word cannot widen its track | `overflow-wrap: anywhere` | MDN: with `anywhere`, the break opportunities "are considered when calculating min-content intrinsic sizes"; with `break-word` they "are NOT" **[doc]**. Grid and flex tracks size from min-content, so `break-word` can still widen a track **[inferred; observed: the stress pages' 48-letter word breaks inside a 358px card]** |
| Breaks get hyphens | `hyphens: auto` with `<html lang>` | without the right language, a German word in an English page breaks without a hyphen **[observed]** |
| Prose keeps a readable line | `max-inline-size: 66ch` inside the slot | — |
| No layout shift on font swap | fallback `@font-face` with `size-adjust` (plus `ascent-override` and `descent-override`) | `size-adjust`: Chrome 92, Firefox 92, Safari 17. **`ascent-override`/`descent-override`/`line-gap-override`: Chrome 87, Firefox 89, Safari only in preview** **[doc]**. On Safari only the width is matched, so measure the shift there |
| Font size follows the fallback's x-height | `font-size-adjust: from-font` | Chrome 127, Firefox 118, Safari 17 **[doc]** |
| Optical vertical centring in buttons | `text-box-trim: trim-both` | Chrome 133, Firefox 154, Safari 18.2 (Baseline 2026) **[doc]**. Optional polish |
| Hanging quotes | `hanging-punctuation: first` | Safari only **[doc]** |

- **Preload one font, the one that draws the hero.** Use `font-display: swap` with a metric-matched fallback, or `optional` where any shift is unacceptable.
- **Form text stays at least 16px** (`adaptive-layout` Step 4). The kit's `max(16px, 1rem)` handles it.

## 8. Subpixel and box rules

- **Borders and outlines in px, never rem.** A rem hairline at 110% zoom is 1.1px and paints blurred.
- **Forced colours: outline, not border.** **[observed]** A 1px forced-colours border on the inverse and photo bands shrank their content box and moved every slot inside 1px off the grid line, at every width. An outline with `outline-offset: -1px` draws the same edge and takes no space.
- **`fr` tracks, not percentages.** Three `33.333%` columns plus gaps leave a fractional pixel somewhere. `minmax(0, 1fr)` distributes it.
- **`min-inline-size: 0` on grid items.** A grid item's min-content must never widen the page. The contract sets it on every slot.
- **`scrollbar-gutter: stable` on `html`.** With classic scrollbars, a page that grows a scrollbar no longer shifts sideways by its width (Chrome 94, Firefox 97, Safari 18.2) **[doc]**.
- **`text-size-adjust: 100%`, never `none`.** It stops iOS landscape text inflation without blocking a reader's text scaling.

## 9. Modes, once, in the contract layer

- **Dark.** Tokens are re-pointed under `prefers-color-scheme: dark` and `[data-theme=dark]`. Declare `color-scheme: light dark`.
- **Forced colours** (Chrome 89, Firefox 89, Safari 16 **[doc]**): backgrounds, gradients and shadows disappear. Outlines carry cards, frames and bands, and the photo scrim becomes an opaque `Canvas` backplate behind the copy. **[observed]** Chromium paints text in the forced `color` while `-webkit-text-fill-color` still reports the author's value, so a contrast check must read `color` in this mode.
- **More contrast** (`prefers-contrast: more`): muted ink becomes full ink, and rules and field edges become `currentColor`. **[observed]** Written on a bare `:root`, it lost to the dark theme's `(0,2,0)` selectors and changed nothing in dark mode; the block now repeats those selectors after the dark blocks, and the device matrix runs `contrast` and `contrast-dark` themes.
- **Reduced motion:** animations and transitions reduced to near zero (`0.01ms`, from a layered `!important`). **[observed]** That makes every style change a 0.01ms transition: a script that changes a style and reads it in the same tick reads the old value. The device matrix waits two frames.
- **RTL:** logical properties throughout. Named grid lines mirror on their own, and every block's Arabic `dir=rtl` stress page passes `off-grid` because its slots span the same physical edges **[observed]**.
- **Print:** bands lose their backgrounds and every colour role is re-pointed to black on white, so a muted line from a dark band does not print light grey (1.75:1) on paper. Photos and ghost buttons are hidden, and external links print their URL.

## 10. Proving it: the verification ladder

| Step | Command | Catches |
|---|---|---|
| 1. Contract | `python3 scripts/block_site_check.py catalog <catalog>` | open props, unbounded strings or lists, props it cannot prove closed (`$ref`, `anyOf`, type lists), styling props, a level-1 block not first, broken paths, duplicate ids |
| 2. Tokens | `… tokens tokens.css` | every role pairing in light and dark (text, field edges, focus, cards on dark bands), light copy over the scrim on a white pixel, the 2.5× type bound, a font stack |
| 3. Manifest | `… manifest site.manifest.json --catalog <catalog>` | the single-h1 order, maxPerPage, adjacency, two dark bands, locked tones, missing required facts, props outside bounds, placeholders anywhere a reader sees text (titles, descriptions, chrome), assets, links and anchors, unsafe link schemes, a `tel:` link that does not dial the business's phone, a variant whose link breaks its label's promise (`call` must be `tel:`), a form that posts to an anchor, overlapping hours (overnight windows included), a date not in the calendar, small sources for the drawn box |
| 4. Render | `python3 scripts/block_site_render.py render …` | refuses what step 3 refuses; then one h1 first, no skipped level, unique ids, labels and links resolve, alt and dimensions, escaped props, JSON-LD hours that match the rows |
| 5. Extremes | `… fixtures <catalog> --out stress.manifest.json`, then render | every block at minimum, maximum, one unbreakable word at full length, and RTL, under the longest header and over a near-white photo |
| 6. Device matrix | `node scripts/device_matrix.mjs --dir dist --manifest … --full --sweep 320:1600:8` | the probe at every viewport, ±1px around each `@media` width, an 8px sweep for container-query states, five themes, and photo contrast |
| 7. Baselines | `… --shots baselines/` | visual regression. Diff against baselines made on the same OS and fonts, never across machines |
| 8. Eyes | element screenshots at 390 and 1280px, both themes | what geometry cannot judge |
| 9. Devices | a real iPhone and iPad, or the Xcode simulator | Safari's toolbar, safe areas, dynamic viewport |

**Probe checks** (`layout-probe.js`; each one proven to fire by `device_matrix.mjs --self-test`):

| id | Reports | Usual fix |
|---|---|---|
| `overflow` | painted past the viewport edge, not clipped by an ancestor | `minmax(0, 1fr)`, `min-inline-size: 0`, `overflow-wrap: anywhere` |
| `zoom-out` | the layout viewport is wider than the screen | the same, on whatever forced the width |
| `off-grid` | a slot off its grid line (±1px), a block that is not a grid, a full or backdrop slot that does not cover its block, something inside a slot running into the gutter, or a wrapper with no visible box padding its content off the line | put narrower content inside the slot; never pad or margin a slot |
| `grid-span` | zero-width columns between real ones | the grid is its own container: wrap it in a slot |
| `text-overflow`, `text-clipped` | text outside its box (sideways or downwards), or cut off by its own box | a bounded string, `overflow-wrap: anywhere`, no fixed widths or heights on text |
| `clipped` | text or a control cut off by an ancestor that clips (a card, a frame, a band) | let the box grow; a scroll container is exempt |
| `overlap` | something painted over text or a control, at any scroll position | remove the overlay, or reserve its space |
| `measure` | running text wider than 75ch | `max-inline-size: var(--measure)` (the contract sets it on p, li, dd) |
| `heading-widow` | a heading's last line is one short word | `text-wrap: balance`, or shorten it if balance is already on |
| `target-size` | under 24×24 with a neighbour, or another small target's circle, inside its 24px circle (SC 2.5.8) | `--target-min` |
| `nav-wrap` | a row of nav links broken onto two lines, or the header's brand, nav and action on more than one row | collapse it into a menu below that width (the renderer's breakpoint is in rem, and counts wide glyphs as 1em) |
| `word-broken` | a figure (`$125,000`, `12:30`) or a word no hyphenation can split, broken across lines by `overflow-wrap: anywhere` | give its box room; keep a figure whole (`white-space: nowrap`) and stack its row before it would break |
| `input-zoom` | form text under 16px | `max(16px, 1rem)` |
| `orphan-row` | one narrow item alone on the last row | count-aware grid or switcher |
| `frame-ratio` | a box with an author `aspect-ratio` drawn off it (stretched beside a taller column) | `align-self: start` in a row (the contract sets it for frames in switchers, sidebars and clusters) |
| `image-distorted`, `image-upscaled`, `image-oversized`, `image-gap`, `image-no-size`, `image-broken`, `img-alt` | stretched; blurry or 3× too heavy for its box at 2x (judged on the decoded file the browser chose); not filling its frame; unsized; missing; unlabelled | frame, a candidate and `sizes` for the drawn box, width/height, alt |
| `text-contrast` | text under 4.5:1 (3:1 large) on the flat background it is painted on | the tokens; a band re-points every role |
| `photo-contrast` (device_matrix) | copy over a photo under its bar at the 5th-percentile pixel | the scrim (`--scrim-weak`) |
| `focus-hidden`, `focus-clipped`, `focus-contrast` | no visible focus indicator, one a clipping ancestor cuts off, or one under 3:1 against what it is drawn on | the contract's focus ring; put a linked photo's ring on its frame; `--focus` |
| `field-contrast` | a form control whose edge (border or fill) is under 3:1 against what it sits on (SC 1.4.11) | `--field-border` |
| `anchor-obscured`, `covered` | an in-page link's target, or the page's end, stays under a fixed or sticky bar | `scroll-margin-top`; pad the page's end by the bar's height |
| `layout-shift` | CLS over 0.01, **in 5 of 5 loads** | reserve space; see §11 |
| `font-failed` | a web font failed, or is used but not loaded | the URL, `font-display`, preload |
| `chrome-share` | fixed or sticky bars over 30% of the height | shrink or un-stick on short viewports |

## 11. What the measurements cannot say

- **Headless Chromium sometimes paints a first frame missing some author styles.**
  - In about 4–8% of loads of a clean page, the first frame lacked some author values: a link had `padding: 0px` and `font-size: 16px` where the next frame had 9.29px and 18.57px. That is a CLS of 0.021 **[observed: 1–2 of 24 loads, 2 of 6, and 16 of 16 when a script forced layout at DOMContentLoaded]**.
  - It is not the stylesheet arriving late: `layout.css` finished at about 16ms and first paint came at 72–80ms. A single bundled stylesheet did not change the rate.
  - **The mechanism is not known**, and it is not claimed. A shift the page itself causes repeats on every load, so the runner reloads a page that shifted in fresh contexts. Shifting in 5 of 5 loads is a finding, and fewer is printed as a note with its count.
  - **The rate rises with CPU load.** The rule was 3 of 3 until a self-test, run while two other headless browsers were busy, reached 3 of 3 on a stress page. With the machine quiet, that page shifted in 0 of 12 loads, and its first animation frame already had every author style **[observed]**. The shift was the header's menu button drawn without its padding for one frame (49px, then 108px wide).
- **Geometry cannot judge taste.** The stretched hours rows (§4), and a scrim band visible outside the photo before the backdrop fix (§1), were caught by looking at screenshots. Step 7 is not optional.
- **Contrast over photos** is a different measurement: [`text-over-photo-contrast-2026.md`](text-over-photo-contrast-2026.md).
- **Open and hover states.** Focus is measured: every focusable element is focused and its ring measured. The matrix also runs the probe a second time with every `<details>` open (the site menu, FAQ answers), skipping the checks a dropdown trips by design (overlap, anchors, fixed bars); those findings say "with every `<details>` open". Hover states and dialogs are not rendered: test them as separate states.
- **Copy over photos in forced colours** cannot be scored on pixels: the browser paints glyphs in the forced colour whatever `-webkit-text-fill-color` says, so they cannot be hidden for the capture, and the hide's own computed-style check would still pass **[observed]**. The matrix skips that one measurement in forced colours, and its self-test checks the kit's opaque `Canvas` backplate instead.
- **Chromium is not WebKit.** See `adaptive-layout` Step 7.

## 12. Pitfalls, each one hit while building the kit

1. A forced-colours border moved every slot 1px off the grid. Use an outline (§8).
2. A measure-limited element placed directly on the line made a short slot. It belongs inside the slot (§1).
3. A count-aware grid used as its own container stayed one column, with zero-width implicit tracks (§4).
4. A photo backdrop boxed inside the content line by its grid placement. Use `grid-column: auto` (§1).
5. Three stats in an `auto-grid` stranded the third at mid widths. Use a switcher (§4).
6. A grid stretched by its row spread its rows apart. Use `align-content: start` (§4).
7. **The probe had a hole:** for one round, the count-aware grid never went multi-column and nothing failed. The self-test now asserts the row pattern for every count at three widths (§5). *A green probe is only as good as the states it was shown failing.*
8. `text-size-adjust: none` was in the first draft of the reset. It is `100%` (§8).
9. The first draft of `layout.css` held colour hex values, which this plugin's own hard-coded-colour hook flagged. Values now live in `tokens.css`, which is exempt by name, and the contract in `layout.css` (§0).
10. **The browser repairs broken markup silently, so no rendered-page check sees it.** A scripted edit left one block
    with an unclosed `<div>` and another with a stray `</div>`. The page rendered, and the device matrix passed 201
    states. Prettier's HTML parser refused the file **[observed]**. Run a parser (prettier `--check`, or an HTML
    validator) over generated markup in CI as well as the probe.
11. **`> :is(img, picture > img)` never matches the `img` inside a `<picture>`**: after `>`, the img's parent must be both the backdrop and a picture. The hero photo kept its own ratio and stopped two-thirds of the way down the band on a phone, and nothing failed until a screenshot showed it. Write `> picture > img` as its own selector; `image-gap` now reports it (§6).
12. **`sizes="100vw"` on a cover-cropped band** made the browser choose a file half the size it needed at 481×900 (§6).
13. **A dark band that re-pointed only the text colour** left a card inside it white on white (1.11:1). Bands re-point every role (§9).
14. **`prefers-contrast: more` on a bare `:root`** did nothing in dark mode (§9).
15. **The first device matrix measured a desktop layout no browser draws.** Headless Chromium hides scrollbars, but `scrollbar-gutter: stable` still reserved 15px, so the body was 1265px while `clientWidth` said 1280 and a correct full-bleed element read as overflow. Desktop rows now run with real scrollbars **[observed]**.
16. **The probe excused anything inside an ancestor that clips.** A button cut off by its card, and text spilling 190px out of a fixed-height box, were silent. Only a scroll container excuses clipping now (`clipped`), and text is checked downwards too.
17. **A frame beside taller copy lost its ratio.** In a switcher row, `align-items: stretch` overrides `aspect-ratio`. With four long paragraphs, the story photo's 4:3 frame became a tall sliver that cover-cropped the photo at 2× enlargement. Only the stress fixtures' longest copy showed it **[observed]**. Frames in a row now align to `start`, and `frame-ratio` reports a stretched frame.
18. **Figures split mid-number, and every check passed.** `overflow-wrap: anywhere` lowers a word's min-content to one character, and a switcher's children are size containers, so four `$125,000`-wide figures in a row at 820px broke into `$125,0` / `00` instead of overflowing **[observed]**. Nothing overflowed, so nothing fired. Figures are now `nowrap`, the renderer sets the stats row's `--switch-at` from its longest value, and `word-broken` reports any figure or unhyphenatable word split across lines.
19. **The menu breakpoint was an estimate in px at 0.6em a character.** Japanese labels are 1em a character, so at 1040–1100px the header's action wrapped onto a second row; and a reader's larger default font grew the text but not the px breakpoint. It is now in rem, counts wide glyphs at 1em, and `nav-wrap` checks the header's rows, not only its links. It errs wide: on the example it asks for 46rem where 36.5rem fits **[measured]**, which shows the menu sooner rather than ever wrapping.
20. **True facts rendered untrue.** A phone with an extension (`ext. 12`) dialled `tel:251555010012`; `1-800-FLOWERS` dialled `tel:1800`; a suite number's `#` cut the city off the maps link; a header button kept calling the old number after the facts changed; a `call` button opened a page; a form posted to `#main` **[observed]**. The schema now takes digits only, `tel:` drops the extension the page shows, the maps query is URL-encoded, every `tel:` link must dial the business's phone, a contract's `variantLinks` holds a variant to its promise, and `endpointProps` must be a real endpoint.
21. **Phone numbers reversed on right-to-left pages.** `+1 (251) 555-0100` displayed as `555-0100 )251( 1+`, and a site with `lang: "ar"` and no `dir` rendered left to right **[observed]**. Numbers are isolated with `dir="ltr"`, and `dir` follows the language's script unless the manifest sets it.
22. **The token check read only the first `:root`.** A later `:root { --field-border: #e2e2e6 }` (1.29:1) passed it, and the probe never measured a control's edge **[observed]**. Every `:root` is read in order now, and `field-contrast` and `focus-contrast` measure the rendered page.
23. **The first `focus-contrast` measured every button at 1.00–1.04:1.** Under reduced motion the kit gives every property a 0.01ms transition, the focus outline's colour included, so a read straight after `focus()` returned the transition's start value, the button's own text colour **[observed]**. The probe now finishes the element's running transitions before it reads the ring. Any read of a style that just changed has the same trap.
24. **An 80-character business name pushed the menu button onto a second row** at 320–390px. The new header-row check found it on the stress pages **[observed]**. The brand now starts from zero width and grows to its own width (`flex: 1 1 0; max-inline-size: max-content`), so a long name wraps inside it, beside the menu, and the link is never wider than the name.
25. **The open menu's "Call us" button read ink on the accent, 2.91:1 (1.87:1 in dark).** `.site-nav a { color: inherit }` sits in the `blocks` layer, which beats `.button`'s label colour in `primitives`. No run had ever laid out the open menu, so nothing saw it until the matrix probed every state with its `<details>` open **[observed]**. The nav link rule now skips `.button`. *A state the probe never renders is a state it cannot pass or fail.*

## Sources

- MDN browser-compat-data (`github.com/mdn/browser-compat-data`, main branch, read 2026-10-27), for every version quoted:
  - `css/properties/text-wrap`, `text-wrap-style`, `text-box-trim`, `hanging-punctuation`, `font-size-adjust`, `scrollbar-gutter`, `content-visibility`;
  - `css/at-rules/font-face` (`size-adjust`, the `*-override` descriptors);
  - `css/at-rules/container`;
  - `css/at-rules/media` (`forced-colors`, `prefers-contrast`, `prefers-reduced-motion`, `hover`, `pointer`);
  - `css/selectors/has`, `css/types/length` (container and dynamic viewport units), `css/types/round`;
  - `html/elements/img` (`sizes="auto"`: Chrome 126, Firefox 150, Safari 27 partial, so it is not used as a default).
- MDN, *text-wrap*: the balance line limits (six lines in Chromium, ten in Firefox), read 2026-10-27.
- W3C, *Understanding SC 1.4.3: Contrast (Minimum)*, WCAG 2.2, read 2026-10-27.
- Maxwell Barvian, *Addressing Accessibility Concerns With Using Fluid Type*, Smashing Magazine, 2023-11-07, read 2026-10-27.
- The primitive names (stack, cluster, switcher, with-sidebar, frame) follow Heydon Pickering and Andy Bell's *Every Layout* **[unverified this session: names used as common vocabulary]**. The interpolation follows Utopia (James Gilyead and Trys Mudford) **[unverified this session: the formula above is the math, stated in full]**.
