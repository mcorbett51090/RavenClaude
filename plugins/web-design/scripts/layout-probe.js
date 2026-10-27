/* layout-probe.js: measure a RENDERED page for the defects that stop a block
 * site looking pixel-perfect. Dependency-free; it runs in any browser context:
 *
 *   Playwright:   await page.evaluate(fs.readFileSync(probe, 'utf8') + ';layoutProbe(' + JSON.stringify(opts) + ')')
 *   DevTools MCP: evaluate_script with the file's text plus `;layoutProbe({})`
 *   A console:    paste the file, then `layoutProbe()`
 *
 * scripts/device_matrix.mjs runs it at every viewport, theme and breakpoint edge.
 * Every check reads the live layout (getBoundingClientRect, getComputedStyle,
 * Range rects, the font set), never the source: a class name in the HTML is a
 * claim about the page, and this measures the page.
 *
 * Checks (finding ids):
 *   overflow        an element is painted past the viewport edge, and no ancestor
 *                   clips it (html/body clipping does not count: it hides the
 *                   overflow instead of fixing it)
 *   zoom-out        the layout viewport is wider than the screen (opts.expectedWidth),
 *                   so a phone shows the whole page shrunk
 *   off-grid        a block's direct child does not sit on its grid line: its edges
 *                   differ by more than opts.edgeTolerance px from the other blocks'
 *                   children on the same line (content | wide | full), or a block is
 *                   not a grid at all, or a full / backdrop slot does not cover the
 *                   block edge to edge
 *   text-overflow   text sticks out of its box (a long word, a nowrap, a fixed width)
 *   text-clipped    text cut off by its box's overflow: hidden / clip
 *   heading-widow   a heading's last line is one short word
 *   target-size     an interactive target under 24×24px with no 24px spacing
 *                   (WCAG 2.2 SC 2.5.8; inline links in running text are exempt)
 *   input-zoom      a text field under 16px, which iOS zooms on focus
 *   orphan-row      a grid whose last row holds one narrow item under fuller rows
 *   grid-span       a grid with zero-width columns: items span tracks the grid does
 *                   not define (typically a container query that cannot match because
 *                   the grid IS the container it queries; put it inside a slot)
 *   image-broken    an image that did not load
 *   image-distorted an image stretched off its natural aspect ratio (object-fit: fill)
 *   image-upscaled  a raster image drawn bigger than its pixels at this DPR
 *   image-no-size   an image with no width/height, no aspect-ratio and no sized
 *                   frame: it will shift the layout when it loads
 *   img-alt         an <img> with no alt attribute (alt="" is a valid choice)
 *   layout-shift    cumulative layout shift above opts.clsThreshold (needs the
 *                   observer device_matrix.mjs installs before the page loads)
 *   font-failed     a web font that failed to load, or a used family not loaded
 *   chrome-share    fixed/sticky bars cover more than opts.maxChromeShare of the height
 *
 * Returns { findings: [{ id, where, msg }], stats }.
 */
// eslint-disable-next-line no-unused-vars
function layoutProbe(options) {
  const opts = Object.assign(
    {
      blockSelector: "[data-block]",
      expectedWidth: 0,
      edgeTolerance: 1,
      minTarget: 24,
      clsThreshold: 0.01,
      maxChromeShare: 0.3,
      upscaleTolerance: 1.15,
      maxPerCheck: 25,
      skip: [],
    },
    options || {},
  );
  const findings = [];
  const counts = {};
  const stats = { checked: {}, notMeasured: [] };
  const skip = new Set(opts.skip);
  const add = (id, el, msg) => {
    counts[id] = (counts[id] || 0) + 1;
    if (counts[id] <= opts.maxPerCheck) findings.push({ id, where: el ? path(el) : "page", msg });
  };
  const W = document.documentElement.clientWidth;
  const H = window.innerHeight;
  const DPR = window.devicePixelRatio || 1;

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
  function visible(el) {
    if (el.closest("[hidden],[inert],[aria-hidden='true']")) return false;
    const s = cs(el);
    if (s.display === "none" || s.visibility === "hidden" || s.visibility === "collapse")
      return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 || r.height > 0;
  }
  const tiny = (r) => r.width <= 1 && r.height <= 1;
  const clipsX = (s) =>
    s.overflowX !== "visible" || s.clipPath !== "none" || /paint|content|strict/.test(s.contain);
  // An ancestor (below body) that clips horizontally contains its descendants'
  // overflow on purpose; html and body do not, because their clipping is the
  // viewport's and hides the overflow from the reader instead of fixing it.
  function clippedByAncestor(el) {
    for (
      let a = el.parentElement;
      a && a !== document.body && a !== document.documentElement;
      a = a.parentElement
    ) {
      if (clipsX(cs(a))) return true;
    }
    return false;
  }
  const run = (id, fn) => {
    if (skip.has(id)) return;
    try {
      fn();
    } catch (e) {
      add("probe-error", null, `${id} threw: ${e && e.message}`);
    }
  };

  // ── overflow + zoom-out ──────────────────────────────────────────────────
  run("overflow", () => {
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
    for (const el of document.body.querySelectorAll("*")) {
      n++;
      const r = el.getBoundingClientRect();
      if (tiny(r) || (r.right <= W + 1 && r.left >= -1)) continue;
      if (!visible(el) || clippedByAncestor(el)) continue;
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
  run("off-grid", () => {
    const blocks = [...document.querySelectorAll(opts.blockSelector)].filter(visible);
    const lines = { content: [], wide: [], full: [] };
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
  });

  // ── text-overflow / text-clipped / heading-widow ─────────────────────────
  run("text-overflow", () => {
    const boxOf = (el) => {
      for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
        const d = cs(e).display;
        if (d !== "inline" && d !== "contents") return e;
      }
      return document.body;
    };
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    const seen = new Set();
    let n = 0;
    for (let t = walker.nextNode(); t && n < 8000; t = walker.nextNode()) {
      if (!t.nodeValue.trim()) continue;
      const el = t.parentElement;
      if (
        !el ||
        el.closest("script,style,noscript,template,svg,select,option,textarea") ||
        !visible(el)
      )
        continue;
      const box = boxOf(el);
      if (seen.has(box)) continue;
      const bs = cs(box);
      const br = box.getBoundingClientRect();
      if (tiny(br)) continue;
      if (bs.overflowX === "auto" || bs.overflowX === "scroll") continue; // scrolls on purpose
      if (bs.textOverflow === "ellipsis") continue; // truncates on purpose
      n++;
      const left = br.left + parseFloat(bs.borderLeftWidth) + parseFloat(bs.paddingLeft);
      const right = br.right - parseFloat(bs.borderRightWidth) - parseFloat(bs.paddingRight);
      range.selectNodeContents(t);
      for (const r of range.getClientRects()) {
        if (r.width === 0) continue;
        if (r.right > right + 1 || r.left < left - 1) {
          seen.add(box);
          const clipped = bs.overflowX === "hidden" || bs.overflowX === "clip";
          add(
            clipped ? "text-clipped" : "text-overflow",
            box,
            `"${t.nodeValue.trim().slice(0, 40)}" runs ${Math.round(Math.max(r.right - right, left - r.left))}px past its box${clipped ? " and is cut off" : ""}`,
          );
          break;
        }
      }
    }
    stats.checked["text-overflow"] = n;
    // A heading whose last line is one short word.
    let h = 0;
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
        add(
          "heading-widow",
          el,
          `"${el.textContent.trim().slice(0, 40)}" ends on a line holding only "${lastWord}" (text-wrap: balance fixes this)`,
        );
      }
    }
    stats.checked["heading-widow"] = h;
  });

  // ── target-size / input-zoom ─────────────────────────────────────────────
  run("target-size", () => {
    const sel =
      "a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=link],[tabindex]:not([tabindex='-1'])";
    const targets = [...document.querySelectorAll(sel)]
      .filter(visible)
      .map((el) => ({ el, r: el.getBoundingClientRect() }));
    const inlineInText = (el) => {
      if (el.tagName !== "A" || cs(el).display !== "inline") return false;
      const p = el.parentElement;
      return !!p && p.textContent.trim().length > el.textContent.trim().length + 10;
    };
    for (const t of targets) {
      const { el, r } = t;
      if (r.width >= opts.minTarget && r.height >= opts.minTarget) continue;
      if (inlineInText(el)) continue;
      // WCAG 2.5.8 spacing exception: a 24px circle on the target's centre must
      // not intersect another target.
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      const rad = opts.minTarget / 2;
      const hits = targets.some((o) => {
        if (o === t || o.el.contains(el) || el.contains(o.el)) return false;
        const nx = Math.max(o.r.left, Math.min(cx, o.r.right));
        const ny = Math.max(o.r.top, Math.min(cy, o.r.bottom));
        return (nx - cx) ** 2 + (ny - cy) ** 2 < rad * rad;
      });
      if (hits)
        add(
          "target-size",
          el,
          `${Math.round(r.width)}×${Math.round(r.height)}px target with a neighbour inside its 24px circle (SC 2.5.8)`,
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

  // ── orphan-row ───────────────────────────────────────────────────────────
  run("orphan-row", () => {
    let n = 0;
    for (const g of document.querySelectorAll("body *")) {
      const s = cs(g);
      if (s.display !== "grid" && s.display !== "inline-grid") continue;
      if (g.matches(opts.blockSelector)) continue; // the page grid: one slot per row by design
      const kids = [...g.children].filter(
        (k) => visible(k) && !["absolute", "fixed"].includes(cs(k).position),
      );
      // Zero-width tracks between real ones: items span columns the template does
      // not define, so the grid silently has fewer real columns than its CSS says.
      const tracks = s.gridTemplateColumns
        .split(/\s+/)
        .filter((t) => /px$/.test(t))
        .map(parseFloat);
      const gap = parseFloat(s.columnGap) || 0;
      if (kids.length && tracks.length > 1 && gap > 0 && tracks.some((t) => t < 0.5)) {
        add(
          "grid-span",
          g,
          `columns resolve to ${tracks.map((t) => Math.round(t)).join(" / ")}px: items span tracks the grid does not define (is this grid the container its own @container rule queries?)`,
        );
      }
      if (kids.length < 3) continue;
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
      if (
        last.length === 1 &&
        ordered.some((r) => r.length >= 2) &&
        last[0].getBoundingClientRect().width < 0.6 * gr.width
      ) {
        add(
          "orphan-row",
          g,
          `${kids.length} items laid out ${ordered.map((r) => r.length).join("+")}: the last one is alone on its row`,
        );
      }
    }
    stats.checked["orphan-row"] = n;
  });

  // ── images ───────────────────────────────────────────────────────────────
  run("images", () => {
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
      const nw = img.naturalWidth;
      const nh = img.naturalHeight;
      if (bw <= 0 || bh <= 0) continue;
      const fit = s.objectFit;
      if (fit === "fill" && Math.abs(bw / bh - nw / nh) / (nw / nh) > 0.02) {
        add(
          "image-distorted",
          img,
          `${nw}×${nh} image drawn ${Math.round(bw)}×${Math.round(bh)}: stretched (use a frame with object-fit: cover)`,
        );
      }
      const src = img.currentSrc || img.src || "";
      const vector = /\.svg(\?|#|$)/i.test(src) || src.startsWith("data:image/svg");
      if (!vector) {
        const scale =
          fit === "cover"
            ? Math.max(bw / nw, bh / nh)
            : fit === "contain" || fit === "scale-down"
              ? Math.min(bw / nw, bh / nh)
              : Math.max(bw / nw, bh / nh);
        if (scale * DPR > opts.upscaleTolerance) {
          add(
            "image-upscaled",
            img,
            `${nw}px-wide image drawn at ${(scale * DPR).toFixed(2)}× its pixels at DPR ${DPR}: blurry (add a larger srcset candidate)`,
          );
        }
      }
      const sized = img.hasAttribute("width") && img.hasAttribute("height");
      const parent =
        img.parentElement && img.parentElement.tagName === "PICTURE"
          ? img.parentElement.parentElement
          : img.parentElement;
      const framed = parent && cs(parent).aspectRatio !== "auto";
      if (!sized && s.aspectRatio === "auto" && !framed) {
        add(
          "image-no-size",
          img,
          "no width/height attributes, no aspect-ratio and no sized frame: the page will shift when it loads",
        );
      }
    }
    stats.checked.images = n;
  });

  // ── layout-shift ─────────────────────────────────────────────────────────
  run("layout-shift", () => {
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
  run("font-failed", () => {
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
  run("chrome-share", () => {
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

  stats.counts = counts;
  stats.viewport = { width: W, innerWidth: window.innerWidth, height: H, dpr: DPR };
  return { findings, stats };
}

if (typeof module !== "undefined" && module.exports) module.exports = { layoutProbe };
