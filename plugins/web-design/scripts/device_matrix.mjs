#!/usr/bin/env node
/* device_matrix.mjs: render a site at every screen it will meet and run
 * layout-probe.js on each page, so "pixel-perfect on every screen" is measured
 * rather than eyeballed at two widths.
 *
 * USAGE
 *   node device_matrix.mjs --dir dist                     a built site, served locally
 *   node device_matrix.mjs --url http://localhost:4321/   a running server (repeatable)
 *     --pages /,/menu/,/visit/   paths to test (default: / only)
 *     --manifest FILE            test every page a site manifest lists (repeatable)
 *     --quick                    one viewport per device class (default)
 *     --full                     every row of adaptive-layout's device table
 *     --sweep 320:1600:8         also every 8px from 320 to 1600 (catches the
 *                                in-between widths container queries produce)
 *     --themes light,dark,forced themes on the quick rows (default: all three)
 *     --shots DIR                full-page PNG per page × viewport × theme, for
 *                                visual-regression baselines
 *     --json FILE                write every finding as JSON
 *     --chrome PATH              a Chromium binary (else CHROME_BIN, else Playwright's)
 *   node device_matrix.mjs --self-test
 *     plants each defect the probe knows in a synthetic page built on
 *     templates/block-site/tokens.css + layout.css, requires each to be reported, and requires
 *     the clean control page to report nothing at every quick viewport in every
 *     theme. A probe that has never failed proves nothing.
 *
 * Breakpoint edges: every width a @media rule in the page's own CSS names is
 * tested at that width and one pixel either side (read from the CSSOM, so a
 * minifier's range syntax `(width<=860px)` and em units are handled).
 *
 * Layout shift must REPEAT to count. Measured 2026-10-27: headless Chromium
 * paints a first frame missing some author styles in about 4–8% of loads of a
 * clean page (padding and font size arrive one frame late; one bundled
 * stylesheet did not change the rate; the mechanism is not known). A shift the
 * page itself causes repeats on every load. So a page state that shifts is
 * reloaded in fresh contexts: shifting in 5 of 5 loads is a finding, and fewer
 * is printed as a note with its count, never hidden. (It was 3 of 3 until a run
 * on a loaded machine, two other browsers busy, reached 3 of 3 on a page that
 * shifted in 0 of 12 loads once the machine was quiet.)
 *
 * Needs Playwright (`npm i -D playwright`, then `npx playwright install chromium`)
 * resolvable from the current directory. Exit: 0 clean, 1 findings, 2 could not run.
 *
 * Chromium is not WebKit: emulation sets the width, DPR, touch and the viewport
 * tag, but has no Safari toolbar, no safe areas and no dynamic viewport. A green
 * run is necessary, not sufficient. Finish on a real iPhone and iPad.
 */
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { createServer } from "node:http";
import { deflateSync } from "node:zlib";
import {
  mkdtempSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
  existsSync,
  statSync,
  rmSync,
  copyFileSync,
} from "node:fs";
import { join, resolve, extname, dirname, normalize, sep } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROBE = readFileSync(join(HERE, "layout-probe.js"), "utf8");
const LAYOUT_CSS = join(HERE, "..", "templates", "block-site", "layout.css");

// ─── viewports (adaptive-layout Step 7; `quick` = one per device class) ──────
const VIEWPORTS = [
  { id: "reflow-320", w: 320, h: 568, dpr: 2, mobile: true, quick: true },
  { id: "iphone-se", w: 375, h: 667, dpr: 2, mobile: true },
  { id: "iphone", w: 390, h: 844, dpr: 3, mobile: true, quick: true },
  { id: "iphone-pro", w: 402, h: 874, dpr: 3, mobile: true },
  { id: "android", w: 420, h: 912, dpr: 2.625, mobile: true },
  { id: "iphone-max", w: 440, h: 956, dpr: 3, mobile: true },
  { id: "iphone-se-land", w: 667, h: 375, dpr: 2, mobile: true },
  { id: "iphone-land", w: 874, h: 402, dpr: 3, mobile: true, quick: true },
  { id: "iphone-max-land", w: 956, h: 440, dpr: 3, mobile: true },
  { id: "duo-outer", w: 382, h: 580, dpr: 3, mobile: true },
  { id: "duo-outer-land", w: 594, h: 368, dpr: 3, mobile: true },
  { id: "duo-inner", w: 669, h: 867, dpr: 3, mobile: true },
  { id: "duo-inner-land", w: 951, h: 585, dpr: 3, mobile: true },
  { id: "duo-split", w: 385, h: 571, dpr: 3, mobile: true },
  { id: "fold-cover", w: 344, h: 882, dpr: 3, mobile: true },
  { id: "fold-open", w: 836, h: 842, dpr: 2.625, mobile: true },
  { id: "ipad-mini", w: 756, h: 1158, dpr: 2, mobile: true },
  { id: "ipad", w: 820, h: 1180, dpr: 2, mobile: true, quick: true },
  { id: "ipad-pro-11", w: 834, h: 1210, dpr: 2, mobile: true },
  { id: "ipad-pro-13", w: 1032, h: 1376, dpr: 2, mobile: true },
  { id: "ipad-pro-13-land", w: 1376, h: 1032, dpr: 2, mobile: true },
  { id: "ipad-split-half", w: 688, h: 1032, dpr: 2, mobile: true },
  { id: "ipad-split-third", w: 375, h: 1032, dpr: 2, mobile: true },
  { id: "laptop-short", w: 1280, h: 720, dpr: 1, mobile: false },
  { id: "laptop", w: 1280, h: 800, dpr: 2, mobile: false, quick: true },
  { id: "laptop-15", w: 1470, h: 956, dpr: 2, mobile: false },
  { id: "desktop", w: 1920, h: 1080, dpr: 1, mobile: false, quick: true },
  { id: "desktop-qhd", w: 2560, h: 1440, dpr: 1, mobile: false },
];

const THEMES = {
  light: { colorScheme: "light", forcedColors: "none" },
  dark: { colorScheme: "dark", forcedColors: "none" },
  forced: { colorScheme: "light", forcedColors: "active" },
  contrast: { colorScheme: "light", forcedColors: "none", contrast: "more" },
  "contrast-dark": { colorScheme: "dark", forcedColors: "none", contrast: "more" },
};

// Installed before any page script: the probe reads it for layout-shift.
const CLS_OBSERVER = `(() => {
  window.__layoutProbe = { cls: 0, sources: [], last: 0 };
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        if (e.hadRecentInput) continue;
        window.__layoutProbe.cls += e.value;
        window.__layoutProbe.last = e.startTime;
        const node = (e.sources || []).map((s) => s.node).find((n) => n && n.nodeType === 1);
        if (node) window.__layoutProbe.sources.push(node.tagName.toLowerCase() + (node.className ? '.' + String(node.className).split(' ')[0] : '') + ' ' + e.value.toFixed(3));
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (_) { /* not Chromium: layout-shift is reported as not measured */ }
})();`;

// Make lazy images load, wait for fonts and image decodes, then wait until the
// page has gone 400ms without a layout shift (at most 3s), so a late shift is
// measured on every load rather than only when the probe happens to be slow.
const SETTLE = `(async () => {
  for (const img of document.images) if (img.loading === 'lazy') img.loading = 'eager';
  await Promise.race([
    Promise.all([document.fonts.ready, ...[...document.images].map((i) => i.decode().catch(() => {}))]),
    new Promise((r) => setTimeout(r, 6000)),
  ]);
  // Let every finite animation and transition end: under reduced motion the kit
  // gives each property a 0.01ms transition, and a style read inside it is stale.
  await Promise.race([
    Promise.all(document.getAnimations()
      .filter((a) => a.effect && a.effect.getComputedTiming().endTime !== Infinity)
      .map((a) => a.finished.catch(() => {}))),
    new Promise((r) => setTimeout(r, 2000)),
  ]);
  const start = performance.now();
  const m = window.__layoutProbe;
  while (performance.now() - start < 3000) {
    await new Promise((r) => setTimeout(r, 100));
    const quietSince = Math.max(start, m ? m.last : 0);
    if (performance.now() - quietSince >= 400) break;
  }
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
})()`;

// Every width a @media rule names, as CSS px, from the live CSSOM.
const BREAKPOINTS = `(() => {
  const out = new Set();
  const cq = new Set();
  const px = (n, u) => (u === 'px' ? n : n * 16);
  const scan = (rules) => {
    for (const r of rules || []) {
      const t = r.conditionText || (r.media && r.media.mediaText) || '';
      const isContainer = typeof CSSContainerRule !== 'undefined' && r instanceof CSSContainerRule;
      if (t) {
        for (const m of t.matchAll(/(min-|max-)?width\\s*(?::|[<>]=?)\\s*([\\d.]+)(px|em|rem)/g)) {
          (isContainer ? cq : out).add(Math.round(px(parseFloat(m[2]), m[3])));
        }
        for (const m of t.matchAll(/([\\d.]+)(px|em|rem)\\s*[<>]=?\\s*width/g)) {
          (isContainer ? cq : out).add(Math.round(px(parseFloat(m[1]), m[2])));
        }
      }
      if (r.cssRules) scan(r.cssRules);
    }
  };
  for (const s of document.styleSheets) { try { scan(s.cssRules); } catch (_) { /* cross-origin sheet */ } }
  return { media: [...out].sort((a, b) => a - b), container: [...cq].sort((a, b) => a - b) };
})()`;

function loadPlaywright() {
  const tries = [process.cwd() + "/", import.meta.url];
  for (const base of tries) {
    try {
      return createRequire(base)("playwright");
    } catch (_) {
      /* next */
    }
  }
  return null;
}

// ─── static server for --dir ─────────────────────────────────────────────────
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".txt": "text/plain",
  ".xml": "application/xml",
  ".webmanifest": "application/manifest+json",
};
function serve(root) {
  const base = resolve(root);
  const server = createServer((req, res) => {
    let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
    let f = normalize(join(base, p));
    if (f !== base && !f.startsWith(base + sep)) {
      res.writeHead(403).end();
      return;
    }
    if (existsSync(f) && statSync(f).isDirectory()) f = join(f, "index.html");
    else if (!existsSync(f) && existsSync(f + ".html")) f += ".html";
    if (!existsSync(f)) {
      const nf = join(base, "404.html");
      res
        .writeHead(404, { "content-type": TYPES[".html"] })
        .end(existsSync(nf) ? readFileSync(nf) : "not found");
      return;
    }
    res
      .writeHead(200, {
        "content-type": TYPES[extname(f).toLowerCase()] || "application/octet-stream",
      })
      .end(readFileSync(f));
  });
  return new Promise((ok) =>
    server.listen(0, "127.0.0.1", () =>
      ok({ server, origin: `http://127.0.0.1:${server.address().port}` }),
    ),
  );
}

// ─── the run ─────────────────────────────────────────────────────────────────
async function probePage(page, expectedWidth, skip = []) {
  await page.evaluate(SETTLE);
  return page.evaluate(`${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth, skip })})`);
}

/** Load a URL; a page that does not answer 2xx is a failure, never a silent pass. */
async function load(page, url) {
  const res = await page.goto(url, { waitUntil: "load" });
  if (!res || res.status() < 200 || res.status() > 299)
    throw new Error(`${url} answered ${res ? res.status() : "nothing"}; check --pages`);
}

// A layout shift is a finding only when it repeats in every one of this many loads.
const SHIFT_LOADS = 5;

/** Reload a page that shifted in fresh contexts; count the loads that shift again. */
async function reloadShifts(browser, v, theme, url, times) {
  let n = 0;
  for (let i = 0; i < times; i++) {
    const ctx = await newStateContext(browser, v, theme);
    const page = await ctx.newPage();
    await load(page, url);
    const { findings } = await probePage(page, v.w);
    if (findings.some((x) => x.id === "layout-shift")) n++;
    await ctx.close();
  }
  return n;
}

// What a closed <details> hides (a site menu, an FAQ answer) is laid out only
// when it opens, so the probe runs again with every one open. Checks that read
// what is UNDER an open menu (overlap, anchors, fixed bars) are skipped: a
// dropdown covers the page by design.
const OPEN_SKIP = [
  "layout-shift",
  "font-failed",
  "images",
  "overlap",
  "anchor-obscured",
  "covered",
  "focus",
];
async function detailsOpen(page, width) {
  const n = await page.evaluate(`(() => {
    const shut = [...document.querySelectorAll("details:not([open])")];
    for (const d of shut) { d.setAttribute("data-dm-opened", ""); d.open = true; }
    return shut.length;
  })()`);
  if (!n) return [];
  await page.evaluate(SETTLE);
  const { findings } = await page.evaluate(
    `${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth: width, skip: OPEN_SKIP })})`,
  );
  await page.evaluate(`(() => {
    for (const d of document.querySelectorAll("details[data-dm-opened]")) { d.open = false; d.removeAttribute("data-dm-opened"); }
  })()`);
  await page.evaluate(FRAME);
  return findings.map((x) => ({ ...x, msg: `${x.msg} (with every <details> open)` }));
}

async function newStateContext(browser, v, theme) {
  const ctx = await browser.newContext({
    viewport: { width: v.w, height: v.h },
    deviceScaleFactor: v.dpr,
    isMobile: v.mobile,
    hasTouch: v.mobile,
    reducedMotion: "reduce",
    ...THEMES[theme],
  });
  await ctx.addInitScript(CLS_OBSERVER);
  await ctx.route(/googletagmanager\.com|google-analytics\.com|cloudflareinsights\.com/, (r) =>
    r.abort(),
  );
  return ctx;
}

// ─── photo-contrast: text over a photograph, on composited pixels ────────────
// No colour stands in for a photograph, so the probe's text-contrast check skips
// text over one, and this scores it instead (knowledge/text-over-photo-contrast-
// 2026.md §1): hide every glyph (text-shadow and the element's own background
// stay, because they sit behind the glyphs), capture the VIEWPORT, and score each
// text line's box pixel by pixel against the text colour composited at its own
// alpha × its ancestors' opacity. The 5th-percentile pixel is the reading: a
// bright patch behind a fifth of a line fails, one specular highlight does not.
// 4.5:1, or 3:1 at 24px / 18.66px bold. The percentile is a HEURISTIC; WCAG names
// no sampling rule for a photograph. Ported from the owner's factory, where it
// was built and broken on purpose (RavenPower-website-factory PR #131).
const PHOTO_FIND = `(async () => {
  // Two frames first: under reduced motion a style changed just before this
  // (a mutation, a theme) is still mid-transition, and its colour reads stale.
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  for (const img of document.images) if (img.loading === 'lazy') img.loading = 'eager';
  await Promise.race([
    Promise.all([...document.images].map((i) => i.decode().catch(() => {}))),
    new Promise((r) => setTimeout(r, 4000)),
  ]);
  const SX = scrollX, SY = scrollY;
  const vis = (el) => {
    if (el.closest('[aria-hidden="true"],[hidden],[inert]')) return false;
    if (el.closest('details:not([open]) > :not(summary)')) return false;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.visibility === 'collapse') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const path = (el) => {
    const parts = [];
    for (let e = el; e && e.nodeType === 1 && parts.length < 4; e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.id) { s += '#' + e.id; parts.unshift(s); break; }
      if (e.dataset && e.dataset.block) s += '[data-block="' + e.dataset.block + '"]';
      else { const c = [...e.classList].slice(0, 2).join('.'); if (c) s += '.' + c; }
      parts.unshift(s);
    }
    return parts.join(' > ');
  };
  const media = [];
  for (const m of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(m);
    if (!/^(IMG|VIDEO|CANVAS)$/.test(m.tagName) && !/url\\(/.test(cs.backgroundImage)) continue;
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = m.getBoundingClientRect();
    if (r.width < 48 || r.height < 48) continue;
    media.push({ el: m, l: r.left + SX, t: r.top + SY, r: r.right + SX, b: r.bottom + SY });
  }
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgba = (css) => {
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = css; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const clipTo = (el, q) => {
    for (let a = el; a && a !== document.body; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (cs.overflowX === 'visible' && cs.overflowY === 'visible' && cs.clip === 'auto' && cs.clipPath === 'none') continue;
      const r = a.getBoundingClientRect();
      q = { l: Math.max(q.l, r.left + SX), t: Math.max(q.t, r.top + SY), r: Math.min(q.r, r.right + SX), b: Math.min(q.b, r.bottom + SY) };
    }
    return q;
  };
  const groups = new Map();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest('svg,script,style,noscript,template,canvas') || !vis(el)) continue;
    range.selectNodeContents(n);
    const rects = [...range.getClientRects()]
      .map((r) => clipTo(el, { l: r.left + SX, t: r.top + SY, r: r.right + SX, b: r.bottom + SY }))
      .filter((q) => q.r - q.l >= 2 && q.b - q.t >= 6);
    // Only the part of a line that lies over a photo is scored, and only when
    // that part is a real share of the line: a line box whose top edge grazes a
    // band above it has its glyphs on the flat colour, not on the photo.
    const over = [];
    for (const q of rects) {
      let best = null;
      for (const m of media) {
        if (el.contains(m.el)) continue;
        const i = { l: Math.max(q.l, m.l), t: Math.max(q.t, m.t), r: Math.min(q.r, m.r), b: Math.min(q.b, m.b) };
        if (i.r - i.l < 2 || i.b - i.t < Math.max(6, (q.b - q.t) / 3)) continue;
        if (!best || (i.r - i.l) * (i.b - i.t) > (best.r - best.l) * (best.b - best.t)) best = i;
      }
      if (best) over.push(best);
    }
    if (!over.length) continue;
    if (!groups.has(el)) groups.set(el, []);
    groups.get(el).push(...over);
  }
  const out = [];
  for (const [el, rects] of groups) {
    const cs = getComputedStyle(el);
    if (cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') continue;
    // Forced colours paint the forced color; the fill still reports the author's.
    const fill = matchMedia('(forced-colors: active)').matches ? cs.color : cs.webkitTextFillColor || cs.color;
    const fg = rgba(fill);
    let alpha = fg[3];
    for (let a = el; a && a !== document.documentElement; a = a.parentElement) alpha *= Number(getComputedStyle(a).opacity);
    if (alpha < 0.02) continue;
    const size = parseFloat(cs.fontSize), weight = Number(cs.fontWeight) || 400;
    out.push({ k: out.length, where: path(el), text: el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40),
      fg: fg.slice(0, 3), alpha, size, large: size >= 24 || (size >= 18.66 && weight >= 700),
      rects, top: Math.min(...rects.map((r) => r.t)), bottom: Math.max(...rects.map((r) => r.b)) });
    el.setAttribute('data-dm-photo', String(out.length - 1));
  }
  return out;
})()`;

// ':root *' outranks a bare '*', so a page's own !important colour cannot survive
// the hide. Whether the hide LANDED is asserted, not assumed.
// The kit's reduced-motion rule gives every property a 0.01ms transition, from a
// layered !important that no unlayered rule can switch off; so the hide waits two
// frames for that transition to end before it is checked and the capture taken.
const PHOTO_HIDE = `(async () => {
  const s = document.createElement('style'); s.setAttribute('data-dm-photo-hide', '');
  s.textContent = ':root *,:root *::before,:root *::after{-webkit-text-fill-color:transparent!important;'
    + 'text-decoration-color:transparent!important;caret-color:transparent!important}'
    + ':root{scroll-behavior:auto!important}';
  document.head.appendChild(s);
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  return [...document.querySelectorAll('[data-dm-photo]')]
    .filter((el) => !/^rgba\\(0, 0, 0, 0\\)$|^transparent$/.test(getComputedStyle(el).webkitTextFillColor))
    .map((el) => el.tagName.toLowerCase() + ' ' + getComputedStyle(el).webkitTextFillColor);
})()`;
const PHOTO_UNHIDE = `(() => { for (const s of document.querySelectorAll('style[data-dm-photo-hide]')) s.remove();
  for (const el of document.querySelectorAll('[data-dm-photo]')) el.removeAttribute('data-dm-photo'); })()`;

const PHOTO_SAMPLE = (b64, cands, dpr) => `(async () => {
  const C = ${JSON.stringify(cands)};
  const SX = scrollX, SY = scrollY, W = innerWidth, H = innerHeight;
  const img = new Image(); img.src = 'data:image/png;base64,${b64}'; await img.decode();
  const k = img.width / W;
  const geometry = { k, kh: img.height / H, dpr: ${dpr}, w: img.width, h: img.height, W, H };
  const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height;
  const ctx = cv.getContext('2d', { willReadFrequently: true }); ctx.drawImage(img, 0, 0);
  const data = ctx.getImageData(0, 0, img.width, img.height).data;
  const LIN = Array.from({ length: 256 }, (_, v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
  const Y = (r, g, b) => 0.2126 * LIN[Math.round(r)] + 0.7152 * LIN[Math.round(g)] + 0.0722 * LIN[Math.round(b)];
  const underChrome = (el, x, y) => {
    for (let e = document.elementFromPoint(x, y); e; e = e.parentElement) {
      if (e === el || e.contains(el)) return false;
      const p = getComputedStyle(e).position;
      if (p === 'fixed' || p === 'sticky') return true;
    }
    return false;
  };
  const step = Math.max(1, Math.round(k));
  const res = [];
  for (const c of C) {
    const el = document.querySelector('[data-dm-photo="' + c.k + '"]');
    const lines = c.rects.map((q) => ({ l: q.l - SX, t: q.t - SY, r: q.r - SX, b: q.b - SY }))
      .filter((q) => q.t >= 0 && q.b <= H && q.r > 0 && q.l < W);
    if (!el || !lines.length) continue;
    const full = lines.length === c.rects.length;
    const q0 = lines[0];
    if (underChrome(el, Math.min(W - 1, Math.max(0, (q0.l + q0.r) / 2)), (q0.t + q0.b) / 2)) continue;
    const [fr, fgc, fb] = c.fg, a = c.alpha;
    const ratios = [];
    for (const q of lines) {
      const x0 = Math.max(0, Math.round(q.l * k)), x1 = Math.min(img.width, Math.round(q.r * k));
      const y0 = Math.max(0, Math.round(q.t * k)), y1 = Math.min(img.height, Math.round(q.b * k));
      for (let y = y0; y < y1; y += step) for (let x = x0; x < x1; x += step) {
        const i = (y * img.width + x) * 4;
        const br = data[i], bg = data[i + 1], bb = data[i + 2];
        const Lb = Y(br, bg, bb);
        const Lt = Y(a * fr + (1 - a) * br, a * fgc + (1 - a) * bg, a * fb + (1 - a) * bb);
        ratios.push((Math.max(Lb, Lt) + 0.05) / (Math.min(Lb, Lt) + 0.05));
      }
    }
    if (!ratios.length) continue;
    ratios.sort((x, y) => x - y);
    res.push({ k: c.k, full, n: ratios.length, p5: ratios[Math.floor(ratios.length * 0.05)],
      median: ratios[Math.floor(ratios.length / 2)] });
  }
  return { geometry, res };
})()`;

const MAX_PHOTO_SHOTS = 12;
const FRAME = `new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))`;

/** Score every text line over a photo on this page, at this viewport. Returns findings. */
async function photoContrast(page, v, stats) {
  const findings = [];
  const cands = await page.evaluate(PHOTO_FIND);
  if (!cands.length) return findings;
  const missed = await page.evaluate(PHOTO_HIDE);
  if (missed.length) {
    throw new Error(
      `hiding the text did NOT land on ${missed.length} element(s) of ${page.url()} (${missed.slice(0, 3).join("; ")}): the capture would score glyphs against themselves`,
    );
  }
  try {
    const pending = [...cands].sort((x, y) => x.top - y.top);
    for (let shots = 0; pending.length && shots < MAX_PHOTO_SHOTS; shots++) {
      // The first pending line a quarter of the way down: under any top chrome,
      // with the lines below it in the same shot.
      await page.evaluate(
        `(async () => { scrollTo({ top: Math.max(0, ${pending[0].top} - innerHeight / 4), behavior: 'instant' }); await ${FRAME}; })()`,
      );
      const shot = (
        await page.screenshot({ type: "png", animations: "disabled", caret: "hide" })
      ).toString("base64");
      const { geometry: g, res } = await page.evaluate(PHOTO_SAMPLE(shot, pending, v.dpr));
      // ⛔ The capture's geometry is asserted: a capture that is not the viewport at
      // the device's pixel ratio puts every sample somewhere else on the page, and
      // the readings are still plausible numbers.
      if (Math.abs(g.k - g.dpr) > 0.05 || Math.abs(g.kh - g.dpr) > 0.05) {
        throw new Error(
          `the capture is ${g.w}x${g.h} for a ${g.W}x${g.H} viewport at dpr ${g.dpr}: every photo-contrast sample would be misplaced`,
        );
      }
      const scored = res.filter((r) => r.full || r.k === pending[0].k);
      const done = new Set(scored.map((r) => r.k));
      if (!done.has(pending[0].k)) {
        stats.photoUnscored++;
        done.add(pending[0].k);
      }
      for (const r of scored) {
        const c = cands[r.k];
        const need = c.large ? 3 : 4.5;
        stats.photoTexts++;
        if (r.p5 / need < stats.minPhoto) {
          stats.minPhoto = r.p5 / need;
          stats.minPhotoAt = `"${c.text.slice(0, 24)}" ${r.p5.toFixed(2)}:1 on ${new URL(page.url()).pathname} @ ${v.id}`;
        }
        if (r.p5 < need) {
          findings.push({
            id: "photo-contrast",
            where: c.where,
            msg:
              `${Math.round(c.size * 10) / 10}px "${c.text}" measures ${r.p5.toFixed(2)}:1 against the photo behind it ` +
              `(5th-percentile pixel; median ${r.median.toFixed(2)}:1), needs ${need}:1 (SC 1.4.3)`,
          });
        }
      }
      for (let i = pending.length - 1; i >= 0; i--)
        if (done.has(pending[i].k)) pending.splice(i, 1);
    }
    stats.photoUnscored += pending.length;
  } finally {
    await page.evaluate(PHOTO_UNHIDE);
    await page.evaluate("scrollTo({ top: 0, behavior: 'instant' })");
  }
  return findings;
}

async function runMatrix({
  chromium,
  urls,
  viewports,
  themes,
  sweep,
  shots,
  launch,
  photo = true,
}) {
  const browser = await chromium.launch(launch);
  const findings = [];
  const notes = new Set();
  const photoStats = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
  let states = 0;
  try {
    // Breakpoint edges from the first URL's own CSS.
    const probeCtx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const p0 = await probeCtx.newPage();
    await load(p0, urls[0]);
    const bp = await p0.evaluate(BREAKPOINTS);
    await probeCtx.close();
    const edgeWidths = new Set();
    for (const w of bp.media) for (const d of [-1, 0, 1]) if (w + d >= 280) edgeWidths.add(w + d);
    const edges = [...edgeWidths].map((w) => ({
      id: `edge-${w}`,
      w,
      h: 900,
      dpr: 2,
      mobile: w < 1024,
    }));
    if (bp.container.length)
      notes.add(
        `container-query thresholds in the CSS: ${bp.container.join(", ")}px of container width (covered by --sweep, not by viewport edges)`,
      );

    const rows = [
      ...viewports.map((v) => ({ ...v, themes: v.quick ? themes : ["light"] })),
      ...edges.map((v) => ({ ...v, themes: ["light"] })),
    ];
    for (const v of rows) {
      for (const theme of v.themes) {
        const ctx = await newStateContext(browser, v, theme);
        const page = await ctx.newPage();
        for (const url of urls) {
          await load(page, url);
          let { findings: f, stats } = await probePage(page, v.w);
          states++;
          for (const n of stats.notMeasured || []) notes.add(n);
          if (f.some((x) => x.id === "layout-shift")) {
            const shifted = 1 + (await reloadShifts(browser, v, theme, url, SHIFT_LOADS - 1));
            if (shifted < SHIFT_LOADS) {
              f = f.filter((x) => x.id !== "layout-shift");
              notes.add(
                `layout shift on ${new URL(url).pathname} @ ${v.id} ${theme} in ${shifted} of ${SHIFT_LOADS} loads: not reproducible, so not a finding (see the header)`,
              );
            } else {
              f = f.map((x) =>
                x.id === "layout-shift"
                  ? { ...x, msg: `${x.msg}; shifted in ${SHIFT_LOADS} of ${SHIFT_LOADS} loads` }
                  : x,
              );
            }
          }
          // Text over photos: one viewport per device class (the crop changes with
          // the aspect ratio), in every theme but forced colours. There the browser
          // paints glyphs in the forced colour whatever -webkit-text-fill-color says,
          // so the hide cannot land (its computed-style check would still pass):
          // the method does not apply, and the kit gives the copy an opaque Canvas
          // backplate instead, which --self-test checks.
          if (photo && v.quick && theme !== "forced")
            f = f.concat(await photoContrast(page, v, photoStats));
          else if (photo && v.quick && theme === "forced")
            notes.add(
              "photo-contrast: not scored in forced colours (glyphs paint in the forced colour and cannot be hidden for the capture)",
            );
          f = f.concat(await detailsOpen(page, v.w));
          for (const x of f) findings.push({ ...x, url, vp: `${v.id} ${v.w}×${v.h}`, theme });
          if (shots) {
            mkdirSync(shots, { recursive: true });
            const name = `${new URL(url).pathname.replace(/[^a-z0-9]+/gi, "_") || "_"}__${v.id}__${theme}.png`;
            await page.screenshot({
              path: join(shots, name),
              fullPage: true,
              animations: "disabled",
              caret: "hide",
            });
          }
        }
        await ctx.close();
      }
    }
    if (sweep) {
      const [from, to, step] = sweep;
      const ctx = await browser.newContext({
        viewport: { width: from, height: 900 },
        deviceScaleFactor: 1,
        reducedMotion: "reduce",
      });
      const page = await ctx.newPage();
      for (const url of urls) {
        await load(page, url);
        await page.evaluate(SETTLE);
        for (let w = from; w <= to; w += step) {
          await page.setViewportSize({ width: w, height: 900 });
          await page.evaluate(FRAME);
          const { findings: f } = await page.evaluate(
            `${PROBE}\n;layoutProbe(${JSON.stringify({ expectedWidth: w, skip: ["layout-shift", "font-failed", "images", "overlap", "anchor-obscured", "covered", "focus"] })})`,
          );
          states++;
          for (const x of f) findings.push({ ...x, url, vp: `sweep ${w}px`, theme: "light" });
        }
      }
      await ctx.close();
    }
    if (photoStats.photoTexts)
      notes.add(
        `photo-contrast: ${photoStats.photoTexts} line(s) over photos scored; lowest ${photoStats.minPhotoAt} (${(photoStats.minPhoto * 100).toFixed(0)}% of its bar)${photoStats.photoUnscored ? `; ${photoStats.photoUnscored} could not be scored` : ""}`,
      );
    return { findings, notes: [...notes], states, breakpoints: bp, photo: photoStats };
  } finally {
    await browser.close();
  }
}

function report({ findings, notes, states, breakpoints }) {
  const groups = new Map();
  for (const f of findings) {
    // One group per defect: the same check on the same element, wherever it shows.
    const k = [f.id, f.url, f.where].join("|");
    if (!groups.has(k)) groups.set(k, { ...f, at: [] });
    groups.get(k).at.push(`${f.vp}${f.theme === "light" ? "" : " " + f.theme}`);
  }
  console.log(
    `device-matrix: ${states} page states; media breakpoints ${breakpoints.media.length ? `${breakpoints.media.join(", ")}px (each tested ±1px)` : "none"}`,
  );
  for (const n of notes) console.log(`  note  ${n}`);
  if (!states) {
    console.log("device-matrix: 0 page states were tested. THIS IS NOT A PASS.");
    return 2;
  }
  if (!groups.size) {
    console.log("device-matrix: OK, no findings.");
    console.log(
      "Chromium is not WebKit: finish on a real iPhone and iPad (adaptive-layout Step 7).",
    );
    return 0;
  }
  console.log(`device-matrix: ${findings.length} finding(s) in ${groups.size} group(s):`);
  for (const g of groups.values()) {
    const at =
      g.at.length > 4 ? `${g.at.slice(0, 4).join(", ")} +${g.at.length - 4} more` : g.at.join(", ");
    console.log(
      `  ✗ [${g.id}] ${new URL(g.url).pathname} ${g.where}\n      ${g.msg}\n      at ${at}`,
    );
  }
  return 1;
}

// ─── self-test ───────────────────────────────────────────────────────────────
function crc32(buf) {
  let c;
  const table = (crc32.t ||= Array.from({ length: 256 }, (_, n) => {
    c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    return c >>> 0;
  }));
  let crc = 0xffffffff;
  for (const b of buf) crc = table[(crc ^ b) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}
/** A solid-colour RGB PNG of w×h: real raster pixels for the image checks. */
function png(w, h, [r, g, b]) {
  const chunk = (type, data) => {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type), data]);
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(td));
    return Buffer.concat([len, td, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr.set([8, 2, 0, 0, 0], 8);
  const row = Buffer.alloc(1 + w * 3);
  for (let x = 0; x < w; x++) row.set([r, g, b], 1 + x * 3);
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

const LONG_WORD = "Donaudampfschifffahrtsgesellschaftskapitänswitwe";
const PROSE =
  "Long-running copy that wraps across several lines, so the width of each line can be measured against a comfortable reading measure on every screen it meets.";
/** A synthetic page on the kit's three stylesheets, for planting one defect at a time. */
function page({ head = "", top = "", extra = "", cards = 5 } = {}) {
  const card = (i) =>
    `<article class="card stack"><h3>Feature ${i}</h3><p class="muted">One honest sentence about what this does for a customer.</p></article>`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Self-test</title><link rel="stylesheet" href="/tokens.css"><link rel="stylesheet" href="/layout.css"><link rel="stylesheet" href="/blocks.css">${head}</head><body>
${top}
<header data-block="site-header" data-tone="canvas" data-space="s" class="site-header"><div class="site-header__bar"><a class="brand" href="/">Diner</a><nav class="site-nav" aria-label="Main"><ul role="list"><li><a href="/">Home</a></li><li><a href="/menu/">Menu</a></li></ul></nav></div></header>
<main id="main">
<section data-block="hero-full" data-tone="media" data-space="l" aria-labelledby="h1">
  <div data-slot="backdrop"><picture><source media="(max-width: 30em) and (orientation: portrait)" srcset="/portrait.png" width="1200" height="1800"><img src="/landscape.png" width="2560" height="1440" alt=""></picture></div>
  <div class="on-photo stack"><h1 id="h1">Breakfast all day, since 1945</h1><p>A diner that still makes its biscuits by hand every morning.</p><div class="cluster"><a class="button" href="/menu/">See the menu</a><a class="button" data-variant="ghost" href="/visit/">Plan a visit</a></div></div>
</section>
<section data-block="features-grid" data-tone="canvas" aria-labelledby="h2a"><div><h2 id="h2a">Why people come back</h2></div><div><div class="cards">${Array.from({ length: cards }, (_, i) => card(i + 1)).join("")}</div></div></section>
<section data-block="story-split" data-tone="surface" aria-labelledby="h2b"><div class="switcher" style="--switch-at: 44rem"><div class="frame" style="--ratio: 4 / 3"><img src="/story.png" width="1200" height="900" alt="The original counter"></div><div class="prose stack"><h2 id="h2b">Same counter, same recipes</h2><p>${PROSE}</p></div></div></section>
<section data-block="contact-form" data-tone="canvas" aria-labelledby="h2c"><div><form class="stack prose" action="#main"><h2 id="h2c">Ask us anything</h2><div class="field"><label for="em">Email</label><input id="em" type="email" autocomplete="email"></div><div><button class="button" type="submit">Send</button></div></form></div></section>
<section data-block="cta-banner" data-tone="inverse" aria-labelledby="h2d"><div class="cluster"><h2 id="h2d">Hungry yet?</h2><a class="button" href="/book/">Book a table</a></div></section>
${extra}
</main>
<footer data-block="site-footer" data-tone="surface" data-space="s" class="site-footer"><div><p>© Example Diner · 411 Fairhope Ave</p></div></footer>
</body></html>`;
}

const sec = (inner, tone = "canvas") =>
  `<section data-block="m" data-tone="${tone}"><div>${inner}</div></section>`;
const MUTATIONS = [
  {
    expect: "overflow",
    vp: "iphone",
    html: {
      extra: sec(
        `<div style="inline-size: 560px; block-size: 8px; background: var(--accent)"></div>`,
      ),
    },
  },
  {
    expect: "zoom-out",
    vp: "iphone",
    html: { head: `<style>body { min-inline-size: 600px; }</style>` },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><p style="margin-inline-start: 7px">Nudged seven pixels off the content line.</p></section>`,
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a block that is not a grid",
    html: {
      extra: `<section data-block="m" data-tone="canvas" style="display: block"><p>Not on the page grid.</p></section>`,
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a measure-limited child placed directly on the line",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="prose"><p>Prose is narrower than the content line, so it belongs INSIDE a slot.</p></div></section>`,
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a ported wrapper that pads its text off the line",
    html: {
      extra: sec(
        `<div style="padding-inline: 15px"><p>A container class from another site.</p></div>`,
      ),
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "an embed that runs into the gutter",
    html: {
      extra: sec(
        `<div style="margin-inline-start: -48px; block-size: 40px; background: var(--rule)">Embed</div>`,
      ),
    },
  },
  {
    expect: "off-grid",
    vp: "laptop",
    why: "a photo backdrop boxed inside the content line",
    html: {
      head: `<style>@layer overrides { [data-tone="media"] > [data-slot="backdrop"] { grid-column: content !important; } }</style>`,
    },
  },
  {
    expect: "text-overflow",
    vp: "reflow-320",
    html: {
      extra: sec(`<p style="overflow-wrap: normal; hyphens: manual">${LONG_WORD}${LONG_WORD}</p>`),
    },
  },
  {
    expect: "text-overflow",
    vp: "laptop",
    why: "text spilling out of the bottom of a fixed-height card",
    html: {
      extra: sec(
        `<article class="card" style="block-size: 4rem; inline-size: 14rem"><p>${PROSE}</p></article>`,
      ),
    },
  },
  {
    expect: "text-clipped",
    vp: "iphone",
    html: {
      extra: sec(
        `<p style="inline-size: 9rem; overflow: hidden; white-space: nowrap">A caption far too long for its fixed box</p>`,
      ),
    },
  },
  {
    expect: "clipped",
    vp: "laptop",
    why: "a button wider than the card that clips it",
    html: {
      extra: sec(
        `<article class="card" style="overflow: hidden; inline-size: 12rem"><a class="button" href="/menu/" style="inline-size: 18rem">A button wider than its card</a></article>`,
      ),
    },
  },
  {
    expect: "overlap",
    vp: "laptop",
    why: "a badge painted over a heading",
    html: {
      extra: sec(
        `<div style="position: relative"><h3>A heading under a badge</h3><span style="position: absolute; inset: 0; background: var(--accent); color: var(--on-accent)">New</span></div>`,
      ),
    },
  },
  {
    expect: "heading-widow",
    vp: "laptop",
    html: {
      extra: sec(
        `<h2 style="font-family: monospace; font-size: 20px; inline-size: 11ch; text-wrap: wrap">aaaaa bbbbb c</h2>`,
      ),
    },
  },
  {
    expect: "measure",
    vp: "laptop",
    html: { extra: sec(`<p style="max-inline-size: none">${PROSE} ${PROSE}</p>`) },
  },
  {
    expect: "target-size",
    vp: "iphone",
    html: {
      extra: sec(
        `<div class="cluster" style="--cluster-gap: 2px"><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="one"></button><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="two"></button></div>`,
      ),
    },
  },
  {
    expect: "target-size",
    vp: "iphone",
    why: "two small targets whose 24px circles meet",
    html: {
      extra: sec(
        `<div class="cluster" style="--cluster-gap: 6px"><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="one"></button><button style="all: unset; inline-size: 14px; block-size: 14px; background: var(--accent)" aria-label="two"></button></div>`,
      ),
    },
  },
  {
    expect: "input-zoom",
    vp: "iphone",
    html: { extra: sec(`<label>Name <input style="font-size: 14px"></label>`) },
  },
  {
    expect: "orphan-row",
    vp: "laptop",
    html: {
      extra: sec(
        `<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem"><div>1</div><div>2</div><div>3</div><div>4</div></div>`,
      ),
    },
  },
  {
    expect: "orphan-row",
    vp: "laptop",
    why: "layout.css's count-aware .cards must not be defeated by a hard-coded column count",
    html: {
      head: `<style>@layer overrides { .cards { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; } .cards > * { grid-column: auto !important; } }</style>`,
    },
    cards: 4,
  },
  {
    expect: "grid-span",
    vp: "laptop",
    why: "a count-aware grid that is its own container",
    html: {
      extra: `<section data-block="m" data-tone="canvas"><div class="cards"><article class="card">1</article><article class="card">2</article><article class="card">3</article></div></section>`,
    },
  },
  {
    expect: "nav-wrap",
    vp: "laptop",
    html: {
      extra: sec(
        `<nav class="site-nav" aria-label="Extra" style="inline-size: 12rem"><ul role="list"><li><a href="/">Breakfast</a></li><li><a href="/">Lunch</a></li><li><a href="/">Catering</a></li><li><a href="/">Gift cards</a></li></ul></nav>`,
      ),
    },
  },
  {
    expect: "image-distorted",
    vp: "laptop",
    html: {
      extra: sec(
        `<img src="/story.png" width="1200" height="900" style="inline-size: 600px; block-size: 200px" alt="Squashed">`,
      ),
    },
  },
  {
    expect: "image-upscaled",
    vp: "iphone",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 1"><img src="/small.png" width="64" height="64" alt="A tiny source drawn large"></div>`,
      ),
    },
  },
  {
    expect: "image-oversized",
    vp: "laptop",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 1; inline-size: 150px"><img src="/landscape.png" width="2560" height="1440" alt="A huge file in a thumbnail"></div>`,
      ),
    },
  },
  {
    expect: "image-gap",
    vp: "iphone",
    why: "a picture in a photo band that does not fill it",
    html: {
      head: `<style>@layer overrides { [data-tone="media"] > [data-slot="backdrop"] > picture > img { block-size: auto !important; } }</style>`,
    },
  },
  {
    expect: "image-no-size",
    vp: "laptop",
    html: { extra: sec(`<img src="/small.png" alt="No dimensions">`) },
  },
  {
    expect: "frame-ratio",
    vp: "laptop",
    why: "a photo frame stretched beside a taller column",
    html: {
      head: `<style>@layer overrides { .switcher > .frame { align-self: stretch !important; } }</style>`,
      extra: sec(
        `<div class="switcher" style="--switch-at: 44rem"><div class="frame" style="--ratio: 4 / 3"><img src="/story.png" width="1200" height="900" alt="The counter"></div><div class="prose stack"><p>${PROSE}</p><p>${PROSE}</p><p>${PROSE}</p><p>${PROSE}</p></div></div>`,
      ),
    },
  },
  {
    expect: "image-broken",
    vp: "laptop",
    html: {
      extra: sec(
        `<div class="frame"><img src="/missing.png" width="800" height="600" alt="A photo that never arrives"></div>`,
      ),
    },
  },
  {
    expect: "img-alt",
    vp: "laptop",
    html: {
      extra: sec(`<div class="frame"><img src="/story.png" width="1200" height="900"></div>`),
    },
  },
  {
    expect: "text-contrast",
    vp: "laptop",
    html: { extra: sec(`<p style="color: #b5b5b5">Light grey on the near-white page.</p>`) },
  },
  {
    expect: "text-contrast",
    vp: "laptop",
    why: "a card on an inverse band painted white while its text stays light",
    html: {
      head: `<style>@layer overrides { [data-tone="inverse"] .card { background: #ffffff; } }</style>`,
      extra: sec(
        `<article class="card stack"><h3>On a dark band</h3><p class="muted">Muted text in a card.</p></article>`,
        "inverse",
      ),
    },
  },
  {
    expect: "focus-hidden",
    vp: "laptop",
    html: {
      extra: sec(
        `<p><a href="/menu/" style="outline: none !important">A link with no focus ring</a></p>`,
      ),
    },
  },
  {
    expect: "focus-clipped",
    vp: "laptop",
    html: {
      extra: sec(
        `<div style="overflow: hidden"><a class="button" href="/menu/">A focus ring its box cuts off</a></div>`,
      ),
    },
  },
  {
    expect: "anchor-obscured",
    vp: "laptop",
    html: {
      head: `<style>@layer overrides { .site-header { position: sticky; inset-block-start: 0; z-index: 5; background: var(--canvas); } }</style>`,
      // Room below the target, so the browser can scroll it to the top of the
      // viewport: a target near the page's end can never sit under the bar.
      extra:
        sec(`<p><a href="#target">Jump</a></p>`) +
        `<section id="target" data-block="m" data-tone="surface"><div><p>${PROSE}</p></div></section>` +
        sec(`<div style="block-size: 120vh"></div>`),
    },
  },
  {
    expect: "covered",
    vp: "laptop",
    html: {
      top: `<div style="position: fixed; inset-inline: 0; inset-block-end: 0; block-size: 6rem; background: var(--surface); z-index: 9"></div>`,
    },
  },
  {
    expect: "layout-shift",
    vp: "laptop",
    html: {
      extra: `<script>setTimeout(() => { const d = document.createElement('div'); d.style.blockSize = '300px'; document.querySelector('main').prepend(d); }, 200)</script>`,
    },
  },
  {
    expect: "font-failed",
    vp: "laptop",
    html: {
      head: `<style>@font-face { font-family: "Missing Serif"; src: url("/missing.woff2") format("woff2"); } h1 { font-family: "Missing Serif", serif; }</style>`,
    },
  },
  {
    expect: "chrome-share",
    vp: "iphone-land",
    html: {
      top: `<div style="position: fixed; inset-block-start: 0; inset-inline: 0; block-size: 45vh; background: var(--surface); z-index: 9"></div>`,
    },
  },
  {
    expect: "word-broken",
    vp: "laptop",
    why: "a figure in a box too narrow for it",
    html: { extra: sec(`<p style="inline-size: 3ch; font-size: 2.5rem">$125,000</p>`) },
  },
  {
    expect: "nav-wrap",
    vp: "iphone",
    why: "a header whose nav wraps under the brand",
    html: { head: `<style>.site-header .brand { min-inline-size: 100%; }</style>` },
  },
  {
    expect: "field-contrast",
    vp: "laptop",
    why: "a field edge at 1.2:1",
    html: { head: `<style>#em { border-color: #e2e2e6; background: transparent; }</style>` },
  },
  {
    expect: "focus-contrast",
    vp: "laptop",
    why: "a focus ring at 1.1:1",
    html: { head: `<style>:root { --focus: #eeeeee; }</style>` },
  },
  {
    expect: "text-overflow",
    vp: "iphone",
    why: "an FAQ answer that overflows only when it is opened",
    details: true,
    html: {
      extra: sec(
        `<details><summary>Can I book for twelve?</summary><p style="white-space: nowrap; max-inline-size: none">${"An answer that never wraps at all. ".repeat(3)}</p></details>`,
      ),
    },
  },
];

// Shapes that LOOK like a defect and are not: each must produce none of the ids
// it names. A probe that fires on correct pages gets switched off.
const CLEAN = [
  {
    forbid: ["overflow"],
    vp: "iphone",
    why: "a skip link parked at left: -9999px",
    html: { top: `<a href="#main" style="position: absolute; left: -9999px">Skip to content</a>` },
  },
  {
    forbid: ["image-upscaled", "image-oversized"],
    vp: "iphone",
    why: "a correct srcset at DPR 3 (the browser's 1200w pick for a 354px box)",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 4 / 3; inline-size: 354px"><img src="/story.png" srcset="/s400.png 400w, /story.png 1200w" sizes="354px" width="1200" height="900" alt="Sharp"></div>`,
      ),
    },
  },
  {
    forbid: ["orphan-row"],
    vp: "laptop",
    why: "a two-column form whose button sits alone on the last row",
    html: {
      extra: sec(
        `<form style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem" action="#main"><div class="field"><label for="a1">One</label><input id="a1"></div><div class="field"><label for="a2">Two</label><input id="a2"></div><div class="field"><label for="a3">Three</label><input id="a3"></div><div class="field"><label for="a4">Four</label><input id="a4"></div><div><button class="button" type="submit">Send</button></div></form>`,
      ),
    },
  },
  {
    forbid: ["orphan-row"],
    vp: "ipad",
    why: "an open-ended .auto-grid marked data-ragged",
    html: {
      extra: sec(
        `<div class="auto-grid" data-ragged><div class="card">1</div><div class="card">2</div><div class="card">3</div></div>`,
      ),
    },
  },
  {
    forbid: ["grid-span", "text-overflow", "measure"],
    vp: "laptop",
    why: "cards inside half a switcher answer to the half, not the slot",
    html: {
      extra: sec(
        `<div class="switcher" style="--switch-at: 44rem"><div><div class="cards" id="half"><article class="card stack"><h3>One</h3><p class="muted">Short.</p></article><article class="card stack"><h3>Two</h3><p class="muted">Short.</p></article><article class="card stack"><h3>Three</h3><p class="muted">Short.</p></article></div></div><div><p>Beside the cards.</p></div></div>`,
      ),
    },
    assert: () =>
      document.querySelector("#half > :first-child").getBoundingClientRect().width > 400,
  },
  {
    forbid: ["focus-clipped", "focus-hidden", "image-gap"],
    vp: "laptop",
    why: "a linked photo in a frame: the link fills it and the ring is drawn on the frame",
    html: {
      extra: sec(
        `<div class="frame" style="--ratio: 4 / 3; inline-size: 20rem"><a href="/menu/"><img src="/story.png" width="1200" height="900" alt="See the menu"></a></div>`,
      ),
    },
    assert: () => {
      const a = document.querySelector('.frame > a[href="/menu/"]');
      return a.getBoundingClientRect().height >= a.parentElement.getBoundingClientRect().height - 1;
    },
  },
];

const KIT_DIR = dirname(LAYOUT_CSS);
const RENDER = join(HERE, "block_site_render.py");
const CHECK = join(HERE, "block_site_check.py");

async function selfTest(chromium, launch) {
  const dir = mkdtempSync(join(tmpdir(), "device-matrix-selftest-"));
  const src = mkdtempSync(join(tmpdir(), "device-matrix-stress-"));
  let failed = 0;
  const row = (ok, label, detail = "") => {
    if (!ok) failed++;
    console.log(`  ${ok ? "ok  " : "FAIL"} ${label}${detail ? ` — ${detail}` : ""}`);
  };
  // 1. The kit's own output: its example site and its stress fixtures, rendered
  //    by the reference renderer, are the control. Planted defects go on
  //    synthetic pages beside them.
  const py = (args) => execFileSync("python3", args, { encoding: "utf8" });
  py([
    RENDER,
    "render",
    join(KIT_DIR, "example.manifest.json"),
    "--catalog",
    join(KIT_DIR, "catalog.json"),
    "--out",
    dir,
    "--placeholders",
  ]);
  py([CHECK, "fixtures", join(KIT_DIR, "catalog.json"), "--out", join(src, "stress.json")]);
  py([
    RENDER,
    "render",
    join(src, "stress.json"),
    "--catalog",
    join(KIT_DIR, "catalog.json"),
    "--out",
    dir,
  ]);
  const example = JSON.parse(
    readFileSync(join(KIT_DIR, "example.manifest.json"), "utf8"),
  ).pages.map((p) => p.path);
  const stress = JSON.parse(readFileSync(join(src, "stress.json"), "utf8")).pages.map(
    (p) => p.path,
  );
  writeFileSync(join(dir, "landscape.png"), png(2560, 1440, [92, 70, 52]));
  writeFileSync(join(dir, "portrait.png"), png(1200, 1800, [92, 70, 52]));
  writeFileSync(join(dir, "story.png"), png(1200, 900, [140, 120, 96]));
  writeFileSync(join(dir, "s400.png"), png(400, 300, [140, 120, 96]));
  writeFileSync(join(dir, "small.png"), png(64, 64, [40, 90, 160]));
  for (const n of [1, 2, 3, 4, 5, 6])
    writeFileSync(join(dir, `cards-${n}.html`), page({ cards: n }));
  MUTATIONS.forEach((m, i) =>
    writeFileSync(join(dir, `m${i}.html`), page({ ...m.html, cards: m.cards ?? 5 })),
  );
  CLEAN.forEach((m, i) => writeFileSync(join(dir, `c${i}.html`), page(m.html)));
  writeFileSync(
    join(dir, "graze.html"),
    page({
      extra:
        `<section data-block="m" data-tone="media" aria-label="Band"><div data-slot="backdrop"><img src="/story.png" width="1200" height="900" alt=""></div><div class="on-photo"><p>Copy on the photo band</p></div></section>` +
        `<section data-block="m" data-tone="canvas" style="padding-block-start: 0"><div><h2 style="margin-block-start: -4px; line-height: 1.6">Flat heading below the band</h2></div></section>`,
    }),
  );
  const { server, origin } = await serve(dir);
  try {
    const quick = VIEWPORTS.filter((v) => v.quick);
    const control = await runMatrix({
      chromium,
      launch,
      urls: example.map((p) => origin + p),
      viewports: quick,
      themes: Object.keys(THEMES),
      sweep: [320, 1600, 40],
    });
    const show = (fs) =>
      fs
        .slice(0, 3)
        .map((f) => `[${f.id}] ${new URL(f.url).pathname} ${f.where} ${f.msg} @ ${f.vp} ${f.theme}`)
        .join(" | ");
    row(
      control.findings.length === 0,
      `control: the kit's example site (${example.length} pages) clean at ${quick.length} viewports × ${Object.keys(THEMES).length} themes + a 320–1600px sweep (${control.states} states)`,
      show(control.findings),
    );
    row(
      control.photo.photoTexts > 0,
      `photo-contrast scored the example's hero copy (${control.photo.photoTexts} lines; lowest ${control.photo.minPhotoAt})`,
    );
    const stressRun = await runMatrix({
      chromium,
      launch,
      urls: stress.map((p) => origin + p),
      viewports: quick,
      themes: ["light"],
      sweep: null,
    });
    row(
      stressRun.findings.length === 0,
      `control: every catalog block at its min, max, longest word and RTL (${stress.length} stress pages) clean at ${quick.length} viewports, photo copy scored on a white photo (${stressRun.states} states)`,
      show(stressRun.findings),
    );
    // The count-aware .cards grid, measured: row pattern per item count at a
    // phone, a tablet (two-column range) and a laptop (six-track range).
    const WANT = {
      "reflow-320": {
        1: "1",
        2: "1+1",
        3: "1+1+1",
        4: "1+1+1+1",
        5: "1+1+1+1+1",
        6: "1+1+1+1+1+1",
      },
      ipad: { 1: "1", 2: "2", 3: "2+1", 4: "2+2", 5: "2+2+1", 6: "2+2+2" },
      laptop: { 1: "1", 2: "2", 3: "3", 4: "2+2", 5: "3+2", 6: "3+3" },
    };
    const browser = await chromium.launch(launch);
    try {
      for (const [vpId, byCount] of Object.entries(WANT)) {
        const v = VIEWPORTS.find((x) => x.id === vpId);
        const ctx = await browser.newContext({
          viewport: { width: v.w, height: v.h },
          deviceScaleFactor: v.dpr,
          isMobile: v.mobile,
        });
        const pg = await ctx.newPage();
        for (const [n, want] of Object.entries(byCount)) {
          await load(pg, `${origin}/cards-${n}.html`);
          const got = await pg.evaluate(() => {
            const rows = new Map();
            for (const k of document.querySelector(".cards").children) {
              const t = Math.round(k.getBoundingClientRect().top);
              rows.set(t, (rows.get(t) || 0) + 1);
            }
            return [...rows.entries()]
              .sort((a, b) => a[0] - b[0])
              .map(([, c]) => c)
              .join("+");
          });
          row(
            got === want,
            `count-aware .cards: ${n} item(s) @ ${vpId} lay out ${want}`,
            got === want ? "" : `got ${got}`,
          );
        }
        await ctx.close();
      }
      // Themes the tokens promise: "more contrast" must change the dark theme too.
      for (const [theme, same] of [
        ["dark", false],
        ["contrast-dark", true],
        ["contrast", true],
      ]) {
        const ctx = await newStateContext(browser, quick[0], theme);
        const pg = await ctx.newPage();
        await load(pg, `${origin}/`);
        await pg.evaluate(SETTLE);
        const [muted, ink] = await pg.evaluate(() => [
          getComputedStyle(document.querySelector(".card .muted")).color,
          getComputedStyle(document.querySelector(".card h3")).color,
        ]);
        row(
          (muted === ink) === same,
          `${theme}: muted text ${same ? "takes the full ink colour" : "stays muted"} (${muted} vs ${ink})`,
        );
        await ctx.close();
      }
      row(
        control.breakpoints.container.length > 0,
        "breakpoint reader finds the container-query thresholds in layout.css",
        control.breakpoints.container.join(","),
      );
      {
        const ctx = await newStateContext(browser, quick[1], "forced");
        const pg = await ctx.newPage();
        await load(pg, `${origin}/`);
        const [plate, canvas] = await pg.evaluate(() => {
          const probe = document.createElement("div");
          probe.style.background = "Canvas";
          document.body.append(probe);
          const c = getComputedStyle(probe).backgroundColor;
          probe.remove();
          return [
            getComputedStyle(document.querySelector(".on-photo"), "::before").backgroundColor,
            c,
          ];
        });
        row(
          plate === canvas && !/rgba/.test(plate),
          `forced colours: the hero copy sits on an opaque Canvas backplate (${plate})`,
        );
        await ctx.close();
      }

      // 2. Each planted defect is reported, and each look-alike is not.
      const at = async (vpId, url) => {
        const v = VIEWPORTS.find((x) => x.id === vpId);
        const ctx = await newStateContext(browser, v, "light");
        const pg = await ctx.newPage();
        await load(pg, url);
        return { v, ctx, pg };
      };
      for (const [i, m] of MUTATIONS.entries()) {
        const { v, ctx, pg } = await at(m.vp, `${origin}/m${i}.html`);
        let { findings } = await probePage(pg, v.w);
        let hit = findings.some((f) => f.id === m.expect);
        // A defect inside a closed <details> must be invisible to the plain pass
        // and reported by the pass that opens it.
        if (m.details) {
          const opened = await detailsOpen(pg, v.w);
          hit = !hit && opened.some((f) => f.id === m.expect);
          findings = findings.concat(opened);
        }
        if (hit && m.expect === "layout-shift")
          hit =
            (await reloadShifts(browser, v, "light", `${origin}/m${i}.html`, SHIFT_LOADS - 1)) ===
            SHIFT_LOADS - 1;
        row(
          hit,
          `must fail: ${m.expect}${m.why ? ` (${m.why})` : ""} @ ${v.id}`,
          hit ? "" : `got ${findings.map((f) => f.id).join(", ") || "nothing"}`,
        );
        await ctx.close();
      }
      for (const [i, m] of CLEAN.entries()) {
        const { v, ctx, pg } = await at(m.vp, `${origin}/c${i}.html`);
        const { findings } = await probePage(pg, v.w);
        const bad = findings.filter((f) => m.forbid.includes(f.id));
        const held = m.assert ? await pg.evaluate(m.assert) : true;
        row(
          !bad.length && held,
          `must pass: ${m.why} @ ${v.id}`,
          bad.length
            ? bad.map((f) => `[${f.id}] ${f.msg}`).join(" | ")
            : held
              ? ""
              : "its layout assertion failed",
        );
        await ctx.close();
      }
      // photo-contrast: on the stress hero (copy over a near-white photo), both the
      // factory's mutation and a scrim too thin to hold must be reported.
      for (const [why, css] of [
        [
          "every text colour white at 15% opacity",
          `:root *, :root *::before { color: rgb(255 255 255 / 0.15) !important; }`,
        ],
        [
          "a scrim too thin over a white photo",
          `:root { --scrim-weak: 25% !important; --scrim-strong: 35% !important; }`,
        ],
      ]) {
        const { v, ctx, pg } = await at("iphone", `${origin}/stress/hero-full/max/`);
        await pg.addStyleTag({ content: css });
        const st = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
        const f = await photoContrast(pg, v, st);
        row(
          f.some((x) => x.id === "photo-contrast"),
          `must fail: photo-contrast (${why}) @ ${v.id}`,
          `${st.photoTexts} lines scored, lowest ${st.minPhotoAt}`,
        );
        await ctx.close();
      }
      {
        // A heading on the flat page whose line box grazes the photo band above
        // it by a few px: its glyphs sit on the flat colour, so it is not scored
        // as photo copy (only the part of a line over the photo counts, and only
        // when that part is a third of the line or more).
        const { v, ctx, pg } = await at("laptop", `${origin}/graze.html`);
        const st = { photoTexts: 0, photoUnscored: 0, minPhoto: Infinity, minPhotoAt: "" };
        const f = await photoContrast(pg, v, st);
        const bad = f.filter((x) => /Flat heading/.test(x.msg + x.where));
        row(
          !bad.length && st.photoTexts > 0,
          `must pass: a flat heading whose line box grazes a photo band is not photo copy @ ${v.id}`,
          bad.map((x) => x.msg).join(" | ") || (st.photoTexts ? "" : "nothing was scored"),
        );
        await ctx.close();
      }
    } finally {
      await browser.close();
    }
    // 3. The harness itself never passes a run that tested nothing.
    row(
      (await main(["--url", `${origin}/`, "--pages", "/no-such-page/"])) === 2,
      "harness: a --pages path that answers 404 stops the run (exit 2), with --url too",
    );
    row(
      (await main(["--dir", dir, "--themes", "drak"])) === 2,
      "harness: an unknown theme is refused (exit 2), not silently dropped",
    );
    row(
      (await main(["--dir", dir, "--sweep", "1600:320:8"])) === 2,
      "harness: a sweep that runs backwards (no states) is refused (exit 2)",
    );
  } finally {
    server.close();
    rmSync(dir, { recursive: true, force: true });
    rmSync(src, { recursive: true, force: true });
  }
  console.log(`device-matrix --self-test: ${failed ? `FAILED (${failed} row(s))` : "OK"}`);
  return failed ? 1 : 0;
}

// ─── cli ─────────────────────────────────────────────────────────────────────
async function main(argv) {
  const args = { urls: [], pages: null, manifests: [], themes: Object.keys(THEMES) };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === "--self-test") args.selfTest = true;
    else if (a === "--dir") args.dir = next();
    else if (a === "--url") args.urls.push(next());
    else if (a === "--pages")
      args.pages = next()
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    else if (a === "--manifest") args.manifests.push(next());
    else if (a === "--full") args.full = true;
    else if (a === "--quick") args.full = false;
    else if (a === "--sweep") args.sweep = next().split(":").map(Number);
    else if (a === "--themes")
      args.themes = next()
        .split(",")
        .map((s) => s.trim());
    else if (a === "--no-photo") args.noPhoto = true;
    else if (a === "--shots") args.shots = resolve(next());
    else if (a === "--json") args.json = resolve(next());
    else if (a === "--chrome") args.chrome = next();
    else {
      console.error(`device-matrix: unknown argument ${a}`);
      return 2;
    }
  }
  const unknown = args.themes.filter((t) => !THEMES[t]);
  if (unknown.length || !args.themes.length) {
    console.error(
      `device-matrix: unknown theme(s) ${unknown.join(", ") || "(none given)"}; choose from ${Object.keys(THEMES).join(", ")}`,
    );
    return 2;
  }
  if (
    args.sweep &&
    (args.sweep.length !== 3 ||
      args.sweep.some((n) => !Number.isFinite(n) || n <= 0) ||
      args.sweep[0] > args.sweep[1])
  ) {
    console.error("device-matrix: --sweep FROM:TO:STEP with FROM <= TO, e.g. 320:1600:8");
    return 2;
  }
  for (const m of args.manifests) {
    if (!existsSync(m)) {
      console.error(`device-matrix: no such manifest ${m}`);
      return 2;
    }
    const fromManifest = JSON.parse(readFileSync(m, "utf8")).pages.map((p) => p.path);
    args.pages = [...(args.pages || []), ...fromManifest];
  }
  const pages = args.pages || ["/"];
  const pw = loadPlaywright();
  if (!pw) {
    console.error(
      "device-matrix: could not load Playwright from this directory. Install it (npm i -D playwright && npx playwright install chromium). THIS IS NOT A PASS.",
    );
    return 2;
  }
  const exe = args.chrome || process.env.CHROME_BIN;
  // Real scrollbars: a desktop browser draws a classic 15px one, and with
  // scrollbar-gutter: stable a page laid out without it measures a width no
  // reader's browser has. Mobile emulation keeps overlay scrollbars, as phones do.
  const launch = {
    ignoreDefaultArgs: ["--hide-scrollbars"],
    ...(exe ? { executablePath: exe } : {}),
  };
  if (args.selfTest) return selfTest(pw.chromium, launch);
  let server;
  const urls = [];
  if (args.dir) {
    if (!existsSync(args.dir)) {
      console.error(`device-matrix: no such directory ${args.dir}`);
      return 2;
    }
    const s = await serve(args.dir);
    server = s.server;
    urls.push(...pages.map((p) => s.origin + (p.startsWith("/") ? p : `/${p}`)));
  }
  for (const base of args.urls) {
    if (args.pages) urls.push(...pages.map((p) => new URL(p, base).href));
    else urls.push(base);
  }
  if (!urls.length) {
    console.error("device-matrix: give --dir DIST or --url URL (see the header)");
    return 2;
  }
  try {
    const result = await runMatrix({
      chromium: pw.chromium,
      launch,
      urls,
      viewports: args.full ? VIEWPORTS : VIEWPORTS.filter((v) => v.quick),
      themes: args.themes,
      sweep: args.sweep,
      shots: args.shots,
      photo: !args.noPhoto,
    });
    if (args.json) writeFileSync(args.json, JSON.stringify(result, null, 2));
    return report(result);
  } catch (e) {
    console.error(`device-matrix: could not run: ${e && e.message}`);
    return 2;
  } finally {
    if (server) server.close();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  main(process.argv.slice(2)).then((code) => process.exit(code));
