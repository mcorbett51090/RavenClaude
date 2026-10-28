/* layout-probe.js: measure a RENDERED page for the defects that stop a block
 * site looking pixel-perfect. Dependency-free; it runs in any browser context:
 *
 *   Playwright:   await page.evaluate(fs.readFileSync(probe, 'utf8') + ';layoutProbe(' + JSON.stringify(opts) + ')')
 *   DevTools MCP: evaluate_script with the file's text plus `;layoutProbe({})`
 *   A console:    paste the file, then `await layoutProbe()`
 *
 * It is async (it decodes each image's file to learn its real pixel size) and it
 * scrolls the page and moves focus to test what a reader would meet; it puts the
 * scroll position and focus back when it is done.
 *
 * scripts/device_matrix.mjs runs it at every viewport, theme and breakpoint edge.
 * Every check reads the live layout (getBoundingClientRect, getComputedStyle,
 * Range rects, elementFromPoint, the font set), never the source: a class name in
 * the HTML is a claim about the page, and this measures the page.
 *
 * Checks (finding ids):
 *   overflow        an element is painted past the viewport's inline edge and no
 *                   ancestor contains it (html/body clipping does not count: it
 *                   hides the overflow instead of fixing it). Something parked
 *                   wholly off-screen to the start or top (a skip link) is not.
 *   zoom-out        the layout viewport is wider than the screen (opts.expectedWidth)
 *   off-grid        a block's direct child is off its grid line (content | wide |
 *                   full) compared with the other blocks', a block is not a grid,
 *                   a full or backdrop slot does not cover the block, something
 *                   inside a slot pokes past the slot's edge into the gutter, or a
 *                   wrapper with no visible box pads its content off the line
 *   text-overflow   text sticks out of its box, sideways or downwards
 *   text-clipped    text cut off by its own box's overflow: hidden / clip
 *   clipped         text or a control cut off by an ANCESTOR's overflow: hidden /
 *                   clip (a card, a frame, a photo band); scroll containers excuse it
 *   overlap         something is painted over text or a control (hit-tested at its
 *                   centre, at every scroll position)
 *   heading-widow   a heading's last line is one short word
 *   measure         running text set wider than opts.measureMax characters per line
 *   target-size     an interactive target under 24×24px whose 24px circle meets
 *                   another target or another small target's circle (SC 2.5.8;
 *                   inline links in running text are exempt)
 *   input-zoom      a text field under 16px, which iOS zooms on focus
 *   orphan-row      a grid of like items whose last row holds one narrow item
 *                   under fuller rows (a grid marked data-ragged opts out)
 *   fold            the page's h1 does not end inside the first screen
 *   grid-span       a grid with zero-width columns: items span tracks the grid does
 *                   not define (a container query that cannot match, because the
 *                   grid IS the container it queries)
 *   nav-wrap        a row of navigation links broken onto more than one line, or
 *                   a site header's items (brand, nav, action) on more than one row
 *   word-broken     a figure ($125,000, 12:30) or a word no hyphenation can split,
 *                   broken across lines by overflow-wrap: its box is too narrow
 *   image-broken    an image that did not load
 *   image-distorted an image stretched off its natural aspect ratio (object-fit: fill)
 *   image-ratio     the width/height the page declares (the img's, or the chosen
 *                   <source>'s) are not the shape of the file the browser shows:
 *                   a photo an EXIF orientation turns, or a wrong size in the
 *                   manifest, so the reserved box, srcset and every crop are wrong
 *   image-upscaled  the file is enlarged to fill its box at min(DPR, 2)x: blurry
 *   image-oversized the file is more than 3x the pixels its box needs at 2x: wasted
 *                   bytes. With a srcset, only when a smaller candidate would still
 *                   cover the box at the screen's real density (a DPR-3 phone that
 *                   takes the next candidate up is the browser being right)
 *   image-gap       an image in a frame or photo band does not fill it
 *   frame-ratio     a box with an aspect-ratio drawn off that ratio (a stretched
 *                   frame cover-crops its photo to a sliver)
 *   image-no-size   an image with no width/height, no aspect-ratio and no sized
 *                   frame: it will shift the layout when it loads
 *   img-alt         an <img> with no alt attribute (alt="" is a valid choice)
 *   text-contrast   text below 4.5:1 (3:1 large) against the flat background it is
 *                   painted on. Text over a photo is skipped here: device_matrix.mjs
 *                   scores that on composited pixels (photo-contrast).
 *   focus-hidden    a focusable element with no visible focus indicator
 *   focus-clipped   its focus ring is cut off by a clipping ancestor
 *   focus-contrast  its focus ring is under 3:1 against what it is drawn on
 *   invisible       text inside a block that takes its space but is drawn at
 *                   opacity under 0.1, visibility: hidden or a transparent colour
 *                   (a reveal-on-scroll whose script never ran)
 *   field-contrast  a form control's edge (border or fill) is under 3:1 against
 *                   what it sits on (SC 1.4.11)
 *   anchor-obscured an in-page link's target lands under a fixed or sticky bar
 *   covered         content at the end of the page stays under a fixed bar
 *   layout-shift    cumulative layout shift above opts.clsThreshold (needs the
 *                   observer device_matrix.mjs installs before the page loads)
 *   font-failed     a web font that failed to load, or a used family not loaded
 *   chrome-share    fixed/sticky bars cover more than opts.maxChromeShare of the height
 *
 * Returns a Promise of { findings: [{ id, where, msg }], stats }.
 */
// eslint-disable-next-line no-unused-vars
async function layoutProbe(options) {
  const opts = Object.assign(
    {
      blockSelector: "[data-block]",
      expectedWidth: 0,
      edgeTolerance: 1,
      minTarget: 24,
      clsThreshold: 0.01,
      maxChromeShare: 0.3,
      upscaleTolerance: 1.15,
      maxDensity: 2,
      oversize: 3,
      measureMax: 75,
      maxPerCheck: 25,
      maxFocus: 80,
      skip: [],
      // A selector: report only findings on elements inside a match (and
      // page-level ones). device_matrix.mjs's open-<details> pass uses it, so
      // an open dropdown covering the footer is not blamed on the footer.
      within: null,
    },
    options || {},
  );
  const findings = [];
  const counts = {};
  const stats = { checked: {}, notMeasured: [] };
  const skip = new Set(opts.skip);
  const add = (id, el, msg) => {
    if (opts.within && el && el.nodeType === 1 && !el.closest(opts.within)) return;
    counts[id] = (counts[id] || 0) + 1;
    if (counts[id] <= opts.maxPerCheck) findings.push({ id, where: el ? path(el) : "page", msg });
  };
  const W = document.documentElement.clientWidth;
  const H = window.innerHeight;
  const DPR = window.devicePixelRatio || 1;
  const DENSITY = Math.min(DPR, opts.maxDensity);
  const startX = window.scrollX;
  const startY = window.scrollY;
  const startFocus = document.activeElement;

  function path(el) {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.id) {
        parts.unshift(`${s}#${e.id}`);
        break;
      }
      if (e.dataset && e.dataset.block) s += `[data-block="${e.dataset.block}"]`;
      else {
        const c = [...e.classList].slice(0, 2).join(".");
        if (c) s += `.${c}`;
      }
      parts.unshift(s);
    }
    return parts.join(" > ");
  }
  const cs = (el) => getComputedStyle(el);
  // Drawn is drawn: aria-hidden and inert change what a screen reader or a
  // pointer gets, never what a reader sees, so every visual check measures them.
  function visible(el) {
    const s = cs(el);
    if (s.display === "none" || s.visibility === "hidden" || s.visibility === "collapse")
      return false;
    if (el.closest("details:not([open]) > :not(summary)")) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 || r.height > 0;
  }
  const tiny = (r) => r.width <= 1 && r.height <= 1;
  const clips = (s) => /hidden|clip/.test(s.overflowX + s.overflowY) || s.clipPath !== "none";
  const scrolls = (s) => /auto|scroll/.test(s.overflowX + s.overflowY);
  const fixedish = (el) => {
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const p = cs(e).position;
      if (p === "fixed" || p === "sticky") return e;
    }
    return null;
  };
  // An ancestor (below body) that clips or scrolls contains its descendants'
  // overflow, so they cannot widen the page. html and body do not count: their
  // clipping is the viewport's and hides the overflow from the reader.
  function containedByAncestor(el) {
    for (
      let a = el.parentElement;
      a && a !== document.body && a !== document.documentElement;
      a = a.parentElement
    ) {
      const s = cs(a);
      if (clips(s) || scrolls(s) || /paint|content|strict/.test(s.contain)) return true;
    }
    return false;
  }
  const textOwners = () => {
    const out = new Set();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n = 0;
    for (let t = walker.nextNode(); t && n < 8000; t = walker.nextNode()) {
      if (!t.nodeValue.trim()) continue;
      const el = t.parentElement;
      if (!el || el.closest("script,style,noscript,template,svg,select,option,textarea")) continue;
      n++;
      out.add(el);
    }
    // Text in a box of 1px or less is visually hidden on purpose (a screen
    // reader label): its glyphs run on past the box, unseen, and are no one's to
    // read, overlap or score.
    return [...out].filter((el) => visible(el) && !tiny(el.getBoundingClientRect()));
  };
  const lineRects = (el) => {
    const range = document.createRange();
    const rects = [];
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.nodeValue.trim()) continue;
      range.selectNodeContents(n);
      for (const r of range.getClientRects()) if (r.width > 0 && r.height > 0) rects.push(r);
    }
    return rects;
  };
  // Any CSS colour (oklch, color-mix, system colours) to 8-bit sRGB, as painted.
  const cv = document.createElement("canvas");
  cv.width = cv.height = 1;
  const cx = cv.getContext("2d", { willReadFrequently: true });
  const rgba = (css) => {
    cx.clearRect(0, 0, 1, 1);
    cx.fillStyle = "#000";
    cx.fillStyle = css;
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const lin = (v) => {
    v /= 255;
    return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const over = (top, under) => {
    const a = top[3];
    return [0, 1, 2].map((i) => top[i] * a + under[i] * (1 - a)).concat(1);
  };
  const ratio = (a, b) => {
    const la = lum(a);
    const lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  };
  // The candidate widths (w descriptors) of the srcset the browser is using for
  // an image: the first <source> whose media matches, else the img's own.
  const srcsetWidths = (img) => {
    let set = img.getAttribute("srcset") || "";
    if (img.parentElement && img.parentElement.tagName === "PICTURE") {
      for (const so of img.parentElement.querySelectorAll("source")) {
        if (!so.media || matchMedia(so.media).matches) {
          set = so.getAttribute("srcset") || set;
          break;
        }
      }
    }
    return set
      .split(",")
      .map((c) => /\s(\d+)w\s*$/.exec(c.trim()))
      .filter(Boolean)
      .map((m) => Number(m[1]));
  };
  const opacity = (el) => {
    let a = 1;
    for (let e = el; e && e !== document.documentElement; e = e.parentElement)
      a *= Number(cs(e).opacity);
    return a;
  };
  // The flat colour behind an element: its own and its ancestors' backgrounds,
  // composited down to the first opaque one (white if none is).
  const backdrop = (el) => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const c = rgba(cs(e).backgroundColor);
      if (c[3] > 0) layers.push(c);
      if (c[3] >= 1) break;
    }
    let base = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return base;
  };
  const forced = matchMedia("(forced-colors: active)").matches;
  const run = async (id, fn) => {
    if (skip.has(id)) return;
    try {
      await fn();
    } catch (e) {
      add("probe-error", null, `${id} threw: ${e && e.message}`);
    }
  };

  // ── overflow + zoom-out ──────────────────────────────────────────────────
  await run("overflow", () => {
    if (opts.expectedWidth && Math.abs(window.innerWidth - opts.expectedWidth) > 1) {
      add(
        "zoom-out",
        null,
        `layout viewport is ${window.innerWidth}px on a ${opts.expectedWidth}px screen: something forced the page wider, so a phone zooms out`,
      );
    }
    const sw = document.documentElement.scrollWidth;
    if (sw > W + 1)
      add("overflow", null, `the page scrolls sideways: ${sw}px of content in a ${W}px viewport`);
    const reported = [];
    let n = 0;
    const rtl = cs(document.documentElement).direction === "rtl";
    for (const el of document.body.querySelectorAll("*")) {
      n++;
      const r = el.getBoundingClientRect();
      if (tiny(r) || (r.right <= W + 1 && r.left >= -1)) continue;
      // Parked wholly before the start edge or above the page: unreachable, so it
      // cannot widen anything (the skip-link and off-canvas patterns).
      if (r.bottom <= 0 || (!rtl && r.right <= 0) || (rtl && r.left >= W)) continue;
      if (!visible(el) || containedByAncestor(el)) continue;
      if (reported.some((p) => p.contains(el))) continue;
      reported.push(el);
      add(
        "overflow",
        el,
        `painted from ${Math.round(r.left)} to ${Math.round(r.right)}px in a ${W}px viewport (${Math.round(Math.max(r.right - W, -r.left))}px out)`,
      );
    }
    stats.checked.overflow = n;
  });

  // ── off-grid ─────────────────────────────────────────────────────────────
  await run("off-grid", () => {
    const blocks = [...document.querySelectorAll(opts.blockSelector)].filter(visible);
    const lines = { content: [], wide: [], full: [] };
    let escapes = 0;
    for (const b of blocks) {
      const s = cs(b);
      if (s.display !== "grid" && s.display !== "inline-grid") {
        add(
          "off-grid",
          b,
          `block is display:${s.display}, not the page grid, so its content cannot share the grid lines`,
        );
        continue;
      }
      const br = b.getBoundingClientRect();
      for (const child of b.children) {
        const c = cs(child);
        const slot = child.dataset.slot || "content";
        if ((slot === "backdrop" || slot === "full") && visible(child)) {
          // A full-bleed slot must reach the block's edges; a backdrop must cover it.
          const r = child.getBoundingClientRect();
          const off = Math.max(
            Math.abs(r.left - br.left),
            Math.abs(r.right - br.right),
            slot === "backdrop"
              ? Math.max(Math.abs(r.top - br.top), Math.abs(r.bottom - br.bottom))
              : 0,
          );
          if (off > opts.edgeTolerance) {
            add(
              "off-grid",
              child,
              `the ${slot} slot covers ${Math.round(r.left)}–${Math.round(r.right)} × ${Math.round(r.top)}–${Math.round(r.bottom)}px of a block that spans ${Math.round(br.left)}–${Math.round(br.right)} × ${Math.round(br.top)}–${Math.round(br.bottom)}px`,
            );
          }
        }
        if (c.position === "absolute" || c.position === "fixed" || !visible(child)) continue;
        if (!lines[slot]) continue;
        const r = child.getBoundingClientRect();
        lines[slot].push({ el: child, left: r.left, right: r.right });
        if (slot === "full") continue;
        // Inside the slot: nothing pokes into the gutter, and no invisible wrapper
        // pads the content off the line.
        for (const d of child.querySelectorAll("*")) {
          if (!visible(d)) continue;
          const ds = cs(d);
          if (ds.position === "absolute" || ds.position === "fixed") continue;
          let inScroller = false;
          for (let p = d.parentElement; p && p !== child; p = p.parentElement)
            if (scrolls(cs(p)) || clips(cs(p))) inScroller = true;
          if (inScroller) continue;
          const dr = d.getBoundingClientRect();
          if (tiny(dr)) continue;
          if (dr.left < r.left - opts.edgeTolerance || dr.right > r.right + opts.edgeTolerance) {
            escapes++;
            add(
              "off-grid",
              d,
              `runs ${Math.round(Math.max(r.left - dr.left, dr.right - r.right))}px past its ${slot} slot (${Math.round(r.left)}–${Math.round(r.right)}px) into the gutter`,
            );
            break;
          }
          const pad = Math.max(parseFloat(ds.paddingInlineStart), parseFloat(ds.paddingInlineEnd));
          const boxless =
            /rgba\(0, 0, 0, 0\)|transparent/.test(ds.backgroundColor) &&
            ds.backgroundImage === "none" &&
            ds.boxShadow === "none" &&
            parseFloat(ds.borderInlineStartWidth) === 0 &&
            parseFloat(ds.borderInlineEndWidth) === 0;
          if (
            pad > opts.edgeTolerance &&
            boxless &&
            /^(block|flex|grid|flow-root)$/.test(ds.display) &&
            !d.matches(
              "li,dl,dd,blockquote,figure,fieldset,details,summary,table,td,th,pre,label,button,a,nav,form",
            ) &&
            // A list's indent holds its markers; with no markers it is padding
            // with nothing to show for it, like any other wrapper's.
            !(
              d.matches("ul,ol") &&
              [...d.children].some(
                (li) => cs(li).display === "list-item" && cs(li).listStyleType !== "none",
              )
            ) &&
            Math.abs(dr.left - r.left) <= opts.edgeTolerance &&
            d.textContent.trim()
          ) {
            add(
              "off-grid",
              d,
              `${Math.round(pad)}px of inline padding on a box with nothing to show for it moves its content off the ${slot} line`,
            );
            break;
          }
        }
      }
    }
    const mode = (xs) => {
      const tally = new Map();
      for (const x of xs) {
        const k = Math.round(x * 2) / 2;
        tally.set(k, (tally.get(k) || 0) + 1);
      }
      return [...tally.entries()].sort((a, b) => b[1] - a[1])[0][0];
    };
    let checked = 0;
    for (const [slot, items] of Object.entries(lines)) {
      if (items.length < 2) continue;
      const L = mode(items.map((i) => i.left));
      const R = mode(items.map((i) => i.right));
      for (const it of items) {
        checked++;
        const dl = it.left - L;
        const dr = it.right - R;
        if (Math.abs(dl) > opts.edgeTolerance || Math.abs(dr) > opts.edgeTolerance) {
          add(
            "off-grid",
            it.el,
            `the ${slot} line runs ${Math.round(L)}–${Math.round(R)}px; this block's ${slot} slot runs ${Math.round(it.left)}–${Math.round(it.right)}px (${dl > 0 ? "+" : ""}${dl.toFixed(1)} / ${dr > 0 ? "+" : ""}${dr.toFixed(1)}px)`,
          );
        }
      }
    }
    stats.checked["off-grid"] = checked;
    stats.checked["grid-escape"] = escapes;
  });

  // ── text-overflow / text-clipped / clipped / heading-widow / measure ─────
  await run("text-overflow", () => {
    const boxOf = (el) => {
      for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
        const d = cs(e).display;
        if (d !== "inline" && d !== "contents") return e;
      }
      return document.body;
    };
    const owners = textOwners();
    const seen = new Set();
    let n = 0;
    for (const el of owners) {
      const box = boxOf(el);
      if (seen.has(box)) continue;
      const bs = cs(box);
      const br = box.getBoundingClientRect();
      if (tiny(br)) continue;
      if (scrolls(bs)) continue; // scrolls on purpose
      if (bs.textOverflow === "ellipsis" || bs.webkitLineClamp !== "none") continue; // truncates on purpose
      n++;
      const left = br.left + parseFloat(bs.borderLeftWidth) + parseFloat(bs.paddingLeft);
      const right = br.right - parseFloat(bs.borderRightWidth) - parseFloat(bs.paddingRight);
      const top = br.top + parseFloat(bs.borderTopWidth);
      const bottom = br.bottom - parseFloat(bs.borderBottomWidth);
      // Glyph boxes overhang a tight line-height by a fraction of the font size.
      const vtol = Math.max(2, parseFloat(cs(el).fontSize) * 0.35);
      for (const r of lineRects(el)) {
        const sideways = r.right > right + 1 || r.left < left - 1;
        const down = r.bottom > bottom + vtol || r.top < top - vtol;
        if (!sideways && !down) continue;
        seen.add(box);
        const cut = sideways ? /hidden|clip/.test(bs.overflowX) : /hidden|clip/.test(bs.overflowY);
        const by = sideways
          ? Math.max(r.right - right, left - r.left)
          : Math.max(r.bottom - bottom, top - r.top);
        add(
          cut ? "text-clipped" : "text-overflow",
          box,
          `"${el.textContent.trim().slice(0, 40)}" runs ${Math.round(by)}px ${sideways ? "past the side of" : "out of the bottom of"} its box${cut ? " and is cut off" : ""}`,
        );
        break;
      }
    }
    // Downwards: a box whose height is fixed lets its text spill out of the
    // bottom, while the text's own block grows with it. So compare each line with
    // its ancestors up to the block, not only with its own box. Out-of-flow text
    // (absolutely positioned, or under a transform) is left to the other checks.
    for (const el of owners) {
      if (seen.has(boxOf(el)) || el.closest("[data-slot='backdrop']")) continue;
      let outOfFlow = false;
      for (let e = el; e && e !== document.body; e = e.parentElement) {
        const es = cs(e);
        if (es.position === "absolute" || es.position === "fixed" || es.transform !== "none")
          outOfFlow = true;
      }
      if (outOfFlow) continue;
      const lines = lineRects(el);
      if (!lines.length) continue;
      const lowest = Math.max(...lines.map((r) => r.bottom));
      const vtol = Math.max(2, parseFloat(cs(el).fontSize) * 0.35);
      for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
        const as = cs(a);
        if (scrolls(as) || /hidden|clip/.test(as.overflowY)) break; // scrolls, or reported as clipped
        const ar = a.getBoundingClientRect();
        const floor = ar.bottom - parseFloat(as.borderBottomWidth);
        if (lowest > floor + vtol) {
          seen.add(boxOf(el));
          add(
            "text-overflow",
            a,
            `"${el.textContent.trim().slice(0, 40)}" runs ${Math.round(lowest - floor)}px out of the bottom of this box (a fixed height?)`,
          );
          break;
        }
        if (a.matches(opts.blockSelector)) break;
      }
    }
    stats.checked["text-overflow"] = n;

    // Text or a control cut off by an ancestor that clips (a card, a frame, a band).
    const subjects = new Set(owners);
    for (const el of document.querySelectorAll("a[href],button,input,select,textarea,summary"))
      if (visible(el)) subjects.add(el);
    const reported = [];
    let c = 0;
    for (const el of subjects) {
      if (el.closest("[data-slot='backdrop']") || reported.some((p) => p.contains(el))) continue;
      const rects = el.matches("a,button,input,select,textarea,summary")
        ? [el.getBoundingClientRect()]
        : lineRects(el);
      if (!rects.length || rects.every(tiny)) continue;
      c++;
      for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
        const s = cs(a);
        if (scrolls(s)) break; // reachable by scrolling
        if (!clips(s)) continue;
        const ar = a.getBoundingClientRect();
        if (tiny(ar)) break; // a visually hidden wrapper: hidden on purpose
        const cutX = /hidden|clip/.test(s.overflowX) || s.clipPath !== "none";
        const cutY = /hidden|clip/.test(s.overflowY) || s.clipPath !== "none";
        let worst = 0;
        for (const r of rects) {
          if (cutX) worst = Math.max(worst, r.right - ar.right, ar.left - r.left);
          if (cutY) worst = Math.max(worst, r.bottom - ar.bottom, ar.top - r.top);
        }
        if (worst > 1) {
          reported.push(el);
          add("clipped", el, `${Math.round(worst)}px of it is cut off by ${path(a)}`);
        }
        break;
      }
    }
    stats.checked.clipped = c;

    // A heading whose last line is one short word.
    let h = 0;
    const range = document.createRange();
    for (const el of document.querySelectorAll("h1,h2,h3")) {
      if (!visible(el)) continue;
      range.selectNodeContents(el);
      const rows = new Map();
      for (const r of range.getClientRects()) {
        if (r.width === 0) continue;
        const k = Math.round(r.top / 4);
        const row = rows.get(k) || { l: r.left, r: r.right };
        row.l = Math.min(row.l, r.left);
        row.r = Math.max(row.r, r.right);
        rows.set(k, row);
      }
      if (rows.size < 2) continue;
      h++;
      const widths = [...rows.entries()].sort((a, b) => a[0] - b[0]).map(([, v]) => v.r - v.l);
      const last = widths[widths.length - 1];
      const words = el.textContent.trim().split(/\s+/);
      const lastWord = words[words.length - 1] || "";
      if (last < 0.2 * Math.max(...widths) && lastWord.length <= 10) {
        const balanced = /balance/.test(cs(el).textWrapStyle || cs(el).textWrap || "");
        add(
          "heading-widow",
          el,
          `"${el.textContent.trim().slice(0, 40)}" ends on a line holding only "${lastWord}" (${balanced ? "text-wrap: balance is already on and did not help: shorten the heading or change its max-inline-size" : "text-wrap: balance fixes this"})`,
        );
      }
    }
    stats.checked["heading-widow"] = h;

    // Running text wider than a comfortable line.
    let m = 0;
    for (const el of document.querySelectorAll("p, li, dd, blockquote, figcaption")) {
      if (!visible(el) || el.closest("nav")) continue;
      const rows = new Set(lineRects(el).map((r) => Math.round(r.top / 4)));
      if (rows.size < 2) continue;
      m++;
      const s = cs(el);
      // From longhands: the font shorthand serialises as "" whenever a longhand it
      // cannot express is set, and the canvas then measures its own 10px default.
      cx.font = `${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
      const ch = cx.measureText("0").width || parseFloat(s.fontSize) * 0.5;
      const width =
        el.getBoundingClientRect().width - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
      const chars = width / ch;
      if (chars > opts.measureMax)
        add(
          "measure",
          el,
          `lines run ${Math.round(chars)}ch wide; keep running text at 45–${opts.measureMax}ch (max-inline-size: var(--measure))`,
        );
    }
    stats.checked.measure = m;
  });

  // ── target-size / input-zoom ─────────────────────────────────────────────
  await run("target-size", () => {
    const sel =
      "a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=link],[tabindex]:not([tabindex='-1'])";
    const targets = [...document.querySelectorAll(sel)]
      .filter(visible)
      .map((el) => ({ el, r: el.getBoundingClientRect() }))
      .filter((t) => !tiny(t.r));
    const inlineInText = (el) => {
      if (el.tagName !== "A" || cs(el).display !== "inline") return false;
      const p = el.parentElement;
      return !!p && p.textContent.trim().length > el.textContent.trim().length + 10;
    };
    const small = (t) =>
      (t.r.width < opts.minTarget || t.r.height < opts.minTarget) && !inlineInText(t.el);
    const rad = opts.minTarget / 2;
    for (const t of targets) {
      if (!small(t)) continue;
      const { el, r } = t;
      // WCAG 2.5.8 spacing exception: a 24px circle on the target's centre must
      // not intersect another target, nor another undersized target's circle.
      const cxp = r.left + r.width / 2;
      const cyp = r.top + r.height / 2;
      const hits = targets.some((o) => {
        if (o === t || o.el.contains(el) || el.contains(o.el)) return false;
        const nx = Math.max(o.r.left, Math.min(cxp, o.r.right));
        const ny = Math.max(o.r.top, Math.min(cyp, o.r.bottom));
        if ((nx - cxp) ** 2 + (ny - cyp) ** 2 < rad * rad) return true;
        if (!small(o)) return false;
        const ox = o.r.left + o.r.width / 2;
        const oy = o.r.top + o.r.height / 2;
        return (ox - cxp) ** 2 + (oy - cyp) ** 2 < (2 * rad) ** 2;
      });
      if (hits)
        add(
          "target-size",
          el,
          `${Math.round(r.width)}×${Math.round(r.height)}px target whose 24px circle meets a neighbour (SC 2.5.8)`,
        );
    }
    stats.checked["target-size"] = targets.length;
    let f = 0;
    for (const el of document.querySelectorAll("input,select,textarea")) {
      const type = (el.getAttribute("type") || "text").toLowerCase();
      if (
        [
          "checkbox",
          "radio",
          "range",
          "color",
          "hidden",
          "submit",
          "button",
          "reset",
          "image",
          "file",
        ].includes(type)
      )
        continue;
      if (!visible(el)) continue;
      f++;
      const size = parseFloat(cs(el).fontSize);
      if (size < 16)
        add("input-zoom", el, `form text is ${size}px; iOS zooms the page on focus below 16px`);
    }
    stats.checked["input-zoom"] = f;
  });

  // ── orphan-row / grid-span / nav-wrap ────────────────────────────────────
  await run("orphan-row", () => {
    let n = 0;
    for (const g of document.querySelectorAll("body *")) {
      const s = cs(g);
      if (s.display !== "grid" && s.display !== "inline-grid") continue;
      if (g.matches(opts.blockSelector)) continue; // the page grid: one slot per row by design
      const kids = [...g.children].filter(
        (k) => visible(k) && !["absolute", "fixed"].includes(cs(k).position),
      );
      // A 0px column that still takes its gaps: what follows it (or the row's
      // end) sits a gap off its line. auto-fit's empty tracks are 0px too, but
      // they collapse with their gutters, so the real columns still fill the row.
      const tracks = s.gridTemplateColumns
        .split(/\s+/)
        .filter((t) => /px$/.test(t))
        .map(parseFloat);
      const gap = parseFloat(s.columnGap) || 0;
      const zero = tracks.map((t) => t < 0.5);
      if (kids.length && tracks.length > 1 && gap > 0 && zero.some(Boolean)) {
        const real = tracks.filter((t) => t >= 0.5);
        const inner =
          g.clientWidth - parseFloat(s.paddingInlineStart) - parseFloat(s.paddingInlineEnd);
        const trailing = zero.indexOf(true) > zero.lastIndexOf(false);
        const collapsed =
          trailing &&
          Math.abs(real.reduce((x, y) => x + y, 0) + gap * (real.length - 1) - inner) <= 1;
        if (!collapsed)
          add(
            "grid-span",
            g,
            `columns resolve to ${tracks.map((t) => Math.round(t)).join(" / ")}px: a 0px column still takes its ${Math.round(gap)}px gaps, so what comes after it sits off its line (an empty optional column, or items spanning tracks the template does not define); leave the column out of the template when it is empty, or use auto-fit, which collapses an empty track and its gutters`,
          );
      }
      if (kids.length < 3 || g.hasAttribute("data-ragged")) continue;
      // Only a grid of LIKE items can strand one: a form's fields and its button
      // are not a set of cards.
      const kind = (k) => `${k.tagName}.${[...k.classList].sort().join(".")}`;
      if (new Set(kids.map(kind)).size !== 1) continue;
      n++;
      const rows = new Map();
      for (const k of kids) {
        const top = Math.round(k.getBoundingClientRect().top / 2);
        rows.set(top, (rows.get(top) || []).concat(k));
      }
      const ordered = [...rows.entries()].sort((a, b) => a[0] - b[0]).map(([, v]) => v);
      if (ordered.length < 2) continue;
      const last = ordered[ordered.length - 1];
      const gr = g.getBoundingClientRect();
      const lr = last[0].getBoundingClientRect();
      // Centred on purpose (a photo card that keeps its column's width) is not
      // stranded: only one left at the start edge, with a hole beside it, is.
      const centred = Math.abs(lr.left + lr.width / 2 - (gr.left + gr.width / 2)) < 2;
      if (
        last.length === 1 &&
        !centred &&
        ordered.some((r) => r.length >= 2) &&
        lr.width < 0.6 * gr.width
      ) {
        add(
          "orphan-row",
          g,
          `${kids.length} items laid out ${ordered.map((r) => r.length).join("+")}: the last one is alone on its row (use .cards, or mark an open-ended list data-ragged)`,
        );
      }
    }
    stats.checked["orphan-row"] = n;
    let v = 0;
    for (const nav of document.querySelectorAll("nav")) {
      if (!visible(nav)) continue;
      const links = [...nav.querySelectorAll("a[href]")].filter(visible);
      if (links.length < 2) continue;
      const parent = links[0].closest("ul,ol") || nav;
      if (cs(parent).flexDirection === "column" || cs(parent).display === "block") continue;
      v++;
      const tops = new Set(links.map((l) => Math.round(l.getBoundingClientRect().top / 4)));
      if (tops.size > 1)
        add(
          "nav-wrap",
          nav,
          `${links.length} links broken over ${tops.size} lines: collapse it into a menu below this width`,
        );
    }
    // A site header is one row (brand, nav, action): an item wrapping under the
    // others means the nav should have become a menu at a wider width.
    for (const hdr of document.querySelectorAll("header, [role='banner']")) {
      if (!visible(hdr) || hdr.closest("main, article, section")) continue;
      for (const row of hdr.querySelectorAll("*")) {
        const s = cs(row);
        if (
          !/flex/.test(s.display) ||
          s.flexDirection.startsWith("column") ||
          s.flexWrap === "nowrap"
        )
          continue;
        if (row.closest("nav") || !visible(row)) continue;
        const kids = [...row.children]
          .filter((k) => visible(k) && !["absolute", "fixed"].includes(cs(k).position))
          .map((k) => k.getBoundingClientRect())
          .sort((a, b) => a.top - b.top);
        if (kids.length < 2) continue;
        v++;
        let lines = 1;
        let bottom = kids[0].bottom;
        for (const r of kids.slice(1)) {
          if (r.top >= bottom - 1) {
            lines++;
            bottom = r.bottom;
          } else bottom = Math.max(bottom, r.bottom);
        }
        if (lines > 1)
          add(
            "nav-wrap",
            row,
            `the header's ${kids.length} items broke onto ${lines} rows: the nav should become a menu below this width`,
          );
      }
    }
    stats.checked["nav-wrap"] = v;
  });

  // ── word-broken: a figure, or a word no hyphenation can split, broken across
  //    lines ("$125,0" / "00"). overflow-wrap: anywhere breaks anything that does
  //    not fit; a box that narrow is the defect. ──────────────────────────────
  await run("word-broken", () => {
    // Scripts written without spaces break between characters by design.
    const spaceless =
      /[\u0e00-\u0eff\u1000-\u109f\u1100-\u11ff\u1780-\u17ff\u2e80-\ua4cf\uac00-\ud7af\uf900-\ufaff\ufe30-\ufe4f\uff00-\uffef]/;
    const range = document.createRange();
    let n = 0;
    for (const el of textOwners()) {
      const s = cs(el);
      const hyphenates = s.hyphens === "auto" || s.webkitHyphens === "auto";
      for (const node of el.childNodes) {
        if (node.nodeType !== 3) continue;
        for (const m of node.nodeValue.matchAll(/\S+/g)) {
          const w = m[0];
          if (w.length < 2 || w.length > 24 || spaceless.test(w)) continue;
          // A word a hyphenation dictionary can split gets a hyphen where it breaks.
          if (hyphenates && !/\d/.test(w)) continue;
          n++;
          range.setStart(node, m.index);
          range.setEnd(node, m.index + w.length);
          const rects = [...range.getClientRects()].filter((r) => r.width > 0);
          if (rects.length < 2) continue;
          const top0 = rects[0].top;
          const half = rects[0].height / 2;
          if (!rects.some((r) => Math.abs(r.top - top0) > half)) continue;
          let at = -1;
          for (let i = 1; i < w.length && at < 0; i++) {
            range.setStart(node, m.index + i);
            range.setEnd(node, m.index + i + 1);
            const r = range.getClientRects()[0];
            if (r && Math.abs(r.top - top0) > half) at = i;
          }
          // After a hyphen, dash or slash is an ordinary place to break a line.
          if (at > 0 && /[-\u2010-\u2014/]/.test(w[at - 1])) continue;
          add(
            "word-broken",
            el,
            `"${w}" is split across lines${at > 0 ? ` after "${w.slice(0, at)}"` : ""}: its box is too narrow for it at this size (give it room, or keep a figure whole with white-space: nowrap)`,
          );
        }
      }
    }
    stats.checked["word-broken"] = n;
  });

  // ── images ───────────────────────────────────────────────────────────────
  await run("images", async () => {
    // The file's real pixels: naturalWidth is corrected for the srcset density the
    // browser chose, so it is the drawn size, not the file's.
    const files = new Map();
    await Promise.all(
      [...document.images].map(async (img) => {
        if (!img.complete || !img.naturalWidth) return;
        const src = img.currentSrc || img.src;
        if (!src) return;
        try {
          const probe = new Image();
          probe.src = src;
          await probe.decode();
          files.set(img, [probe.naturalWidth, probe.naturalHeight]);
        } catch (_) {
          /* not decodable here: reported as not measured below */
        }
      }),
    );
    // The width each image draws its file at (object-fit applied). A browser may
    // show an already-loaded bigger candidate rather than fetch a smaller one
    // (Chromium does, from its memory cache): no extra bytes, so a file ANOTHER
    // image on the page draws at a size that needs it is not oversized.
    const drawnWidth = (im) => {
      const r = im.getBoundingClientRect();
      const fit = cs(im).objectFit;
      const ar = im.naturalWidth / im.naturalHeight;
      if (!ar || !r.height) return r.width;
      if (fit === "cover") return Math.max(r.width, r.height * ar);
      if (fit === "contain" || fit === "scale-down") return Math.min(r.width, r.height * ar);
      if (fit === "none") return im.naturalWidth;
      return r.width;
    };
    const drawnBy = new Map();
    for (const im of document.images) {
      if (!im.complete || !im.naturalWidth || !visible(im)) continue;
      const k = im.currentSrc || im.src;
      if (!drawnBy.has(k)) drawnBy.set(k, []);
      drawnBy.get(k).push([im, drawnWidth(im)]);
    }
    let n = 0;
    for (const img of document.images) {
      if (!img.hasAttribute("alt"))
        add("img-alt", img, `no alt attribute (use alt="" for a decorative image)`);
      if (!visible(img)) continue;
      n++;
      if (!img.complete || img.naturalWidth === 0) {
        add("image-broken", img, `did not load: ${img.currentSrc || img.src}`.slice(0, 160));
        continue;
      }
      const s = cs(img);
      const r = img.getBoundingClientRect();
      const bw =
        r.width -
        parseFloat(s.paddingLeft) -
        parseFloat(s.paddingRight) -
        parseFloat(s.borderLeftWidth) -
        parseFloat(s.borderRightWidth);
      const bh =
        r.height -
        parseFloat(s.paddingTop) -
        parseFloat(s.paddingBottom) -
        parseFloat(s.borderTopWidth) -
        parseFloat(s.borderBottomWidth);
      if (bw <= 0 || bh <= 0) continue;
      const fit = s.objectFit;
      const nw = img.naturalWidth;
      const nh = img.naturalHeight;
      if (fit === "fill" && Math.abs(bw / bh - nw / nh) / (nw / nh) > 0.02) {
        add(
          "image-distorted",
          img,
          `${nw}×${nh} image drawn ${Math.round(bw)}×${Math.round(bh)}: stretched (use a frame with object-fit: cover)`,
        );
      }
      // A frame or a photo band the image does not fill.
      const holder =
        img.parentElement && img.parentElement.tagName === "PICTURE"
          ? img.parentElement.parentElement
          : img.parentElement;
      const framed =
        holder &&
        (holder.matches(".frame, [data-slot='backdrop']") || cs(holder).aspectRatio !== "auto");
      if (framed) {
        const hr = holder.getBoundingClientRect();
        const gap = Math.max(
          hr.right - r.right,
          r.left - hr.left,
          hr.bottom - r.bottom,
          r.top - hr.top,
        );
        if (gap > 1)
          add(
            "image-gap",
            img,
            `the image covers ${Math.round(r.width)}×${Math.round(r.height)}px of its ${Math.round(hr.width)}×${Math.round(hr.height)}px frame: ${Math.round(gap)}px of the frame shows through`,
          );
      }
      const src = img.currentSrc || img.src || "";
      const vector = /\.svg(\?|#|$)/i.test(src) || src.startsWith("data:image/svg");
      const file = files.get(img);
      if (!vector && file) {
        // The shape the page declares: the chosen <source>'s width and height when
        // it has them (an art-directed crop), else the img's. The decoded file is
        // the shape the browser draws, an EXIF turn applied.
        let decl = img;
        if (img.parentElement && img.parentElement.tagName === "PICTURE") {
          for (const so of img.parentElement.querySelectorAll("source")) {
            const urls = (so.getAttribute("srcset") || "")
              .split(",")
              .map((c) => c.trim().split(/\s+/)[0])
              .filter(Boolean)
              .map((u) => new URL(u, document.baseURI).href);
            if (urls.includes(img.currentSrc)) {
              if (so.hasAttribute("width") && so.hasAttribute("height")) decl = so;
              break;
            }
          }
        }
        const dw0 = parseFloat(decl.getAttribute("width"));
        const dh0 = parseFloat(decl.getAttribute("height"));
        if (dw0 > 0 && dh0 > 0) {
          const said = dw0 / dh0;
          const real = file[0] / file[1];
          if (Math.abs(said - real) / real > 0.02)
            add(
              "image-ratio",
              img,
              `the page declares ${dw0}×${dh0} (${said.toFixed(2)}:1) for a file the browser shows as ${file[0]}×${file[1]} (${real.toFixed(2)}:1): an EXIF orientation that turns the photo, or a wrong size in the manifest. Save the photo upright and give its real size`,
            );
        }
        const [fw, fh] = file;
        const ar = fw / fh;
        let dw;
        let dh;
        if (fit === "cover") {
          dw = Math.max(bw, bh * ar);
          dh = dw / ar;
        } else if (fit === "contain" || fit === "scale-down") {
          dw = Math.min(bw, bh * ar);
          dh = dw / ar;
          if (fit === "scale-down" && nw < dw) {
            dw = nw;
            dh = nh;
          }
        } else if (fit === "none") {
          dw = nw;
          dh = nh;
        } else {
          dw = bw;
          dh = bh;
        }
        const scale = Math.max(dw / fw, dh / fh) * DENSITY;
        if (scale > opts.upscaleTolerance) {
          add(
            "image-upscaled",
            img,
            `a ${fw}×${fh} file drawn ${Math.round(dw)}×${Math.round(dh)} CSS px is enlarged ${scale.toFixed(2)}× at ${DENSITY}x: blurry (supply at least ${Math.ceil(dw * DENSITY)}×${Math.ceil(dh * DENSITY)} for this crop)`,
          );
        }
        // With a srcset, the browser takes the smallest candidate that covers the
        // drawn width at the screen's REAL density (3x on many phones). If that is
        // the file, the weight comes from the candidates' spacing and the density,
        // not from a wrong sizes: only a smaller candidate that would have done
        // makes it oversized.
        const cands = srcsetWidths(img);
        const needW = dw * DPR;
        const covering = cands.filter((w) => w >= needW * 0.98);
        const fair =
          cands.length && fw <= (covering.length ? Math.min(...covering) : Math.max(...cands));
        const shared = (drawnBy.get(src) || []).some(
          ([o, w]) => o !== img && w * DENSITY * opts.oversize >= fw,
        );
        if (!fair && !shared && fw >= 1000 && scale > 0 && 1 / scale > opts.oversize) {
          add(
            "image-oversized",
            img,
            `a ${fw}px-wide file for a ${Math.round(dw)}px box at ${DENSITY}x: ${(1 / scale).toFixed(1)}× the pixels it needs (fix its sizes, or add a smaller srcset candidate)`,
          );
        }
      } else if (!vector && !file) {
        stats.notMeasured.push(
          `image size of ${src.slice(0, 80)} (its file could not be decoded here)`,
        );
      }
      const sized = img.hasAttribute("width") && img.hasAttribute("height");
      if (!sized && s.aspectRatio === "auto" && !framed) {
        add(
          "image-no-size",
          img,
          "no width/height attributes, no aspect-ratio and no sized frame: the page will shift when it loads",
        );
      }
    }
    stats.checked.images = n;
    // A frame stretched off its declared ratio (align-items: stretch beside a
    // taller column overrides aspect-ratio).
    let fr = 0;
    for (const el of document.body.querySelectorAll("*")) {
      const ar = cs(el).aspectRatio;
      // "auto W / H" is the browser's hint from an img's width and height, which
      // yields to the box it fills; only an author's ratio is a promise.
      if (!ar || /auto/.test(ar) || !visible(el)) continue;
      const m = ar.match(/([\d.]+)\s*\/\s*([\d.]+)/) || ar.match(/^([\d.]+)$/);
      if (!m) continue;
      const want = Number(m[1]) / Number(m[2] || 1);
      const r = el.getBoundingClientRect();
      if (r.width < 24 || r.height < 24 || !want) continue;
      fr++;
      const got = r.width / r.height;
      if (Math.abs(got - want) / want > 0.02)
        add(
          "frame-ratio",
          el,
          `declared ${ar} but drawn ${Math.round(r.width)}×${Math.round(r.height)} (${got.toFixed(2)}): something stretched it (align-self: start in a row)`,
        );
    }
    stats.checked["frame-ratio"] = fr;
  });

  // ── text-contrast (flat backgrounds; photos are device_matrix.mjs's) ─────
  await run("text-contrast", () => {
    const media = [];
    for (const m of document.body.querySelectorAll("img,video,canvas,picture,*")) {
      const isMedia = /^(IMG|VIDEO|CANVAS)$/.test(m.tagName);
      if (!isMedia && cs(m).backgroundImage === "none") continue;
      const r = m.getBoundingClientRect();
      if (r.width >= 48 && r.height >= 48) media.push({ el: m, r });
    }
    let n = 0;
    for (const el of textOwners()) {
      if (el.closest("[data-tone='media']") || el.matches(":disabled")) continue;
      const rects = lineRects(el);
      if (!rects.length || rects.every(tiny)) continue;
      const r0 = rects[0];
      if (
        media.some(
          (m) =>
            !el.contains(m.el) &&
            !m.el.contains(el) &&
            r0.left < m.r.right &&
            r0.right > m.r.left &&
            r0.top < m.r.bottom &&
            r0.bottom > m.r.top,
        ) ||
        media.some(
          (m) => m.el.contains(el) && m.el.tagName !== "BODY" && m.el !== document.documentElement,
        )
      )
        continue; // over a photo or a gradient: scored on pixels by device_matrix.mjs
      const s = cs(el);
      if (s.backgroundClip === "text" || s.webkitBackgroundClip === "text") continue;
      // The glyphs paint in -webkit-text-fill-color, except in forced colours,
      // where the browser paints the forced color and the fill still reports
      // the author's value (measured in Chromium, 2026-10-27).
      const fill = forced ? s.color : s.webkitTextFillColor || s.color;
      const fg = rgba(fill);
      fg[3] *= opacity(el);
      if (fg[3] < 0.02) continue;
      n++;
      const bg = backdrop(el);
      const shown = over(fg, bg);
      const r = ratio(shown, bg);
      const size = parseFloat(s.fontSize);
      const large = size >= 24 || (size >= 18.66 && Number(s.fontWeight) >= 700);
      const need = large ? 3 : 4.5;
      if (r < need - 0.005)
        add(
          "text-contrast",
          el,
          `"${el.textContent.trim().slice(0, 30)}" is ${r.toFixed(2)}:1 on its background, needs ${need}:1 (SC 1.4.3)`,
        );
    }
    stats.checked["text-contrast"] = n;
  });

  // ── invisible: text a block lays out but nobody can see ──────────────────
  // Opacity under 0.1, visibility: hidden or a transparent fill on text that
  // still takes its space: a reveal-on-scroll whose script never ran, an
  // entrance animation stuck at its start. Every other check would skip it as
  // intentionally hidden, so a blank page would pass.
  await run("invisible", () => {
    let n = 0;
    const seen = new Set();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) {
      if (!t.nodeValue.trim()) continue;
      const el = t.parentElement;
      if (!el || seen.has(el)) continue;
      seen.add(el);
      if (!el.closest(opts.blockSelector)) continue;
      if (el.closest("script,style,noscript,template,svg,[hidden],[inert],[aria-hidden='true']"))
        continue;
      if (el.closest("details:not([open]) > :not(summary)")) continue;
      const s = cs(el);
      if (s.display === "none" || s.visibility === "collapse") continue;
      const r = el.getBoundingClientRect();
      if (tiny(r) || r.width < 2 || r.height < 2) continue; // visually hidden on purpose
      n++;
      const fill = rgba(forced ? s.color : s.webkitTextFillColor || s.color);
      const clipText = s.backgroundClip === "text" || s.webkitBackgroundClip === "text";
      const why =
        s.visibility === "hidden"
          ? "visibility: hidden"
          : opacity(el) < 0.1
            ? `opacity ${opacity(el).toFixed(2)}`
            : fill[3] < 0.02 && !clipText
              ? "a transparent text colour"
              : "";
      if (why)
        add(
          "invisible",
          el,
          `"${el.textContent.trim().slice(0, 30)}" takes its space but is drawn with ${why}: a reveal that never ran, or content hidden by CSS`,
        );
    }
    stats.checked.invisible = n;
  });

  // ── field-contrast: a form control's edge against what it sits on ────────
  await run("field-contrast", () => {
    if (forced) return; // the browser draws controls in system colours
    let n = 0;
    const sel =
      "input:not([type=hidden],[type=checkbox],[type=radio],[type=range],[type=color],[type=submit],[type=button],[type=reset],[type=image],[type=file]),select,textarea";
    for (const f of document.querySelectorAll(sel)) {
      if (!visible(f) || f.disabled || f.closest("[data-tone='media']")) continue;
      n++;
      const s = cs(f);
      const outside = backdrop(f.parentElement);
      const fill = over(rgba(s.backgroundColor), outside);
      // The edge that identifies the control: its border (on its fill), or its
      // fill against the page, whichever shows more.
      let edge = ratio(fill, outside);
      for (const side of ["Top", "Right", "Bottom", "Left"]) {
        if ((parseFloat(s[`border${side}Width`]) || 0) < 1) continue;
        const b = over(rgba(s[`border${side}Color`]), fill);
        edge = Math.max(edge, ratio(b, outside));
      }
      if (edge < 3 - 0.005)
        add(
          "field-contrast",
          f,
          `its edge is ${edge.toFixed(2)}:1 against what it sits on, needs 3:1: a reader cannot see where to type (SC 1.4.11)`,
        );
    }
    stats.checked["field-contrast"] = n;
  });

  // ── layout-shift ─────────────────────────────────────────────────────────
  await run("layout-shift", () => {
    const m = window.__layoutProbe;
    if (!m || typeof m.cls !== "number") {
      stats.notMeasured.push("layout-shift (no observer installed before load)");
      return;
    }
    stats.cls = Math.round(m.cls * 10000) / 10000;
    if (m.cls > opts.clsThreshold) {
      add(
        "layout-shift",
        null,
        `cumulative layout shift ${stats.cls} (largest shift: ${(m.sources || []).slice(0, 2).join("; ") || "unknown source"})`,
      );
    }
  });

  // ── fonts ────────────────────────────────────────────────────────────────
  await run("font-failed", () => {
    const declared = new Set();
    for (const f of document.fonts) {
      declared.add(f.family.replace(/^["']|["']$/g, ""));
      if (f.status === "error")
        add("font-failed", null, `font "${f.family}" (${f.weight} ${f.style}) failed to load`);
    }
    const used = new Set();
    for (const el of document.querySelectorAll("body, h1, h2, h3, p, a, button")) {
      if (!visible(el)) continue;
      const first = cs(el)
        .fontFamily.split(",")[0]
        .trim()
        .replace(/^["']|["']$/g, "");
      if (declared.has(first))
        used.add(
          `${cs(el).fontWeight} ${cs(el).fontStyle === "italic" ? "italic " : ""}16px "${first}"`,
        );
    }
    for (const font of used) {
      if (!document.fonts.check(font))
        add("font-failed", null, `${font} is used but not loaded: the fallback is showing`);
    }
    stats.checked.fonts = used.size;
  });

  // ── chrome-share ─────────────────────────────────────────────────────────
  // ── fold: the page's h1 is on the first screen ────────────────────────────
  // A page whose heading ends below the first screen (a tall header, a tall
  // band on a phone on its side) opens on chrome and a photo, with its title
  // cut. The kit's worst case (a 32-character header name, a 70-character h1)
  // ends 47px inside a 320×568 screen.
  await run("fold", () => {
    window.scrollTo({ left: 0, top: 0, behavior: "instant" });
    const h1 = [...document.querySelectorAll("h1")].find((x) => visible(x));
    stats.checked.fold = h1 ? 1 : 0;
    if (!h1) return;
    const r = h1.getBoundingClientRect();
    if (r.bottom > H + 1)
      add(
        "fold",
        h1,
        `the page's h1 ends ${Math.round(r.bottom - H)}px below the first screen (${H}px tall): shorten the header or the band on short screens`,
      );
  });
  await run("chrome-share", () => {
    let covered = 0;
    for (const el of document.body.querySelectorAll("*")) {
      const s = cs(el);
      if (s.position !== "fixed" && s.position !== "sticky") continue;
      if (!visible(el)) continue;
      const r = el.getBoundingClientRect();
      if (r.width < W * 0.5) continue; // a floating button is not chrome
      const top = Math.max(0, r.top);
      const bottom = Math.min(H, r.bottom);
      if (bottom <= top) continue;
      if (r.top <= 1 || r.bottom >= H - 1) covered += bottom - top;
    }
    stats.chromeShare = Math.round((covered / H) * 100) / 100;
    if (covered / H > opts.maxChromeShare) {
      add(
        "chrome-share",
        null,
        `fixed and sticky bars cover ${Math.round((covered / H) * 100)}% of a ${H}px-tall viewport (keep it under ${Math.round(opts.maxChromeShare * 100)}%)`,
      );
    }
  });

  // ── what a reader meets while scrolling: overlap, anchors, the page's end ─
  const jump = (x, y) => window.scrollTo({ left: x, top: y, behavior: "instant" });
  await run("overlap", () => {
    const subjects = [
      ...new Set([
        ...textOwners(),
        ...document.querySelectorAll("a[href],button,input,select,textarea,summary"),
      ]),
    ].filter((el) => visible(el) && !el.closest("[data-slot='backdrop']") && !fixedish(el));
    const isControl = (el) => el.matches("a,button,input,select,textarea,summary");
    const boxes = (el) =>
      (isControl(el) ? [el.getBoundingClientRect()] : lineRects(el)).filter((r) => !tiny(r));
    // A stretched link's empty ::before/::after over a card is a hit area, not
    // paint: the card's text is still seen (text-hidden measures paint).
    const hitArea = (hit) =>
      ["::before", "::after"].some((pe) => {
        const p = getComputedStyle(hit, pe);
        return (
          p.content !== "none" &&
          /absolute|fixed/.test(p.position) &&
          rgba(p.backgroundColor)[3] === 0 &&
          p.backgroundImage === "none"
        );
      });
    // Every line, at ten points across its glyphs: a badge over the end of the
    // last line misses the centre of the first one.
    const XS = [0.1, 0.3, 0.5, 0.7, 0.9];
    const YS = [0.35, 0.7];
    const pending = new Map(subjects.map((el) => [el, null]));
    const maxY = Math.max(0, document.documentElement.scrollHeight - H);
    let n = 0;
    for (let y = 0; ; y = Math.min(maxY, y + Math.round(H * 0.8))) {
      jump(0, y);
      for (const [el, left] of pending) {
        const rects = boxes(el);
        const todo = left || new Set(rects.map((_, i) => i));
        for (const i of [...todo]) {
          const r = rects[i];
          if (!r) {
            todo.delete(i);
            continue;
          }
          if (r.top < 0 || r.bottom > H) continue;
          let barred = false;
          let over = null;
          for (const fy of YS) {
            for (const fx of XS) {
              const px = r.left + r.width * fx;
              const py = r.top + r.height * fy;
              if (px < 0 || px >= W) continue;
              const hit = document.elementFromPoint(px, py);
              if (!hit || hit === el || el.contains(hit) || hit.contains(el)) continue;
              if (fixedish(hit)) {
                barred = true; // under a bar at this scroll position: try the next one
                break;
              }
              if (el.closest("label") && el.closest("label").contains(hit)) continue;
              if (hitArea(hit)) continue;
              over = [hit, px, py];
              break;
            }
            if (barred || over) break;
          }
          if (barred) continue;
          todo.delete(i);
          n++;
          if (over) {
            add(
              "overlap",
              el,
              `${path(over[0])} is painted over ${rects.length > 1 ? `line ${i + 1} of ${rects.length}` : "it"} at (${Math.round(over[1])}, ${Math.round(over[2])})`,
            );
            todo.clear();
            break;
          }
        }
        if (todo.size) pending.set(el, todo);
        else pending.delete(el);
      }
      if (y >= maxY) break;
    }
    stats.checked.overlap = n;
  });
  await run("anchor-obscured", () => {
    let n = 0;
    const ids = new Set(
      [...document.querySelectorAll("a[href^='#']")]
        .map((a) => decodeURIComponent(a.getAttribute("href").slice(1)))
        .filter(Boolean),
    );
    for (const id of ids) {
      const target = document.getElementById(id);
      if (!target || !visible(target)) continue;
      n++;
      target.scrollIntoView({ block: "start", behavior: "instant" });
      const r = target.getBoundingClientRect();
      for (const fx of [0.1, 0.5, 0.9]) {
        const px = r.left + r.width * fx;
        const py = Math.max(0, r.top) + 4;
        if (py >= H || px < 0 || px >= W) continue;
        const hit = document.elementFromPoint(px, py);
        const bar = hit && !target.contains(hit) && !hit.contains(target) && fixedish(hit);
        if (bar) {
          add(
            "anchor-obscured",
            target,
            `#${id} lands under ${path(bar)}: give it scroll-margin-top as tall as the bar`,
          );
          break;
        }
      }
    }
    stats.checked["anchor-obscured"] = n;
  });
  await run("covered", () => {
    jump(0, document.documentElement.scrollHeight);
    let n = 0;
    for (const el of textOwners()) {
      const r = lineRects(el)[0];
      if (!r || fixedish(el) || r.top < 0 || r.bottom > H) continue;
      n++;
      const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      const bar = hit && hit !== el && !el.contains(hit) && !hit.contains(el) && fixedish(hit);
      if (bar)
        add(
          "covered",
          el,
          `at the end of the page it is still under ${path(bar)}: pad the page's end by the bar's height`,
        );
    }
    stats.checked.covered = n;
  });

  // ── focus: every focusable shows a ring, and nothing clips it ────────────
  await run("focus", () => {
    const sel =
      "a[href],button,input:not([type=hidden]),select,textarea,summary,[tabindex]:not([tabindex='-1'])";
    const els = [...document.querySelectorAll(sel)]
      .filter((el) => visible(el) && !el.matches(":disabled"))
      .slice(0, opts.maxFocus);
    let n = 0;
    for (const el of els) {
      el.focus({ focusVisible: true });
      if (document.activeElement !== el || !el.matches(":focus-visible")) continue;
      // The ring may be transitioning in (under reduced motion the kit gives every
      // property a 0.01ms transition): read it at its end, not at its start.
      for (const an of document.getAnimations()) {
        const t = an.effect && an.effect.target;
        if (t && (t === el || t.contains(el)) && an.effect.getComputedTiming().endTime !== Infinity)
          an.finish();
      }
      n++;
      // The ring may be drawn on the element or, for a linked photo, on its frame.
      let owner = null;
      for (let e = el, i = 0; e && i < 3; e = e.parentElement, i++) {
        const s = cs(e);
        if (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) {
          owner = e;
          break;
        }
      }
      if (!owner) {
        if (cs(el).boxShadow === "none")
          add(
            "focus-hidden",
            el,
            "focused, it shows no outline and no box-shadow: a keyboard user cannot see where they are (SC 2.4.7)",
          );
        continue;
      }
      const os = cs(owner);
      if (!forced && !owner.closest("[data-tone='media']")) {
        // An outline is drawn outside the box (offset >= 0), on the parent's colour.
        const behind = backdrop(parseFloat(os.outlineOffset) >= 0 ? owner.parentElement : owner);
        const ring = over(rgba(os.outlineColor), behind);
        const r = ratio(ring, behind);
        if (r < 3 - 0.005)
          add(
            "focus-contrast",
            el,
            `its focus ring is ${r.toFixed(2)}:1 against what it is drawn on, needs 3:1 (SC 1.4.11)`,
          );
      }
      const grow = parseFloat(os.outlineOffset) + parseFloat(os.outlineWidth);
      const or = owner.getBoundingClientRect();
      const ring = { l: or.left - grow, r: or.right + grow, t: or.top - grow, b: or.bottom + grow };
      for (let a = owner.parentElement; a && a !== document.body; a = a.parentElement) {
        const s = cs(a);
        if (scrolls(s) && !clips(s)) break;
        if (!clips(s)) continue;
        const ar = a.getBoundingClientRect();
        const cut = Math.max(
          ring.r - ar.right,
          ar.left - ring.l,
          ring.b - ar.bottom,
          ar.top - ring.t,
        );
        if (cut > 0.5)
          add(
            "focus-clipped",
            el,
            `${Math.round(cut)}px of its focus ring is cut off by ${path(a)}`,
          );
        break;
      }
    }
    stats.checked.focus = n;
  });

  // Put the page back as it was found.
  if (startFocus && startFocus.focus && startFocus !== document.body)
    startFocus.focus({ preventScroll: true });
  else if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
  jump(startX, startY);

  stats.counts = counts;
  stats.viewport = { width: W, innerWidth: window.innerWidth, height: H, dpr: DPR };
  return { findings, stats };
}

if (typeof module !== "undefined" && module.exports) module.exports = { layoutProbe };
